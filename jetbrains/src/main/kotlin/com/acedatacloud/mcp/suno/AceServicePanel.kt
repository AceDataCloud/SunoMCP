package com.acedatacloud.mcp.suno

import com.google.gson.JsonObject
import com.google.gson.JsonParser
import com.intellij.ide.BrowserUtil
import com.intellij.openapi.ui.Messages
import java.awt.BorderLayout
import java.awt.FlowLayout
import java.net.URI
import javax.swing.*

/** Native IDE controls for Suno. Uses the existing Ace MCP, not a new LLM provider. */
class AceServicePanel : JPanel(BorderLayout(8, 8)) {
    private val apiKey = JPasswordField(34)
    private val model = JTextField(28)
    private val prompt = JTextArea(4, 48)
    private val taskId = JTextField(30)
    private val result = JTextArea(12, 58).apply { isEditable = false; lineWrap = true; wrapStyleWord = true }
    private val status = JLabel("No request sent. API calls use your application balance.")
    private val operations = mutableListOf<JButton>()
    private var disposed = false

    init {
        val controls = JPanel().apply { layout = BoxLayout(this, BoxLayout.Y_AXIS) }
        controls.add(JLabel("Suno by Ace Data Cloud · independent integration provided by Ace Data Cloud"))
        controls.add(row("Application API Key", apiKey))
        controls.add(row("Model (choose explicitly)", model))
        controls.add(JLabel("Prompt"))
        controls.add(JScrollPane(prompt))
        controls.add(row("Existing task ID", taskId))
        val buttons = JPanel(FlowLayout(FlowLayout.LEFT))
        buttons.add(button("List models", "suno_list_models") { JsonObject() })
        buttons.add(button("Generate music", "suno_generate_music", billable = true) {
            require(model.text.isNotBlank()) { "List models, check current pricing and enter a model explicitly." }
            require("".isEmpty() || model.text.trim().startsWith("")) {
                "This independent Suno entry only accepts  models. Use the matching service plugin for another model."
            }
            require(prompt.text.isNotBlank()) { "Enter a prompt." }
            JsonObject().apply { addProperty("model", model.text.trim()); addProperty("prompt", prompt.text.trim()) }
        })
        buttons.add(button("Check existing task", "suno_get_task") {
            require(taskId.text.isNotBlank()) { "Enter the task ID from the original submission." }
            JsonObject().apply { addProperty("task_id", taskId.text.trim()) }
        })
        buttons.add(JButton("Get API key").apply { addActionListener { BrowserUtil.browse("https://platform.acedata.cloud/console/applications?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_api_key") } })
        buttons.add(JButton("Current pricing").apply { addActionListener { BrowserUtil.browse("https://platform.acedata.cloud/models?utm_source=jetbrains_marketplace&utm_medium=referral&utm_campaign=evergreen&utm_content=suno_mcp_jetbrains_models") } })
        controls.add(buttons)
        controls.add(JLabel("The native panel does not require AI Assistant. MCP chat configuration remains optional."))
        controls.add(JLabel("The key stays in this panel's memory and is cleared when this settings page closes."))
        add(controls, BorderLayout.NORTH)
        add(JScrollPane(result), BorderLayout.CENTER)
        add(status, BorderLayout.SOUTH)
    }

    private fun row(label: String, field: JComponent) = JPanel(FlowLayout(FlowLayout.LEFT)).apply {
        add(JLabel(label)); add(field)
    }

    private fun button(label: String, tool: String, billable: Boolean = false, arguments: () -> JsonObject): JButton {
        return JButton(label).also { button ->
            operations.add(button)
            button.addActionListener {
                try {
                    val args = arguments()
                    val token = String(apiKey.password).trim()
                    require(token.isNotBlank() && !token.startsWith("Bearer ")) { "Paste only your raw application API key." }
                    if (billable && Messages.showYesNoDialog(
                            null as com.intellij.openapi.project.Project?, "Submit one Suno request using model ${model.text.trim()}? This can charge your Ace application balance. Check Current pricing first. No automatic retry will run.",
                            "Submit a paid generation", "Submit once", "Cancel", Messages.getWarningIcon()
                        ) != Messages.YES) return@addActionListener
                    operations.forEach { it.isEnabled = false }
                    status.text = "Request running. Do not submit again."
                    object : SwingWorker<String, Unit>() {
                        override fun doInBackground(): String = AceServiceClient(URI("https://suno.mcp.acedata.cloud/mcp"), token).callTool(tool, args)
                        override fun done() {
                            if (disposed) return
                            operations.forEach { it.isEnabled = true }
                            try {
                                val output = get()
                                result.text = output
                                findTaskId(output)?.let { taskId.text = it }
                                status.text = if (billable) "Submission returned. Use the same task ID to check completion; a response alone does not mean success." else "Response received. Review the status and result below."
                            } catch (error: Exception) {
                                result.text = error.cause?.message ?: error.message ?: "Request failed."
                                status.text = "No retry sent. If submission may have reached the service, check its existing task ID before resubmitting."
                            }
                        }
                    }.execute()
                } catch (error: IllegalArgumentException) { status.text = error.message }
            }
        }
    }

    private fun findTaskId(text: String): String? = runCatching {
        val root = JsonParser.parseString(text).asJsonObject
        root.get("task_id")?.takeIf { !it.isJsonNull }?.asString
            ?: root.getAsJsonObject("data")?.get("task_id")?.takeIf { !it.isJsonNull }?.asString
    }.getOrNull()

    fun dispose() { disposed = true; apiKey.text = "" }
}
