document.addEventListener("DOMContentLoaded", () => {
    let currentSessionId = null;
    const sessionsList = document.getElementById("sessions-list");
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    
    // الميزة 4: الوضع الليلي
    const themeBtn = document.getElementById("theme-btn");
    const isDark = localStorage.getItem("darkMode") === "true";
    if (isDark) document.body.classList.add("dark-mode");
    
    themeBtn.onclick = () => {
        document.body.classList.toggle("dark-mode");
        const darkModeEnabled = document.body.classList.contains("dark-mode");
        localStorage.setItem("darkMode", darkModeEnabled);
        themeBtn.innerHTML = darkModeEnabled ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    };

    // الميزة 5: تحميل المحادثة كصورة
    document.getElementById("download-btn").onclick = () => {
        const captureArea = document.getElementById("capture-area");
        html2canvas(captureArea, { scale: 2 }).then(canvas => {
            const link = document.createElement('a');
            link.download = 'ذكريات_أنوس_وحنان.png';
            link.href = canvas.toDataURL();
            link.click();
        });
    };

    // الميزة 2: تأثير القلوب (Easter Egg)
    function triggerHearts(text) {
        const keywords = ["بحبك", "بموت فيك", "عشقي", "حبيبي", "شوق", "قلبي"];
        if (keywords.some(word => text.includes(word))) {
            for (let i = 0; i < 25; i++) {
                let heart = document.createElement("div");
                heart.innerHTML = "❤️";
                heart.className = "heart-fall";
                heart.style.left = Math.random() * 100 + "vw";
                heart.style.animationDuration = (Math.random() * 3 + 2) + "s";
                heart.style.fontSize = (Math.random() * 1.5 + 1) + "rem";
                document.body.appendChild(heart);
                setTimeout(() => heart.remove(), 5000);
            }
        }
    }

    // الميزة 3: قارئ الصوت (Text to Speech)
    function speakText(text) {
        window.speechSynthesis.cancel(); // إيقاف أي صوت سابق
        const speech = new SpeechSynthesisUtterance(text);
        speech.lang = 'ar-SA'; // نطق عربي
        speech.rate = 0.9; // سرعة هادئة رومانسية
        window.speechSynthesis.speak(speech);
    }

    // إدارة الجلسات
    function loadSessions() {
        fetch("/api/sessions").then(res => res.json()).then(sessions => {
            sessionsList.innerHTML = "";
            sessions.forEach(session => {
                const li = document.createElement("li");
                
                const titleSpan = document.createElement("span");
                titleSpan.textContent = session.title;
                titleSpan.onclick = () => loadMessages(session.id, li);
                
                // الميزة 1: زر الحذف
                const deleteBtn = document.createElement("button");
                deleteBtn.className = "delete-btn";
                deleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
                deleteBtn.title = "مسح الذكرى";
                deleteBtn.onclick = (e) => {
                    e.stopPropagation();
                    if(confirm("متأكدة بدك تمسحي هالذكرى يا روحي؟ 🥺")) {
                        fetch(`/api/sessions/${session.id}`, { method: "DELETE" })
                        .then(() => {
                            if(currentSessionId === session.id) {
                                chatMessages.innerHTML = "";
                                currentSessionId = null;
                            }
                            loadSessions();
                        });
                    }
                };

                li.appendChild(titleSpan);
                li.appendChild(deleteBtn);
                sessionsList.appendChild(li);
            });
        });
    }

    document.getElementById("new-chat-btn").onclick = () => {
        fetch("/api/new_session", { method: "POST" }).then(res => res.json()).then(() => loadSessions());
    };

    function loadMessages(sessionId, liElement) {
        currentSessionId = sessionId;
        document.querySelectorAll("#sessions-list li").forEach(li => li.classList.remove("active"));
        if(liElement) liElement.classList.add("active");

        fetch(`/api/messages/${sessionId}`).then(res => res.json()).then(messages => {
            chatMessages.innerHTML = "";
            messages.forEach(msg => appendMessage(msg.sender, msg.text));
        });
    }

    function appendMessage(sender, text) {
        const div = document.createElement("div");
        div.className = `msg-bubble ${sender === 'Hanan' ? 'msg-user' : 'msg-bot'}`;
        div.textContent = text;
        
        // إضافة أيقونة الصوت لرسائل أنوس
        if (sender !== 'Hanan') {
            const ttsBtn = document.createElement("button");
            ttsBtn.className = "tts-btn";
            ttsBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i> اسمعي صوتي';
            ttsBtn.onclick = () => speakText(text);
            div.appendChild(ttsBtn);
        }

        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendMessage() {
        const text = userInput.value.trim();
        if (!text || !currentSessionId) return;

        triggerHearts(text); // فحص الكلمات الرومانسية قبل الإرسال
        appendMessage("Hanan", text);
        userInput.value = "";
        
        const typingId = "typing-" + Date.now();
        chatMessages.insertAdjacentHTML('beforeend', `<div class="typing-indicator" id="${typingId}"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`);
        chatMessages.style.display = "flex"; // Fix typing display
        document.getElementById(typingId).style.display = "flex";
        chatMessages.scrollTop = chatMessages.scrollHeight;

        fetch("/api/send_message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: currentSessionId, text: text })
        }).then(res => res.json()).then(data => {
            document.getElementById(typingId).remove();
            if (data.reply) appendMessage("AnosBot", data.reply);
        });
    }

    document.getElementById("send-btn").onclick = sendMessage;
    userInput.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });

    loadSessions();
});
