# Suno by Ace Data Cloud：中文安装与首用指南

[English](https://github.com/AceDataCloud/SunoMCP/blob/main/README.md)

本集成由 **Ace Data Cloud** 提供，可在支持 MCP 的客户端中使用 Suno 的音乐生成、歌词、翻唱和任务结果。它不是模型厂商官方出品或背书的应用。

更新日期：2026-10-19。品牌标题、图标、指南入口和中英文本已随 [源码 PR #983](https://github.com/AceDataCloud/MCPs/pull/983) 合并并镜像；本服务官方条目和匹配 PyPI 包已读回 `2026.10.18.2`。这证明公开发布，不证明所有客户端普通安装或生成终态已验收。

## 1. 从官方目录找到单服务入口

打开 [Suno 的官方 MCP Registry 条目](https://registry.modelcontextprotocol.io/?q=io.github.AceDataCloud%2Fmcp-suno)，确认名称为 `io.github.AceDataCloud/mcp-suno`。可直接搜索 `suno`；官方当前按名称子串搜索，显示标题不等于搜索别名。 展开条目，在 **Packages** 查看 `mcp-suno`，在 **Remotes** 查看 `https://suno.mcp.acedata.cloud/mcp`。

Registry 是目录，不是运行工具的聊天软件，也没有统一的“安装后直接聊天”界面。若客户端有官方目录导入，使用该条目的标准安装信息；若没有，只能按下面手动连接，这一步不能记作客户端原生目录收录。不要为了凑条目复制同一个服务器换名。

官方条目的 Website 已读回为带来源标签的公共指南；若看到页脚 Local，它表示当前网站同源模式，并非强制访问 localhost。本文不放无法匿名访问的内部报告图；实际客户端截图参考在第3节，不能冒充本服务已安装。

## 2. 注册/登录并取得专用 API Token

1. 打开 [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_api_key)，注册或登录。
2. 进入 **General application**；如果没有，先点 **Initialize General Application**。通用应用可访问账户已开通的服务；单服务应用 Key 的范围限于该应用。
3. 复制应用卡片的 **API Key**，或打开 **Keys / Manage Keys → Create** 创建单独命名的集成凭据，例如 `Suno MCP`。它与 `platform-...` 账户管理 Token 不同，后者不能代替生成 API Key。
4. 核对 **Expiration Time、Set Usage Limitation、Allowed APIs**。若限制接口，至少覆盖本次使用的 `/suno/audios` 与查询 `/suno/tasks`。同时确认服务/模型权限、余额和[当前价格](https://platform.acedata.cloud/models?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_readme_models)，不要把历史额度或价格当今天可用。
5. 只复制 Token 原值；客户端 **API Token/API Key** 或环境变量字段不加 `Bearer `，手动 HTTP `Authorization` 头才写 `Bearer <TOKEN>`。不要把 Key 放在聊天正文、截图、共享配置或 Git。

![Ace 平台真实原图：复制 Key 或管理 Key，内容已遮挡](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/get-api-key-en.png)

![Ace 平台真实原图：创建独立 Key 并按需设置限制](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/create-api-key-en.png)

两图源自固定版本 SunoDify 教程，仓库图片更新日期为 **2026-10-09 Asia/Shanghai**，敏感内容已遮挡。创建框的历史名称是 `Dify tutorial`，这里只复用相同平台流程；不能声称已经为本服务新建 Key 或已在客户端填写。

## 3. 在客户端填写连接与 Token

**支持远程连接的客户端：** 添加远程 MCP，地址填 `https://suno.mcp.acedata.cloud/mcp`。支持 OAuth 的客户端可走已有浏览器登录/授权；固定 API Key 方式在客户端凭据字段填原值，或其 HTTP Header 设置 `Authorization: Bearer <TOKEN>`。不要两种方式混填，也不要把网址当模型 Provider base URL。

![MCP 官方文档真实客户端截图：添加远程连接器](https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/86f6e0c675afea9a8f233e09b6faf566b126086c/docs/images/quickstart-remote/1-add-connector.png)

这是 MCP 官方文档中的 Claude **Example Remote Server** 参考图，图片仓库最后修改于 **2025-07-25**、客户端版本未注明。只解释名称/URL/信任提示所在位置；图中不是 Ace，也不证明 Suno 已在该客户端连接成功。不同客户端菜单以各自当前官方指南为准。

**本地 stdio 安装：** 需要 Python 与 `uv`；在客户端的 MCP 服务器设置中使用包名并填 `env`。有官方目录安装功能时，应由客户端读取条目指定的包版本，而不是猜“最新版”。手动通用配置示例：

```json
{
  "mcpServers": {
    "suno-by-ace": {
      "command": "uvx",
      "args": ["mcp-suno"],
      "env": {"ACEDATACLOUD_API_TOKEN": "YOUR_ACE_APPLICATION_TOKEN"}
    }
  }
}
```

占位符不是有效 Key。优先使用客户端安全凭据存储，保存的用户级配置要保密；项目仓库中不要提交字面量 Token。远程地址方式和本地包方式任选一种；不要因两者都出现就重复启动两份同名服务。公开包存在不等于本机已安装；若下载站连接超时，保留日志，不改 TLS 验证或假称安装成功。

## 4. 先免费检查连接，再决定是否生成

初始化后检查客户端工具列表。调用 `suno_list_models` 阅读模型说明；该工具只返回静态信息，不发起生成。 这只证明工具可发现/信息可读，不能证明收费请求、媒体或账单。

真正首次生成前，先选择客户端 schema 中支持的模型、核当前价格和预算，再调用 `suno_generate_music`。先提供明确的 `prompt` 与所选模型，其他参数按工具 schema 填写；不要因为示例没有额度就自动提交。文档更新过程中没有为本教程新发收费生成。

## 5. 用同一个任务 ID 查询结果

保存原始提交响应的 `task_id`。在 `suno_get_task` 中将它填入 **`task_id`**；输入的是返回值，不是变量名称或另建新任务。已有合法成功任务也只能查询原 ID。

```json
{"task_id": "ORIGINAL_TASK_ID"}
```

`pending`、空媒体或客户端执行成功提示都不等于生成完成。继续查询同一 ID，直到服务返回成功终态/媒体，或明确失败；不要重跑生成来“刷新结果”。任务返回字段和响应中的错误以本服务工具为准，查看媒体 URL 是否可访问。保留 task/trace ID 供排错，不发 Key。本生态尚无该目录安装到终态媒体、唯一 Credits 账单的完整新证据，不把其他宿主的运行图移植成这里的结果。

## 6. 排错

| 现象 | 操作 |
|---|---|
| 搜不到条目 | 使用 `suno` 或完整标识，确认查询官方目录；第三方宿主有独立收录策略。 |
| Website 404 | 官方条目已读回正确指南；若仍404，确认是否使用旧缓存/下游目录，保留实际URL反馈，不反复生成。 |
| 401 / 403 | 检查 Token 原值、应用服务范围、过期与接口限制；固定 Header 无效时不要假设自动切 OAuth。 |
| 模型不可用/余额不足 | 查看账户当前权限、余额和价格，避免盲目切模型或反复生成。 |
| 包下载超时 | 记录下载站/版本与网络错误；不把 metadata 存在当安装成功。 |
| 任务 pending / 媒体空 | 查询原任务 ID；不提交新生成。 |
| 任务失败或5xx | 检查原 task/trace 与请求历史后再决定是否重试，避免重复扣费。 |

## 证据与边界

本页是中文首用说明，不是已完成的客户端 UI 验收或真实付费效果报告。官方目录公开、包发行、普通安装、客户端调用、终态媒体、唯一账单、注册付费归因必须分别验证；测试与截图参考不能互相替代。
