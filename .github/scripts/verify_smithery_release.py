"""Require the accepted Smithery release to succeed before CI reports success.

Distribution copies live in each active server's .github/scripts directory.
Run scripts/sync_smithery_release.py after editing this source.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from urllib.parse import quote

USER_AGENT = "AceDataCloud-Smithery-Release-Check/1.0"
PENDING_STATUSES = {"PENDING", "QUEUED", "WORKING"}
TERMINAL_STATUSES = {
    "SUCCESS",
    "FAILURE",
    "FAILURE_SCAN",
    "AUTH_REQUIRED",
    "AUTH_TIMEOUT",
    "CANCELLED",
    "INTERNAL_ERROR",
}


class ReleaseStatusError(RuntimeError):
    """A sanitized, known release state that must never pass CI."""


class ReleasePendingTimeout(TimeoutError):
    """The accepted release stayed pending until the verification deadline."""


def read_release(url, key, timeout):
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def safe_failure_reason(error):
    """Keep HTTP/scan failures distinguishable without echoing upstream secrets."""
    if isinstance(error, ReleaseStatusError):
        return str(error)
    if isinstance(error, ReleasePendingTimeout):
        return "Release still pending after verification deadline; inspect before publishing again"
    if isinstance(error, urllib.error.HTTPError):
        return f"Release API returned HTTP {error.code}"
    if isinstance(error, (urllib.error.URLError, TimeoutError)):
        return "Release API network/TLS/timeout failure"
    if isinstance(error, (ValueError, TypeError, AttributeError)):
        return "Release API response or release identity is invalid"
    return "Release verification failed unexpectedly"


def accepted_release(log, qualified_name):
    """Read the CLI's non-TTY receipt, rather than checking an older latest release."""
    for line in reversed(log.splitlines()):
        try:
            receipt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(receipt, dict) or "deploymentId" not in receipt:
            continue
        if receipt.get("qualifiedName") != qualified_name:
            raise ValueError("Smithery receipt belongs to a different server")
        release_id = receipt["deploymentId"]
        uuid.UUID(release_id)
        return release_id
    raise ValueError("Smithery CLI did not return an accepted release ID")


def wait_for_release(
    release_id,
    fetch,
    *,
    timeout=300,
    interval=5,
    clock=time.monotonic,
    sleep=time.sleep,
):
    deadline = clock() + timeout
    previous_status = None
    while clock() < deadline:
        release = fetch(min(15, deadline - clock()))
        if release.get("id") != release_id:
            raise ValueError("Smithery returned a different release ID")
        raw_status = release.get("status")
        status = (
            raw_status
            if isinstance(raw_status, str) and raw_status in PENDING_STATUSES | TERMINAL_STATUSES
            else "UNKNOWN"
        )
        if status != previous_status:
            print(f"Smithery release {release_id}: {status}", flush=True)
            previous_status = status
        if status == "SUCCESS":
            return release
        if status not in PENDING_STATUSES:
            raise ReleaseStatusError(f"Smithery release did not succeed: {status}")
        sleep(max(0, min(interval, deadline - clock())))
    raise ReleasePendingTimeout("Release still pending; inspect it before publishing again")


def main():
    qualified_name, log_path = sys.argv[1:]
    key = os.environ.get("SMITHERY_API_KEY")
    if not key:
        raise ValueError("SMITHERY_API_KEY is required to verify the accepted release")
    release_id = accepted_release(Path(log_path).read_text(), qualified_name)
    url = f"https://api.smithery.ai/servers/{quote(qualified_name, safe='/')}/releases/{release_id}"

    def fetch(timeout):
        return read_release(url, key, timeout)

    try:
        wait_for_release(release_id, fetch)
    except Exception as error:
        # Do not print response bodies or upstream logs: they may contain secrets.
        raise RuntimeError(
            f"{safe_failure_reason(error)}. Inspect https://smithery.ai/servers/"
            f"{qualified_name}/releases (release {release_id})"
        ) from None


if __name__ == "__main__":
    main()
