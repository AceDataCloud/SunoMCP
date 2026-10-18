package com.acedatacloud.mcp.suno

import com.intellij.openapi.options.Configurable
import com.intellij.openapi.ui.DialogPanel
import com.intellij.ui.dsl.builder.AlignX
import com.intellij.ui.dsl.builder.bindText
import com.intellij.ui.dsl.builder.panel
import com.intellij.ui.dsl.builder.rows
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import javax.swing.JComponent

class McpSunoSettingsConfigurable : Configurable {

    private var myPanel: DialogPanel? = null
    private var nativePanel: AceServicePanel? = null
    private var apiToken: String = ""

    override fun getDisplayName(): String = "Suno MCP"

    override fun createComponent(): JComponent {
        val settings = McpSunoSettings.getInstance()
        apiToken = settings.state.apiToken

        myPanel = panel {
            group("API Configuration") {
                // BEGIN TOKEN ONBOARDING
                row {
                    browserLink("Get an API key", "https://platform.acedata.cloud/console/applications?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_api_key")
                }
                row {
                    comment("Sign in, initialize General Application if needed, then copy an API key.")
                }
                // END TOKEN ONBOARDING
                row("API Token:") {
                    passwordField()
                        .bindText(::apiToken)
                        .align(AlignX.FILL)
                        .comment("Paste the raw token without Bearer. Click Apply before copying a configuration.")
                }
            }

            group("MCP Configuration for AI Assistant") {
                row {
                    comment(
                        "Copy a configuration below, then paste it into<br>" +
                        "<b>Settings → Tools → AI Assistant → Model Context Protocol (MCP)</b>"
                    )
                }

                group("STDIO (Local)") {
                    row {
                        comment("Runs the MCP server locally via <code>uvx</code>. Requires <a href=\"https://github.com/astral-sh/uv\">uv</a> installed.")
                    }
                    row {
                        textArea()
                            .align(AlignX.FILL)
                            .rows(8)
                            .applyToComponent {
                                text = settings.getStdioConfig()
                                isEditable = false
                            }
                    }
                    row {
                        button("Copy STDIO Config") {
                            copyToClipboard(McpSunoSettings.getInstance().getStdioConfig())
                        }
                    }
                }

                group("HTTP (Remote)") {
                    row {
                        comment("Connects to the hosted MCP server. No local install needed.")
                    }
                    row {
                        textArea()
                            .align(AlignX.FILL)
                            .rows(7)
                            .applyToComponent {
                                text = settings.getHttpConfig()
                                isEditable = false
                            }
                    }
                    row {
                        button("Copy HTTP Config") {
                            copyToClipboard(McpSunoSettings.getInstance().getHttpConfig())
                        }
                    }
                }
            }

            group("Links") {
                row {
                    browserLink("Ace Data Cloud Platform", "https://platform.acedata.cloud?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_platform")
                }
                row {
                    browserLink("Documentation", "https://platform.acedata.cloud/documents/suno-mcp?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_quick_start")
                }
                row {
                    browserLink("Source Code", "https://github.com/AceDataCloud/SunoMCP")
                }
                row {
                    browserLink("PyPI Package", "https://pypi.org/project/mcp-suno/")
                }
            }
        }

        nativePanel = AceServicePanel()
        return javax.swing.JTabbedPane().apply {
            addTab("Suno", nativePanel)
            addTab("AI Assistant MCP (optional)", myPanel)
        }
    }

    override fun isModified(): Boolean {
        val settings = McpSunoSettings.getInstance()
        return apiToken != settings.state.apiToken
    }

    override fun apply() {
        val settings = McpSunoSettings.getInstance()
        settings.state.apiToken = apiToken
    }

    override fun reset() {
        val settings = McpSunoSettings.getInstance()
        apiToken = settings.state.apiToken
        myPanel?.reset()
    }

    override fun disposeUIResources() {
        nativePanel?.dispose()
        nativePanel = null
        myPanel = null
    }

    private fun copyToClipboard(text: String) {
        val clipboard = Toolkit.getDefaultToolkit().systemClipboard
        clipboard.setContents(StringSelection(text), null)
    }
}
