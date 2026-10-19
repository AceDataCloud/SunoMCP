# Suno by Ace Data Cloud for Cline

Use Suno music tools inside Cline through the existing Ace Data Cloud MCP server. This is an Ace Data Cloud integration, not an official Suno or Cline first-party plugin.

English guide · [中文步骤](#中文步骤) · [API access and current pricing](https://platform.acedata.cloud/documents/suno-mcp?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_pricing)

## 1. Install from the Cline directory

Open Cline's **Marketplace**, search **Suno**, and select **Suno by Ace Data Cloud**. Check the author is **Ace Data Cloud** and the repository is [AceDataCloud/SunoMCP](https://github.com/AceDataCloud/SunoMCP).

**Submission status (2026-10-18): this directory entry is being proposed; it is not yet an approved/public listing.** If the card is unavailable, use this manual equivalent while review is pending:

```bash
cline mcp add suno-acedatacloud https://suno.mcp.acedata.cloud/mcp --transport http --yes
```

This installs one named server, not all Ace services. It does not create an account, supply a key or run a generation. Cline's native MCP marketplace is used; no separate code package is copied. [Official MCP configuration](https://docs.cline.bot/mcp/mcp-overview) · [Official directory](https://github.com/cline/marketplace).

## 2. Register or sign in and obtain your API Token

1. Open [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_api_key). Register/sign in if needed.
2. Open **General application**; if none exists, choose **Initialize General Application**. A general key can access services enabled for your account; a service-specific key is limited to that service. Confirm **Suno** access, current pricing and a sufficient account balance.
3. Copy the API Key on the application card, or open **Manage Keys → Create** to make a dedicated key named `Cline Suno`.

![Copy a key or open Manage Keys](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/get-api-key-en.png)

4. Review **Expiration Time**, **Set Usage Limitation**, and **Allowed APIs**. Restrict only as needed and allow both /suno/audios and /suno/tasks. Create the key, return to the list, and copy the complete value.

![Create a dedicated API key with optional restrictions](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/create-api-key-en.png)

These are existing redacted Ace console screenshots from the pinned Dify guide (collected 2026-10-18), reused only for the same Ace key controls; the Dify installation steps do not apply to Cline. No live secret is displayed. Copy the token string only: no quotes, spaces or `Bearer `. A `platform-...` account-management token is not this service API key. Any trial balance is what your account currently shows, not a promised allowance.

## 3. Paste the Token in Cline's MCP settings

In the Cline panel, open **MCP Servers → Configure → Configure MCP Servers**. Merge the following named server into that user-level JSON file and preserve your other servers:

```json
{
  "mcpServers": {
    "suno-acedatacloud": {
      "type": "streamableHttp",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Replace **only** `YOUR_API_TOKEN` with your copied token. The `Authorization` header requires `Bearer ` once. The file contains a secret: keep it private and out of Git and screenshots. Cline CLI uses `~/.cline/data/settings/cline_mcp_settings.json` by default; `CLINE_MCP_SETTINGS_PATH` can override it. Project `.cline/` rules are not a project MCP settings file. Save, reconnect the server and confirm tools appear.

If you prefer browser authorization, remove the entire fixed `headers` property, then use **Authorize OAuth** in the `cline mcp` wizard. The hosted server publishes OAuth metadata, but a successful account consent flow must still be verified for your Cline version. Do not combine a fixed Bearer header with OAuth for the same server. Authentication does not waive API charges.

![Official Cline settings reference](https://raw.githubusercontent.com/cline/cline/b549ceb4bb4247284c975f6d6ca0979decec097c/docs/assets/free-models/free-models-vscode-cline-provider.png)

**Official original reference, not an Ace run.** This Cline document screenshot shows the original Cline Usage-Billing provider and its own model list; it was collected 2026-10-17 and its capture date/version are unspecified (Nightly). It identifies the native Cline panel only, not an Ace selection, MCP settings screenshot or successful connection. Click the panel's **MCP Servers** control for the tool configuration above; do not put `https://suno.mcp.acedata.cloud/mcp` into the model Provider Base URL.

Model setup is separate: use a model provider already configured in Cline. Ace chat models use **OpenAI Compatible**, Base URL `https://api.acedata.cloud/v1`, your own Key and a model that supports Chat Completions and tool calls. This MCP entry does not add a named Ace model provider.

## 4. First use and asynchronous results

For a no-generation installation check, ask Cline to use the static `suno_list_models` reference tool. Static reference results or a loaded schema prove tool loading only, not valid paid access or balance. In the IDE, leave MCP `autoApprove` empty and check global approval settings; CLI headless tasks may auto-approve, so use `cline --tui --auto-approve false` when you require interactive approval.

When **you decide to generate** after reviewing the [current service contract and prices](https://platform.acedata.cloud/documents/suno-mcp?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_first_use), ask Cline to call `suno_generate_music` for one request with a currently supported model and parameters. This can be charged. Keep the returned **task_id**, then call `suno_get_task` with **that same ID** until its task result is terminal. Do not repeat the generation merely because the task is pending. A completed chat turn or a playable preview is not task completion.

Read the returned task status, success/error and media fields according to the tool schema. On success, open the returned audio/video/image URL; do not invent a URL, reuse another account's task or treat an empty media field as success. Check [usage history](https://platform.acedata.cloud/console/usages?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_usage) for the original request and its charge; list/configuration commands are not billable-generation evidence. This guide contains no claimed Suno generation result or new paid test.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| No directory card | The proposal is pending; use the named manual MCP command, not an unrelated similarly named integration. |
| Tools missing | Check server URL, `streamableHttp`, saved file and reconnect. For a local `uvx` setup, allow a longer per-server timeout (for example 30s) on first startup. |
| 401 / 403 | Check raw Token, one Bearer prefix, application access, expiration, Allowed APIs, usage limit and balance. Remove a stale fixed header before OAuth. |
| 400 parameter error | Use the current tool model enum/schema; do not copy parameters from another service or old model. |
| Pending task | Query the same task ID. Do not regenerate or enable automatic paid retries. |
| 429 | Wait and reduce concurrency; inspect the service's limits. |
| Timeout / 5xx / failed task | Inspect original task and usage before considering a new submission; retain task/trace ID, never share the Token. |

## Privacy, cost and source

The MCP integration is free to install; the server receives your selected prompts/media and authorization and calls Ace Data Cloud. Service calls follow current account/service pricing. Keep credentials in Cline's private user configuration, not prompts, shared workflows or exports. Use only content you may process.

[Source](https://github.com/AceDataCloud/SunoMCP) · [Current models and prices](https://platform.acedata.cloud/models?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_models) · dev@acedata.cloud. Development/source PRs and local checks are separate from official directory acceptance, actual install, task completion, billing and attributed users.

## 中文步骤

这是 **Suno by Ace Data Cloud** 的 Cline 接入指南：服务能力由 Ace Data Cloud 提供，不是 Suno 或 Cline 第一方官方插件。

### 1. 查找并安装正确的条目

在 Cline **Marketplace** 搜索 **Suno**，核对标题 **Suno by Ace Data Cloud**、作者 **Ace Data Cloud**、[源仓 AceDataCloud/SunoMCP](https://github.com/AceDataCloud/SunoMCP)。

**2026-10-18 状态：官方目录投稿仍待审核，尚未收录。** 若搜索不到卡片，可在审核期间使用以下手动等效配置；不要把这条命令视为官方上架证明：

```bash
cline mcp add suno-acedatacloud https://suno.mcp.acedata.cloud/mcp --transport http --yes
```

此命令只添加这一个命名服务，不安装 Ace 全合集、不创建账号、不填 Token、不发送生成请求。参见 [Cline 官方 MCP 说明](https://docs.cline.bot/mcp/mcp-overview)。

### 2. 注册登录并获取专用 API Token

1. 打开 [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_api_key_zh)，新用户先注册并登录。
2. 进入 **General application**；尚未创建时先点 **Initialize General Application**。通用应用的 Key 能访问账号已开通服务；专用应用的 Key 受对应服务限制。确认 **Suno** 权限、[当前模型和价格](https://platform.acedata.cloud/models?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_pricing_zh)及余额，不假定有固定免费额度。
3. 点应用卡片的复制按钮取得现有 API Key，或 **Manage Keys → Create** 创建名为 `Cline Suno` 的独立 Key，方便撤销和轮换。

![复制已有 API Key 或打开 Manage Keys](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/get-api-key-en.png)

4. 检查 **Expiration Time**、**Set Usage Limitation** 和 **Allowed APIs**。只设置所需限制，同时允许本服务的生成和任务查询 API（/suno/audios and /suno/tasks）；创建后返回 Key 列表复制完整值。允许任务查询不代表允许提交生成。

![创建专用 Key 并按需设置有效期、额度和 API 限制](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/create-api-key-en.png)

两张图来自固定版本的脱敏 Ace 控制台截图，2026-10-18 复用于同一取 Key 流程；不是 Cline 内授权完成图，也不套用 Dify 安装步骤。复制原始 Token 字符串，不含引号、空格、`Bearer ` 或图片中的遮挡字符。`platform-...` 账号管理令牌不能替代这里的服务 API Key。

### 3. 在 Cline 填写 Token

在 Cline 面板点 **MCP Servers → Configure → Configure MCP Servers**，把以下服务合并到打开的**用户配置文件**，保留已有其他服务：

```json
{
  "mcpServers": {
    "suno-acedatacloud": {
      "type": "streamableHttp",
      "url": "https://suno.mcp.acedata.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

只把 `YOUR_API_TOKEN` 替换为刚复制的原始值；`Authorization` 中只加一次 `Bearer `。文件内有明文密钥，不要提交 Git、放进提示词/共享工作流或截图。CLI 默认使用 `~/.cline/data/settings/cline_mcp_settings.json`，设置 `CLINE_MCP_SETTINGS_PATH` 时使用指定文件；项目 `.cline/` 规则目录不是项目 MCP 设置入口。保存后重连，检查工具列表。

若改用浏览器 OAuth，先移除整个固定 `headers` 属性，再从 `cline mcp` 向导点 **Authorize OAuth**。此服务公开 OAuth 元数据，但仍需在你的 Cline 版本完成真实账号授权；不要给同一服务同时配置固定 Bearer header 与 OAuth。授权成功也不代表 API 调用免费。

![Cline 官方设置原图参考](https://raw.githubusercontent.com/cline/cline/b549ceb4bb4247284c975f6d6ca0979decec097c/docs/assets/free-models/free-models-vscode-cline-provider.png)

**官方原始参考图，非 Ace 实测。** 图中仍为 Cline Usage-Billing 与其自己的模型列表，采集日期 2026-10-17，原拍摄日期和精确版本不详（Nightly）；它只展示 Cline 面板，不是 MCP 授权界面或 Ace 成功连接截图。本服务工具应进入 **MCP Servers**，不要把 `https://suno.mcp.acedata.cloud/mcp` 填到模型 Provider。

模型需要独立配置：已有模型可继续使用；Ace 聊天接入用现有 **OpenAI Compatible**，Base URL `https://api.acedata.cloud/v1`，自己的 Key 和支持 Chat Completions/工具调用的模型 ID，不追加 `/chat/completions`。这个 MCP 条目不会新增命名 Ace 模型服务商。

### 4. 首用、同 ID 查询与结果

免费安装检查先调用只读的 `suno_list_models`，查看静态参考列表。静态列表或 schema 只证明工具加载，不证明有效密钥、余额或收费业务成功。IDE 保持 `autoApprove` 为空并检查全局自动批准；CLI 无界面任务可能自动批准，需要逐次确认时使用 `cline --tui --auto-approve false`。

真正生成前先查看 [本服务当前接口和计费](https://platform.acedata.cloud/documents/suno-mcp?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_first_use_zh) 并确认本次额度，然后让 Cline 调用 `suno_generate_music` 一次，参数/模型以当前工具 schema 为准。该动作可能收费。保存返回的 **task_id**，使用 `suno_get_task(task_id="<原 task_id>")` 持续查询同一个任务到终态；pending 时不要再次生成、不要打开自动付费重试。

按实际工具返回检查成功/失败状态、错误与媒体字段；成功后打开返回的真实音频/视频/图片链接。GPT Image 查询以 `finished_at` 判断已结束，再看 `response` 的成功或错误，不能只凭时间戳当成功；其他服务按自己的 schema 判断。聊天回合结束、绿色工具卡或可播放预览都不等于任务完成。媒体字段为空时不编造 URL、不拿别人的任务替代。

到 [使用历史](https://platform.acedata.cloud/console/usages?utm_source=cli&utm_medium=referral&utm_campaign=evergreen&utm_content=cline_suno_usage_zh) 核对原请求和扣费；查询/安装日志不能当真实生成或唯一账单证明。本指南未声称已在 Cline 生成 Suno 媒体或带来付费用户。

### 5. 常见问题与隐私

| 现象 | 处理 |
| --- | --- |
| 市场搜不到 | 当前投稿仍待审；使用上方手动命名服务配置，不安装同名但来源不符的集成。 |
| 无工具/连接超时 | 核 URL、`streamableHttp`、实际保存文件和重连；本地 `uvx` 首次启动可设单服务 timeout 如 30 秒。 |
| 401 / 403 | 核完整 Token、一个 Bearer 前缀、服务权限、有效期、Allowed APIs、额度上限与余额；切 OAuth 前移除旧固定 header。 |
| 400 参数错误 | 按当前 schema/模型枚举，别混用其他服务参数或过时示例。 |
| pending | 只查询同一个 task_id，不重复提交生成。 |
| 429 | 等待、降低并发，检查服务限额。 |
| 5xx / 失败 / 链接不可用 | 先查原任务、终态错误、使用历史及返回媒体地址；保留 task/trace ID，支持排查时不要发密钥。 |

安装本集成本身免费，服务 API 按当前账号/套餐计费；选定提示词、媒体和认证会交给托管服务并调用 Ace API。只提交有权处理的内容。密钥留在用户私有设置，正式目录收录、真实安装/授权、终态媒体、账单和增长分别验收。
