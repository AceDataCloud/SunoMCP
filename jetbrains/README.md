# Suno by Ace Data Cloud

Independent Suno music integration provided by Ace Data Cloud for JetBrains IDEs. Not an official Suno or JetBrains product.

[中文完整教程](README.zh-CN.md)

## Install from Marketplace

[Open the official installation entry](https://plugins.jetbrains.com/plugin/30782-suno-mcp), or search **Suno** in **Settings → Plugins → Marketplace** and check publisher **AceDataCloud**. Official Marketplace entry exists; new panel awaits an approved release.

The new native panel is under **Settings → Tools → Suno MCP → Suno**. It provides model discovery, an explicit model field, prompt submission, existing-task lookup and the raw service result. It does not require AI Assistant. Plugin installation is free; API operations use your Ace application's permissions and balance.

![Official JetBrains Marketplace installation screen](_assets/marketplace-official.png)

Source: [JetBrains installation documentation](https://www.jetbrains.com/help/idea/managing-plugins.html), official 2026.2 documentation image downloaded 2026-10-18. It shows another plugin, not an Ace installation or runtime result.

## Get an application API key

<!-- BEGIN TOKEN ONBOARDING -->
1. Open [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_api_key). Sign in, or register an account first.
2. Find **General application**. If it has not been created, choose **Initialize General Application**. A general key can use the services available to your account; a dedicated application's key is limited to its service. Check the required service/model access and [current pricing](https://platform.acedata.cloud/models?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_models).
3. Copy the **API Key** from the application card, or open **Keys / Manage Keys → Create** to create a separate key for this integration. Give it a recognizable name so you can revoke or rotate it independently.
4. When creating a key, review **Expiration Time**, **Set Usage Limitation**, and **Allowed APIs**. Enable only the restrictions you need, allow the operations you will call, then click **Create** and copy the token from the key list. Task lookup does not grant permission to submit a generation. Confirm the application's balance can cover your first request; any trial allowance is whatever your account currently displays.
5. Copy only the token value, without quotation marks, spaces, or `Bearer `. An API Key / API Token field expects this raw value; only a manually configured HTTP `Authorization` header needs the `Bearer ` prefix. A `platform-...` account-management token cannot replace a generation API key.

![Copy an application API key or open Manage Keys](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/2522b2f57210597af2db866445319334a1677a23/_assets/tutorial/get-api-key-en.png)

![Create a separately named key with optional restrictions](https://raw.githubusercontent.com/AceDataCloud/NanoBananaDify/2522b2f57210597af2db866445319334a1677a23/_assets/tutorial/create-api-key-en.png)

Save the key in the client's credential store or the environment variable shown below. Never put it in a prompt, shared workflow, screenshot, or Git commit. If authentication fails, check the full copied value, application/service access, expiration, usage limit, and balance before creating another key.
<!-- END TOKEN ONBOARDING -->

The new native panel keeps its key in memory and clears it when the settings page closes. Paste the raw key into **Application API Key** in the Suno tab. The older optional MCP helper stores its separate settings key locally; do not put credentials in shared project files.

## First use and existing task lookup

1. Click **List models**. Review [current pricing](https://platform.acedata.cloud/models?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_models), then enter the exact model ID you want. The plugin does not silently select a substitute.
2. Enter a prompt and click **Generate music**. Review the one-request charge confirmation. Cancel if the model, access or balance is unclear. No automatic generation or retry runs.
3. Copy the returned `task_id` to **Existing task ID** if it is not filled automatically. Click **Check existing task** on that same ID until the response reports a terminal state. Keep the result/URL and verify it opens before calling the job successful. A pending response or accepted request is not completed media.
4. If a submission times out, do not submit again blindly. Find the original task in your Ace account first to avoid duplicate charges. A failed/content-restricted/rate-limited result must remain distinct.

Read-only first-use tool: `suno_list_models`. Generation tool: `suno_generate_music`. Same-task query: `suno_get_task(task_id="EXISTING_TASK_ID")`. This guide contains no proof of a newly paid generation or revenue.

## Optional AI Assistant tools

If you use AI Assistant, the second tab can still copy the HTTP/STDIO configuration. Paste it into **Settings → Tools → AI Assistant → Model Context Protocol → HTTP**, then Apply and review the available tools. This optional route is separate from an LLM provider.

![Official AI Assistant HTTP MCP dialog](_assets/mcp-http-official.png)

Source: [JetBrains MCP documentation](https://www.jetbrains.com/help/ai-assistant/mcp.html), official 2026.2 image downloaded 2026-10-18. Empty official dialog, not a screenshot of Ace connected. No fabricated screenshot of the new panel is included; real panel screenshots remain a release acceptance item.

```json
{"mcpServers": {"suno": {"url": "https://suno.mcp.acedata.cloud/mcp", "headers": {"Authorization": "Bearer YOUR_API_KEY"}}}}
```

## Troubleshooting

- **401:** check raw copied key, expiration and Allowed APIs. A `platform-` management token cannot replace an application API key.
- **403:** check service access or content restrictions. Do not change to another model without choosing and pricing it explicitly.
- **429:** wait before a later manual attempt; the plugin does not retry generation.
- **Pending task:** query the same ID. Never treat HTTP 200 or an accepted task as completed media.
- **Plugin missing from search:** only approved public versions can be installed normally. Source, local ZIPs and uploaded review candidates are separate stages.
- **Want an Ace model in AI Assistant's provider dropdown?** This is a service plugin, not a default LLM preset. JetBrains currently documents a separate [third-party model setup](https://www.jetbrains.com/help/ai-assistant/use-custom-models.html).

## 中文上手

请参阅[中文完整教程](README.zh-CN.md)：包含注册、专用 Key 图文步骤、本平台填写位置、首用与同 ID 查询、结果和排错。新原生面板仍待正式发版与真实界面验收；下方官方参考图不代表 Ace 已连接。

## Source and support

[Source repository](https://github.com/AceDataCloud/SunoMCP) · [Service documentation](https://platform.acedata.cloud/documents/suno-mcp?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_quick_start) · [Current pricing](https://platform.acedata.cloud/models?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_models). Source of truth: [AceDataCloud/MCPs](https://github.com/AceDataCloud/MCPs). Existing MCP server and billing are reused. MIT.
