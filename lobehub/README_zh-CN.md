# LobeHub：Suno（Ace Data Cloud 提供）

[English](README.md) · [官方市场安装入口](https://lobehub.com/mcp/acedatacloud-mcpsuno) · [当前 API/价格](https://platform.acedata.cloud/documents/suno-audios?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_lobehub_readme_pricing)

这是 **Ace Data Cloud 提供的 Suno 集成**，不是模型原厂官方插件。复用现有 [SunoMCP](https://github.com/AceDataCloud/SunoMCP) 和 `mcp-suno`，不新建重复后台。发布材料对应已有条目 `acedatacloud-mcpsuno`；2026-10-18 公开页仍为未验证旧卡片，不能把本文件当作更新已上架。

## 1. 安装

![LobeHub 官方 MCP 市场真实历史截图](https://lobehub.com/img/hub/blog/assetsb811f2aae8e8346aef16793d6bd10f88.webp)

原图来自 [2026-03-03 的官方文档源码](https://github.com/lobehub/lobehub/blob/43578a9bcc37dbf0ec9beb5f5ab1dcd5ba09daf7/docs/usage/community/mcp-market.mdx)，拍摄时间/产品版本未知；2026-10-18 引用核验。它只说明真实搜索框、分类与卡片位置，不是 Ace 已安装、当前排名或调用成功证据。

打开上面的单服务市场入口，查看源码、安装与认证要求后安装。搜索 `Suno` 或 `Ace Data Cloud`；不保证排名。同名历史卡片以精确 identifier 区分，不另发重复项。

也可在 **设置 → 连接器** 导入本目录 [单项 HTTP 配置](install-http.json)。稳定版 v2.2.19 一次只读取第一项，而且不保留 HTTP headers/auth；导入后必须在界面单独填写认证。桌面端可用 [STDIO 配置](install-stdio.json)，并安装 uvx。

## 2. 登录并获取 Token

登录或注册 [Ace → Applications（我的应用）](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_lobehub_readme_api_key)。如果还没有 **General application（通用应用）**，先初始化，再打开应用；确认 Suno 服务权限、余额和当前价格。复制已有服务 API Token，或在 **Manage Keys** 创建专用于 LobeHub 的 Key。不要填平台管理 Token 或原厂 Key。

![复制 API Token，Ace 真实历史截图；2026-10-18 引用](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/get-api-key-en.png)

![创建专用 Key，真实凭据已隐藏；历史截图](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/create-api-key-en.png)

图来自上面固定 commit 的真实 Ace 页面，拍摄日期未断言；不是 LobeHub 安装或调用成功证据。

## 3. 在 LobeHub 填写与启用

在连接器认证处选 **Bearer**，只填 Token 字符串，不加 `Bearer `、引号或遮挡字符；或者手动添加 `Authorization: Bearer YOUR_API_TOKEN` 请求头。保存并检查连接，再进入 **助理设置 → 连接器** 启用，生成/修改工具先设 Ask 或 Deny。真实界面步骤见 [LobeHub 官方指南](https://lobehub.com/docs/usage/community/mcp-market)。本生态的实际认证截图仍排队核验，不用假截图替代。

## 4. 首用与异步结果

只调用 `suno_list_models`，参数为空；它返回内置信息，不发生成请求。 如果通过聊天模型要求助理调用，聊天模型仍可能计费；优先使用直接工具测试入口。

生成前选 schema 支持的型号并核价，只提交一次。保存任务 ID，用 `suno_get_task` 查询同一个 ID，直到明确终态成功或失败。预览链接/等待状态不是完成，不重复提交生成；终态成功后打开最终媒体，保留任务与用量记录检查唯一账单。本次材料没有发收费生成。

## 常见问题

- 401/403：重新复制服务 Token，检查权限、有效期和余额；不要用平台管理凭据。
- 导入后未认证：HTTP 快速导入会丢弃认证；必须到界面填写 Bearer。
- 有连接没有工具：给当前助理启用，并检查工具权限和聊天模型工具能力。
- 本地启动：当前变量是 `ACEDATACLOUD_API_TOKEN`，不是旧 `ACEDATA_API_TOKEN`；HTTP 用 https://suno.mcp.acedata.cloud/mcp。
- Pending：继续查同 ID，不因等待重发；429/500 保留真实错误，不自动换模型或价格。

发布者应使用已有身份确认 `plugin list`，认领现有 `acedatacloud-mcpsuno` 后 update；不得重复 publish。manifest 来自已发包 `2026.10.12.1` 的真实 schema，远程版本一致性需发布前认证核实。当前未登录 publisher，不能声称认领或认证已完成。归因采用后端认可的 opensource/referral/evergreen 四项标签，以 `suno_lobehub_*` 区分具体入口，不宣称带来注册/收入。
