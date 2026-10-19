# 在 Kilo 中使用 Suno by Ace Data Cloud

[English](README.md)

通过自己的 Ace Data Cloud 账户在 Kilo 中使用 Suno。本集成由 **Ace Data Cloud** 提供和维护，不是 Suno 模型所属厂商的官方插件，也不代表厂商背书。

## 1. 找到并安装对应服务

打开 Kilo 的 **Marketplace**，选择 **MCP**，搜索 **Suno**。选择 **Suno by Ace Data Cloud**，确认作者为 **Ace Data Cloud**。本目录投稿仍在审核；如果搜索不到该卡片，说明条目尚未发布。不能把本地配置视为官方市场已经可用。

[官方目录投稿 #423](https://github.com/Kilo-Org/kilo-marketplace/pull/423) · [Kilo Marketplace 官方说明](https://kilo.ai/docs/customize/marketplace) · [服务源码](https://github.com/AceDataCloud/SunoMCP) · [已发布 Python 包](https://pypi.org/project/mcp-suno/)

选择 **Hosted (API token)** 可直接连接，无需安装 Python。也可以选择 **Local (UVX, pinned)**，使用固定版本 `mcp-suno==2026.10.12.1`；此方式需要 Python 3.10+ 和 `uvx`。两者使用相同类型的应用 API Token。优先选择 **Global**，避免密钥写入项目仓库；全局配置仍需保密，Global 并不代表密钥会自动被遮挡。

![Kilo 官方历史 MCP 设置界面，仅作参考](https://raw.githubusercontent.com/Kilo-Org/kilocode/1552877e82ceaecc79a9fd4be7859518745e6f56/packages/kilo-docs/public/img/using-mcp-in-kilo-code/mcp-installed-config.png)

*官方原始截图，2026-10-18 获取。图中是已有 Kilo MCP 设置页，不是本条目或 Ace 执行结果。官方未标注原截图日期和版本；当前 Kilo 7.8.x 使用 Marketplace 安装对话框，不要逐字照抄旧图中的菜单路径。*

## 2. 获取正确的应用 API Token

1. 注册或登录 [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=kilo_suno_api_key)。如果还没有通用应用，选择 **Initialize General Application**。
2. 打开 **General application**。生成前确认 Suno 服务权限、[当前价格和账户余额](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=kilo_suno_pricing)。通用应用 Token 可访问账户已有权限的多个服务；专用服务 Token 仅覆盖对应服务。
3. 使用复制图标获取现有 Key，或选择 **Manage Keys → Create**，创建名为 `Kilo Suno` 的专用 Key。按需设置有效期、用量限制。若启用 Allowed APIs，需同时允许 **/suno/audios and /suno/tasks**，以免只允许生成却无法查询结果。

![复制应用 API Key 或打开 Manage Keys](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/get-api-key-en.png)

![按需创建单独的应用 Key](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/create-api-key-en.png)

*上两张是 [Suno for Dify 教程](https://github.com/AceDataCloud/SunoDify/blob/8d3d03570e73324220f111f7fe343da0792a8071/README.md) 中的共享 Ace Applications 真实界面，来源固定到提交，2026-10-18 获取。图中 `Dify tutorial` 只是示例名称，本流程可填写 `Kilo Suno`。真实凭据已遮挡；这些图不是 Kilo 调用截图。*

只复制 **Token 字符串本身**，不要带 `Bearer `、引号或图中的遮挡符号。平台管理 Token（例如 `platform-...`）不是本集成需要的推理凭据。不要把真实 Key 放进聊天、提示词、截图或共享项目配置。

## 3. 在 Kilo 填入 Token

在 Marketplace 安装对话框中选择安装方式、**Global** 目标和 **Ace Data Cloud API Token** 参数，粘贴应用 Token 后点击 **Install**。Hosted 方式会自动添加 Bearer 前缀，并为这个显式 Token 流程关闭 OAuth。本条目不要求第三方厂商账户登录，也不消耗 Kilo Gateway 额度。

打开 MCP 设置检查连接，应能看到 Suno 工具。安装只注册工具，不代表同意付费生成；请检查工具权限，让生成和编辑操作仍需你的明确批准。

Local 方式使用上面已核实的公开包固定版本。更新前先查看对应服务发布说明，再调整版本。Hosted 服务由 Ace 维护，其部署版本与本地包版本是两项不同事实。

## 4. 先检查连接，不生成付费媒体

向 Kilo 输入：

```text
调用 suno_list_models 列出可用的 Suno 模型。不要生成音乐。
```

这一步检查工具发现或本地信息工具，不进行付费生成。信息工具返回的模型、限制或示例价格属于该包版本的内容；实际收费以链接中的实时 Ace 价格为准。仅看到 connected 或工具列表，不能证明媒体生成、终态或计费都已通过。不要为了测试安装而生成媒体。

## 5. 明确生成后，查询同一个任务

先查看 [服务参数和当前价格](https://platform.acedata.cloud/documents/suno-audios?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=kilo_suno_service_docs)，再明确要求生成所需内容。`suno_generate_music` 是付费操作；批准前核对具体模型、时长或尺寸等必填字段，不自动替换模型。

保留返回的 **task ID**。结果为 pending 时，按工具 schema 中的字段，用 **`suno_get_task`** 查询同一 ID，直到终态成功并返回最终音频链接，例如 `audio_url`，或出现终态失败。超时、断连不代表应该重新生成；应先查询已有任务。请打开接口实际返回的结果链接，不使用占位 URL。

在 [Ace Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=kilo_suno_usage) 核对同一应用、同一凭据的请求与用量记录。一个工作流程可能包含多个 API 请求，应对每个实际请求去重核查。安装量、单次本地测试成功都不是营收或唯一账单证明。

## 常见问题

- **搜索不到卡片**：官方投稿可能仍在审核，或客户端目录尚未刷新。当前入口以 [Kilo 官方说明](https://kilo.ai/docs/customize/marketplace) 为准。
- **401 或认证失败**：粘贴原始应用 API Token，并核对有效期、服务权限和 Allowed APIs；不要把真实 Token 发到 issue。
- **连接失败**：Hosted 需能通过 HTTPS 访问 `suno.mcp.acedata.cloud`；Local 需 Python 和 uvx。显式 Bearer Token 安装方式应保持 OAuth 关闭。
- **生成权限或余额错误**：在 Ace 核实服务权限、生成及任务查询 API 限制、预算和余额，不盲目重发可能收费的请求。
- **媒体仍 pending**：继续查询同一 task ID；重新生成会创建新任务，并可能再次收费。
- **模型或参数不匹配**：原样使用该服务工具和文档中的模型 ID、字段名，不从其他服务推断兼容性。

## 来源与发现方式

服务搜索词：**suno, music, lyrics**。标题和描述只覆盖本服务实际能力。Kilo 当前 MCP schema 没有自定义关键词或图标字段，因此使用支持的 name、description、category；不伪造 tags 或厂商官方图标身份。

运行时单一来源：`AceDataCloud/MCPs` → `SunoMCP` 镜像 → `mcp-suno`。本目录只提供 Kilo 上手指南，不创建新的服务实现、模型 fallback 或额外计费层。
