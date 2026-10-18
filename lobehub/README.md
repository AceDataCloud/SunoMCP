# Suno by Ace Data Cloud for LobeHub

[简体中文](README_zh-CN.md) · [Install in the official MCP market](https://lobehub.com/mcp/acedatacloud-mcpsuno) · [Current API/pricing](https://platform.acedata.cloud/documents/suno-audios?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_lobehub_readme_pricing)

Music generation, lyrics and audio editing, provided by **Ace Data Cloud**. This is an Ace integration, not an official plugin from the model vendor. It reuses [SunoMCP](https://github.com/AceDataCloud/SunoMCP) and the existing `mcp-suno` server; no duplicate generation backend or new publisher identity is created.

> Publication status (2026-10-18): this directory is reviewable source material for the existing LobeHub listing `acedatacloud-mcpsuno`. The public card is still Unvalidated and its declared version may be old. These files do not mean the owner update has been published or a normal LobeHub installation has passed. The declaration below comes from published package `2026.10.12.1`; confirm authenticated hosted schema/version parity before updating the hosted listing.

## 1. Install the service

![Official LobeHub MCP marketplace screenshot; historical documentation reference](https://lobehub.com/img/hub/blog/assetsb811f2aae8e8346aef16793d6bd10f88.webp)

This is an unchanged [official documentation image](https://github.com/lobehub/lobehub/blob/43578a9bcc37dbf0ec9beb5f5ab1dcd5ba09daf7/docs/usage/community/mcp-market.mdx), present in the 2026-03-03 documentation commit; its capture date/version is unknown. It illustrates the real search field and service cards, not an Ace install or current card ranking. Reference checked 2026-10-18.

Open the [official Suno card](https://lobehub.com/mcp/acedatacloud-mcpsuno), review source and installation details, then select Install. Search terms are `Suno`, `Suno`, and `Ace Data Cloud`; exact ranking is not promised. If there are multiple historical cards, use the identifier above rather than creating another one.

If the card's automatic configuration is incomplete, add this single HTTP connector in **Settings → Connectors**, then configure authentication separately:

```json
{
  "mcpServers": {
    "ace-suno": {
      "type": "http",
      "url": "https://suno.mcp.acedata.cloud/mcp"
    }
  }
}
```

LobeHub stable v2.2.19 quick import reads only the first entry and drops HTTP `headers`/`auth`; import this service alone. An imported URL is not authentication. Desktop users can instead use [install-stdio.json](install-stdio.json) with uvx and the pinned public package. STDIO commands are not supported as local browser processes.

## 2. Register/sign in and obtain your API Token

1. Sign in or register at [Ace → Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_lobehub_readme_api_key).
2. Initialize **General application** if absent, then open it. Check **Suno** service entitlement, current balance and pricing. A service-specific key can be restricted to that service.
3. Copy the existing service API Token, or open **Manage Keys** and create a dedicated LobeHub key. Do not use a platform management token or a model vendor's key.

![Copy an API Token in Ace Applications; real historical screenshot, referenced 2026-10-18](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/get-api-key-en.png)

![Create a dedicated key; credentials hidden; historical screenshot](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/create-api-key-en.png)

These images are real Ace Applications screenshots from the linked source commit, not evidence that this LobeHub card installed or ran. Their original capture date is not asserted.

## 3. Paste the Token in LobeHub

Choose **Bearer** in this connector's authentication settings and paste only the token string, without `Bearer `, quotes or masked characters. Alternatively enter an explicit `Authorization: Bearer YOUR_API_TOKEN` header. Save/test the connection, then enable it in **Agent Settings → Connectors**. Keep write/generation tools on Ask or Deny until you intend to use them. Never paste tokens into chat or screenshots.

[Official LobeHub MCP setup and permission guide](https://lobehub.com/docs/usage/community/mcp-market) documents the real entry points. A screenshot of the actual Suno connector/authorization flow is queued for coordinated capture; this source does not fabricate a screenshot of a successful installation.

## 4. First use and task completion

Call `suno_list_models` with no arguments. It returns built-in information and makes no generation request. Starting a chat to ask an Agent to run it may still charge the chat model; use a direct tool-test surface if available.

For generation, explicitly select a model supported by the installed schema, confirm current pricing and permissions, and submit once. Save the returned task ID and query `suno_get_task` with that **same ID** until the response explicitly reports terminal success or failure. Pending/preview media is not final success. Open the final result URL only after terminal success; keep task and usage records to verify one charge. No paid generation was run to author this directory.

## Troubleshooting

- **401/403:** recopy a service token and check entitlement, expiry and balance. `ACEDATACLOUD_API_TOKEN` is the STDIO variable; old `ACEDATA_API_TOKEN` examples are obsolete.
- **Imported but unauthorized:** quick import did not preserve the HTTP auth header. Fill Bearer in the connector UI before checking it.
- **Connected but no tools in chat:** enable this connector for the current Agent, check Allow/Ask/Deny and the chat model's tool support.
- **Pending:** query the existing task; do not submit a second generation just because it takes time.
- **429/500:** preserve the returned error meaning; do not silently switch model or price tier.

## Existing-listing update (publisher)

The owner declaration contains actual `tools/list` schemas from the public package, not invented tool names. It is not a package release or live marketplace receipt. With an existing authorized publisher identity, inspect auth/GitHub state and `plugin list`, then claim the exact existing identifier if necessary and `plugin update --dir /absolute/path/to/this/directory`. Do not `plugin publish` a duplicate or automatically register an M2M identity. Human login/GitHub authorization and any new terms remain human steps. Read [official publisher rules](https://lobehub.com/publish-mcp/skill.md).

Attribution uses the current allowed `opensource/referral/evergreen` contract plus a service-specific `*_lobehub_*` content tag. A source label is not a proven referrer, install, registration or purchase. No global attribution rule changes are made.
