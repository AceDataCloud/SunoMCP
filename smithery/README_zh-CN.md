# Suno 的 MCP 直连配置

Smithery 在 2026 年 10 月 31 日关闭了托管连接及账号服务，保留公开目录。[平台公告](https://smithery.ai/future)

在支持 Streamable HTTP 的 MCP 客户端中添加 `https://suno.mcp.acedata.cloud/mcp`，按客户端提示完成服务授权。已有连接如使用旧的 Smithery 代理地址，请改用这个 Ace Data Cloud 端点。安装和密钥设置见[本服务说明](../README.md)。

生成前检查[当前价格与访问权限](https://platform.acedata.cloud/documents/suno-audios?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen)。查询进度时，将原任务的 `task_id` 传给 `suno_get_task`。
