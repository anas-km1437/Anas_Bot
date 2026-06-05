document.addEventListener("DOMContentLoaded", () => {
    let currentSessionId = null;
    const sessionsList = document.getElementById("sessions-list");
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const newChatBtn = document.getElementById("new-chat-btn");

    // إنشاء عنصر مؤشر الكتابة (النقاط الثلاث) وإضافته مؤقتاً
    const typingIndicator = document.createElement("div");
    typingIndicator.className = "typing-indicator";
    typingIndicator.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';

    // تحميل الجلسات
    function loadSessions() {
        fetch("/api/sessions")
            .then(res => res.json())
            .then(sessions => {
                sessionsList.innerHTML = "";
                sessions.forEach(session => {
                    const li = document.createElement("li");
                    li.textContent = session.title;
                    li.onclick = () => loadMessages(session.id, li);
                    sessionsList.appendChild(li);
                });
                if (sessions.length > 0 && !currentSessionId) {
                    loadMessages(sessions[0].id, sessionsList.firstChild);
                }
            });
    }

    // إنشاء محادثة جديدة
    newChatBtn.onclick = () => {
        fetch("/api/new_session", { method: "POST" })
            .then(res => res.json())
            .then(data => {
                currentSessionId = data.id;
                chatMessages.innerHTML = "";
                loadSessions();
            });
    };

    // تحميل رسائل الجلسة
    function loadMessages(sessionId, liElement) {
        currentSessionId = sessionId;
        document.querySelectorAll("#sessions-list li").forEach(li => li.classList.remove("active"));
        if(liElement) liElement.classList.add("active");

        fetch(`/api/messages/${sessionId}`)
            .then(res => res.json())
            .then(messages => {
                chatMessages.innerHTML = "";
                messages.forEach(msg => {
                    appendMessage(msg.sender, msg.text);
                });
                scrollToBottom();
            });
    }

    // إضافة الرسالة للواجهة
    function appendMessage(sender, text) {
        const div = document.createElement("div");
        div.className = `msg-bubble ${sender === 'Hanan' ? 'msg-user' : 'msg-bot'}`;
        div.textContent = text;
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    // إظهار النقاط الثلاث
    function showTyping() {
        chatMessages.appendChild(typingIndicator);
        typingIndicator.style.display = "flex";
        scrollToBottom();
    }

    // إخفاء النقاط الثلاث
    function hideTyping() {
        typingIndicator.style.display = "none";
    }

    // النزول لأسفل المحادثة
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // إرسال الرسالة
    function sendMessage() {
        const text = userInput.value.trim();
        if (!text || !currentSessionId) return;

        // إظهار رسالة المستخدم
        appendMessage("Hanan", text);
        userInput.value = "";
        
        // إظهار أن البوت يكتب...
        showTyping();

        fetch("/api/send_message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: currentSessionId, text: text })
        })
        .then(res => res.json())
        .then(data => {
            hideTyping(); // إخفاء النقاط بعد وصول الرد
            if (data.reply) {
                appendMessage("AnosBot", data.reply);
            }
        })
        .catch(err => {
            hideTyping();
            appendMessage("AnosBot", "يا روحي الشبكة فيها شوية ضغط، دقيقة بس!");
            console.error(err);
        });
    }

    sendBtn.onclick = sendMessage;
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    loadSessions();
});
