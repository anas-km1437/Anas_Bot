document.addEventListener("DOMContentLoaded", () => {
    let currentSessionId = null;
    const sessionsList = document.getElementById("sessions-list");
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const themeBtn = document.getElementById("theme-btn");
    const downloadBtn = document.getElementById("download-btn");
    const newChatBtn = document.getElementById("new-chat-btn");

    // عناصر جرعة الحب
    const capsuleBtn = document.getElementById("love-capsule-btn");
    const capsuleModal = document.getElementById("capsule-modal");
    const closeModal = document.getElementById("close-modal");
    const capsuleText = document.getElementById("capsule-text");

    // رسائل جرعة الحب (أضف وعدّل كما تريد هنا)
    const myLoveMessages = [
        "أنتِ النور اللي ضوّى حياتي، وكل يوم معك هو أحلى يوم بعمري.",
        "لو جمعت كل كلمات الحب بالدنيا، ما توفي حق عيونك الحلوين.",
        "ضحكتك هي الأغنية المفضلة لقلبي، لا تحرميني منها أبداً.",
        "بحبك مش بس لأنك حبيبتي، بحبك لأنك أقرب حد لروحي وتوأمي.",
        "وقت أكون معك، بنسى كل تعب الدنيا. أنتِ راحتي وأماني.",
        "بتعرفي إنك أحلى صدفة بحياتي؟ يا ريتني عرفتك من زمان.",
        "مهما بعدتنا المسافات أو الظروف، رح تضلي بقلبي ملكة متوجة.",
        "الله يخليلي إياكي وما يحرمني من هالصوت وهالحنية.",
        "أنا محظوظ جداً لأنك بحياتي، بحبك يا أغلى ما أملك.",
        "وجودك بيكفيني عن كل العالم، أنتِ عالمي كله."
    ];

    // الميزة 4: إدارة الوضع الليلي
    const isDark = localStorage.getItem("darkMode") === "true";
    if (isDark) {
        document.body.classList.add("dark-mode");
        themeBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }
    
    themeBtn.onclick = () => {
        document.body.classList.toggle("dark-mode");
        const darkModeEnabled = document.body.classList.contains("dark-mode");
        localStorage.setItem("darkMode", darkModeEnabled);
        themeBtn.innerHTML = darkModeEnabled ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    };

    // الميزة 5: تصدير الشات كـصورة PNG
    downloadBtn.onclick = () => {
        html2canvas(chatMessages, { scale: 2, backgroundColor: null }).then(canvas => {
            const link = document.createElement('a');
            link.download = `ذكريات_حب_${Date.now()}.png`;
            link.href = canvas.toDataURL();
            link.click();
        });
    };

    // تأثير تساقط القلوب السحري
    function triggerHearts(force = false, text = "") {
        const keywords = ["بحبك", "بموت فيك", "عشقي", "حبيبي", "شوق", "قلبي", "اشتقتلك"];
        if (force || keywords.some(word => text.includes(word))) {
            for (let i = 0; i < 30; i++) {
                let heart = document.createElement("div");
                heart.innerHTML = "❤️";
                heart.className = "heart-fall";
                heart.style.left = Math.random() * 100 + "vw";
                heart.style.animationDuration = (Math.random() * 2 + 2) + "s";
                heart.style.fontSize = (Math.random() * 1.5 + 1) + "rem";
                document.body.appendChild(heart);
                setTimeout(() => heart.remove(), 4000);
            }
        }
    }

    // فتح شاشة جرعة الحب
    capsuleBtn.onclick = () => {
        const randomMsg = myLoveMessages[Math.floor(Math.random() * myLoveMessages.length)];
        capsuleText.textContent = randomMsg;
        capsuleModal.classList.add("show");
        triggerHearts(true); // تشغيل القلوب إجبارياً عند فتح الجرعة
    };

    // إغلاق شاشة جرعة الحب
    closeModal.onclick = () => capsuleModal.classList.remove("show");
    capsuleModal.onclick = (e) => {
        if (e.target === capsuleModal) capsuleModal.classList.remove("show");
    };

    // ميزة القراءة الصوتية
    function speakText(text) {
        window.speechSynthesis.cancel();
        const speech = new SpeechSynthesisUtterance(text);
        speech.lang = 'ar-SA';
        speech.rate = 0.95;
        window.speechSynthesis.speak(speech);
    }

    // إدارة الجلسات
    function loadSessions() {
        fetch("/api/sessions")
            .then(res => res.json())
            .then(sessions => {
                sessionsList.innerHTML = "";
                sessions.forEach((session, index) => {
                    const li = document.createElement("li");
                    
                    const titleSpan = document.createElement("span");
                    titleSpan.textContent = session.title;
                    titleSpan.onclick = () => loadMessages(session.id, li);
                    
                    const deleteBtn = document.createElement("button");
                    deleteBtn.className = "delete-btn";
                    deleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
                    deleteBtn.title = "حذف هذه الذكرى";
                    deleteBtn.onclick = (e) => {
                        e.stopPropagation();
                        if (confirm("متأكدة بدك تمسحي هالمحادثة يا روحي؟ 🥺")) {
                            fetch(`/api/sessions/${session.id}`, { method: "DELETE" })
                                .then(() => {
                                    if (currentSessionId === session.id) {
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

                    if (!currentSessionId && index === 0) {
                        loadMessages(session.id, li);
                    }
                });
            });
    }

    newChatBtn.onclick = () => {
        fetch("/api/new_session", { method: "POST" })
            .then(res => res.json())
            .then(data => {
                currentSessionId = data.id;
                chatMessages.innerHTML = "";
                loadSessions();
            });
    };

    function loadMessages(sessionId, liElement) {
        currentSessionId = sessionId;
        document.querySelectorAll("#sessions-list li").forEach(li => li.classList.remove("active"));
        if (liElement) liElement.classList.add("active");

        fetch(`/api/messages/${sessionId}`)
            .then(res => res.json())
            .then(messages => {
                chatMessages.innerHTML = "";
                messages.forEach(msg => appendMessage(msg.sender, msg.text));
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });
    }

    function appendMessage(sender, text) {
        const div = document.createElement("div");
        div.className = `msg-bubble ${sender === 'Hanan' ? 'msg-user' : 'msg-bot'}`;
        
        const textSpan = document.createElement("span");
        textSpan.textContent = text;
        div.appendChild(textSpan);
        
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
        if (!text) return;
        
        if (!currentSessionId) {
            alert("الرجاء إنشاء محادثة جديدة أولاً أو اختيار محادثة نشطة من القائمة الجانبية.");
            return;
        }

        triggerHearts(false, text);
        appendMessage("Hanan", text);
        userInput.value = "";
        
        const typingId = "typing-" + Date.now();
        const typingHTML = `<div class="typing-indicator" id="${typingId}" style="display: flex;"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
        chatMessages.insertAdjacentHTML('beforeend', typingHTML);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        fetch("/api/send_message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: currentSessionId, text: text })
        })
        .then(res => res.json())
        .then(data => {
            const indicator = document.getElementById(typingId);
            if (indicator) indicator.remove();
            
            if (data.reply) {
                appendMessage("AnosBot", data.reply);
            }
        })
        .catch(err => {
            const indicator = document.getElementById(typingId);
            if (indicator) indicator.remove();
            appendMessage("AnosBot", "يا روحي السيرفر مضغوط شوية، ثواني وعيدي الإرسال!");
            console.error(err);
        });
    }

    sendBtn.onclick = sendMessage;
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    loadSessions();
});
