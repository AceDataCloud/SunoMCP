# Suno by Ace Data Cloud · VS Code 中文教程

[English](https://github.com/AceDataCloud/SunoMCP/blob/main/vscode/README.md) · [官方扩展市场安装](https://marketplace.visualstudio.com/items?itemName=acedatacloud.mcp-suno)

本扩展由 **Ace Data Cloud** 提供和运营，接入对应模型/服务；不是模型或服务品牌方的官方扩展。使用 Ace 的应用 API Token，不能用其他供应方的 Key 替代。安装本服务独立扩展即可注册工具，合集只作可选补充；仍需选择支持工具调用的聊天模型并配置凭据。

## 1. 安装和找到入口

在 VS Code 扩展市场搜索本服务名称，确认发布者为 `acedatacloud`，打开上述安装入口并点击 Install。要求 VS Code 1.101+。安装后不必手写 `mcp.json`。停用合集或手工配置中的同一服务副本，避免工具重复。

## 2. 注册并复制应用 API Token

1. 打开 [Ace Applications](https://platform.acedata.cloud/console/applications?utm_source=vscode_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_vscode_api_key)，先注册或登录 Ace。
2. 找到 **General application（通用应用）**；若不存在，先点 **Initialize General Application**。可复制卡片上的 API Key，或进入 **Keys / Manage Keys → Create** 创建本扩展专用 Key。
3. 创建时检查有效期、使用限额、Allowed APIs。只开放需要的生成/查询接口，确认服务权限、[当前价格](https://platform.acedata.cloud/models?utm_source=vscode_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_vscode_models)及余额。生成和任务查询是两个操作，允许查询不等于允许生成。
4. 复制裸 token，不加引号或 `Bearer `。`platform-...` 是账号管理令牌，不能替代图片、视频或音乐服务的应用 Key。

![通用应用的API Key复制入口，真实界面参考](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/get-api-key-en.png)

![创建独立Key和可选权限限制，真实界面参考](https://raw.githubusercontent.com/AceDataCloud/SunoDify/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial/create-api-key-en.png)

上图来自 Ace SunoDify 已有真实平台截图，固定到原始提交；界面标签为英文，仅说明取 Key，不证明本扩展已发布。不要把真实 Key 放到截图、提示词或Git提交。

## 3. 粘贴到VS Code并选工具

运行命令 **Suno by Ace Data Cloud: Set Ace Data Cloud API Key**，粘贴应用 Token；保存于 VS Code SecretStorage。服务器地址为 `https://suno.mcp.acedata.cloud/mcp`。若要求信任服务器，先核对地址。

打开 **Chat: Manage Language Models**，使所选模型可见，再在 Chat 选择它；可安装独立的 [Ace Chat Models](https://marketplace.visualstudio.com/items?itemName=acedatacloud.chat-models)。打开 **Agent → Configure Tools**，只勾选 `suno_list_models`，列表为空时先 Update Tools。组织禁用 BYOK 时遵守管理员政策。

![真实VS Code模型管理界面参考](https://raw.githubusercontent.com/AceDataCloud/VSCodeModelProvider/667593eb14bf15d434a1c41d47ef1f39199f7d68/assets/tutorial/02-manage-models.png)

![真实VS Code工具选择界面参考](https://raw.githubusercontent.com/AceDataCloud/MCPs/537d5767aea410db930e4b01faf5dd14580c8ba7/vscode-bundle/assets/tutorial/04-tools.png)

VS Code 1.141历史真实截图于2026-10-09收入教程；工具图以OpenAI为例，实际选择本服务和上面指定的工具。不是当前新版本截图，也不能当作本独立卡片已经实测。完整模型设置见 [Ace模型教程](https://github.com/AceDataCloud/VSCodeModelProvider#4-show-the-model-in-chat)。

## 4. 首次验证与同ID结果查询

```text
只调用 suno_list_models，显示模型/动作说明，不要生成任何媒体。
```

模型说明工具不生成媒体，也不证明生成权限；没有已完成任务时，图片服务停在工具发现，不要为验安装新发生成。聊天模型和辅助请求仍可能收费，先查模型价格。已有任务只用 `suno_get_task` 查询同一个原ID（将 `TASK_ID` 替换为自己的原任务ID），直至成功或失败；打开结果媒体，并在 [Usage](https://platform.acedata.cloud/console/usage?utm_source=vscode_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_vscode_console_usage) 对应原生成任务及Credits账单。accepted、绿色聊天回合都不等于最终媒体成功，不要重新生成来轮询。

## 5. 常见问题

- 看不到模型：先完成 Manage Language Models 和模型扩展设置；不要绕过组织政策。
- 看不到工具：Update Tools、确认工作区和服务器信任，停用重复的合集/手工副本。
- 401/403：查Key完整性、应用/服务访问权限、有效期、限额、Allowed APIs与余额。
- 任务未完成：保留原ID继续查；429或5xx先核原任务和Usage，不自动付费重试。

更多服务说明见 [Documentation](https://platform.acedata.cloud/documents/suno-mcp?utm_source=vscode_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_vscode_quick_start)。支持排查时提供task/trace ID，不提供Key。
