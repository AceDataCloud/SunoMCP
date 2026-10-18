package com.acedatacloud.mcp.suno

import com.google.gson.JsonArray
import com.google.gson.JsonObject
import com.google.gson.JsonParser
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.time.Duration

/** MCP transport reused by the native service panel. No automatic submission or retry. */
class AceServiceClient(private val endpoint: URI, private val token: String) {
    private val http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(20)).build()
    private var session: String? = null
    private var nextId = 1

    fun callTool(name: String, arguments: JsonObject): String {
        require(token.isNotBlank()) { "Enter your Ace application API key first." }
        val init = JsonObject().apply {
            addProperty("protocolVersion", "2025-03-26")
            add("capabilities", JsonObject())
            add("clientInfo", JsonObject().apply {
                addProperty("name", "ace-jetbrains-suno")
                addProperty("version", "1")
            })
        }
        exchange("initialize", init)
        exchange("notifications/initialized", JsonObject(), notification = true)
        if (name.startsWith("@schema:")) {
            val target = name.removePrefix("@schema:")
            val tools = exchange("tools/list", JsonObject()).getAsJsonArray("tools") ?: JsonArray()
            val tool = tools.firstOrNull { it.asJsonObject.get("name")?.asString == target }?.asJsonObject
                ?: error("The configured generation tool is not available on this server.")
            return tool.getAsJsonObject("inputSchema")?.getAsJsonObject("properties")?.get("model")?.toString()
                ?: error("No model schema was published by the server.")
        }
        val result = exchange("tools/call", JsonObject().apply {
            addProperty("name", name)
            add("arguments", arguments)
        })
        val content = result.getAsJsonArray("content") ?: JsonArray()
        val text = content.mapNotNull { item ->
            item.asJsonObject.takeIf { it.get("type")?.asString == "text" }?.get("text")?.asString
        }.joinToString("\n")
        if (result.get("isError")?.asBoolean == true) {
            throw IllegalStateException(text.ifBlank { "The service returned a tool error." })
        }
        if (name == "suno_list_models" && "".isNotEmpty()) {
            return text.lines().filter { it.contains("") }.joinToString("\n")
                .ifBlank { "No Suno models were listed. Do not submit a generation until your model is available." }
        }
        return text.ifBlank { result.toString() }
    }

    private fun exchange(method: String, params: JsonObject, notification: Boolean = false): JsonObject {
        val id = if (notification) null else nextId++
        val body = JsonObject().apply {
            addProperty("jsonrpc", "2.0")
            if (id != null) addProperty("id", id)
            addProperty("method", method)
            add("params", params)
        }
        val builder = HttpRequest.newBuilder(endpoint)
            .timeout(Duration.ofSeconds(120))
            .header("Content-Type", "application/json")
            .header("Accept", "application/json, text/event-stream")
            .header("Authorization", "Bearer $token")
            .header("MCP-Protocol-Version", "2025-03-26")
            .POST(HttpRequest.BodyPublishers.ofString(body.toString()))
        session?.let { builder.header("Mcp-Session-Id", it) }
        val response = http.send(builder.build(), HttpResponse.BodyHandlers.ofString())
        response.headers().firstValue("Mcp-Session-Id").ifPresent { session = it }
        check(response.statusCode() in 200..299) {
            when (response.statusCode()) {
                401 -> "HTTP 401: check the application key, expiry and allowed APIs."
                403 -> "HTTP 403: the operation was denied; check service access or content restrictions."
                429 -> "HTTP 429: rate limit reached. Wait before trying again."
                else -> "Service HTTP ${response.statusCode()}. No request was retried."
            }
        }
        if (notification) return JsonObject()
        val raw = response.body().trim()
        val messages = if (response.headers().firstValue("content-type").orElse("").contains("text/event-stream")) {
            raw.replace("\r\n", "\n").split("\n\n").mapNotNull { event ->
                event.lines().filter { it.startsWith("data:") }
                    .joinToString("\n") { it.removePrefix("data:").trimStart() }
                    .takeIf { it.isNotBlank() && it != "[DONE]" }
            }
        } else listOf(raw)
        val reply = messages.mapNotNull { message ->
            runCatching { JsonParser.parseString(message).asJsonObject }.getOrNull()
        }.firstOrNull { it.get("id")?.asInt == id }
            ?: error("No matching MCP response. Do not resubmit a generation; check an existing task ID first.")
        reply.getAsJsonObject("error")?.let {
            // Do not expose transport payloads that may contain credentials or private data.
            error("MCP request failed (code ${it.get("code")}). No retry was sent.")
        }
        return reply.getAsJsonObject("result") ?: error("MCP response has no result.")
    }
}
