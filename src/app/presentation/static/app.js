/* ===== BarCloud Inventory Chatbot — Client Logic ===== */

const SESSION_ID = crypto.randomUUID();

// DOM references
const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const sessionBadge = document.getElementById("sessionBadge");
const sqlCode = document.getElementById("sqlCode");
const intentBadge = document.getElementById("intentBadge");
const metricLatency = document.getElementById("metricLatency");
const metricProvider = document.getElementById("metricProvider");
const metricTokensIn = document.getElementById("metricTokensIn");
const metricTokensOut = document.getElementById("metricTokensOut");

// Show truncated session ID
sessionBadge.textContent = SESSION_ID.slice(0, 8) + "…";
sessionBadge.title = SESSION_ID;

// Enter key sends message
messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Sample question click
function askSample(btn) {
    messageInput.value = btn.textContent;
    sendMessage();
}

// Remove welcome message on first interaction
let welcomeRemoved = false;
function removeWelcome() {
    if (welcomeRemoved) return;
    const welcome = chatMessages.querySelector(".welcome-msg");
    if (welcome) {
        welcome.style.animation = "fadeIn 0.3s ease reverse forwards";
        setTimeout(() => welcome.remove(), 300);
    }
    welcomeRemoved = true;
}

// Add a message bubble to the chat
function addBubble(role, content) {
    const row = document.createElement("div");
    row.className = `msg-row ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar";
    avatar.textContent = role === "user" ? "U" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.textContent = content;

    row.appendChild(avatar);
    row.appendChild(bubble);
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return row;
}

// Show/hide typing indicator
function showTyping() {
    const row = document.createElement("div");
    row.className = "msg-row assistant";
    row.id = "typingRow";

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar";
    avatar.textContent = "AI";

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

    row.appendChild(avatar);
    row.appendChild(bubble);
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById("typingRow");
    if (el) el.remove();
}

// Update the SQL panel
function updateSQL(sql) {
    sqlCode.textContent = sql || "No query generated.";
}

// Update intent badge
function updateIntent(sql) {
    // Simple heuristic to display a readable intent
    if (!sql) {
        intentBadge.textContent = "—";
        intentBadge.classList.remove("active");
        return;
    }
    let label = "custom_query";
    const upper = sql.toUpperCase();
    if (upper.includes("COUNT(*)") && upper.includes("ASSETS") && !upper.includes("JOIN"))
        label = "count_assets";
    else if (upper.includes("SITENAME") && upper.includes("COUNT"))
        label = "assets_by_site";
    else if (upper.includes("SUM") && upper.includes("COST"))
        label = "asset_value_by_site";
    else if (upper.includes("YEAR(PURCHASEDATE)"))
        label = "assets_purchased_this_year";
    else if (upper.includes("TOP 1") && upper.includes("VENDORNAME"))
        label = "top_vendor_by_assets";
    else if (upper.includes("TOTALBILLED"))
        label = "total_billed_last_quarter";
    else if (upper.includes("OPENPOS") || (upper.includes("PURCHASEORDERS") && upper.includes("OPEN")))
        label = "open_purchase_orders";
    else if (upper.includes("CATEGORY") && upper.includes("GROUP BY"))
        label = "assets_by_category";
    else if (upper.includes("CUSTOMERNAME") && upper.includes("SALESORDERS"))
        label = "sales_orders_by_customer";

    intentBadge.textContent = label;
    intentBadge.classList.add("active");
}

// Update metrics
function updateMetrics(data) {
    metricLatency.textContent = data.latency_ms != null ? data.latency_ms + "ms" : "—";
    metricProvider.textContent = data.provider || "—";
    metricTokensIn.textContent = data.token_usage ? data.token_usage.prompt_tokens : "—";
    metricTokensOut.textContent = data.token_usage ? data.token_usage.completion_tokens : "—";
}

// Main send function
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    removeWelcome();
    addBubble("user", text);
    messageInput.value = "";
    sendBtn.disabled = true;
    messageInput.disabled = true;
    showTyping();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: SESSION_ID, message: text }),
        });

        const data = await res.json();
        hideTyping();

        if (data.status === "ok") {
            addBubble("assistant", data.natural_language_answer);
            updateSQL(data.sql_query);
            updateIntent(data.sql_query);
        } else {
            const errRow = addBubble("assistant", data.error_detail || data.natural_language_answer || "An error occurred.");
            errRow.classList.add("error");
            updateSQL("");
        }

        updateMetrics(data);
    } catch (err) {
        hideTyping();
        const errRow = addBubble("assistant", "Network error — could not reach the server.");
        errRow.classList.add("error");
    } finally {
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}
