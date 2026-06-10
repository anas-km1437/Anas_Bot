document.addEventListener("DOMContentLoaded", () => {
    let currentSessionId = null;
    const sessionsList = document.getElementById("sessions-list");
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const themeBtn = document.getElementById("theme-btn");
    const newChatBtn = document.getElementById("new-chat-btn");

    const sidebar = document.getElementById("sidebar");
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const closeSidebarBtn = document.getElementById("close-sidebar-btn");
    const sidebarOverlay = document.getElementById("sidebar-overlay");

    const capsuleBtn = document.getElementById("love-capsule-btn");
    const capsuleModal = document.getElementById("capsule-modal");
    const closeModal = document.getElementById("close-modal");
    const capsuleText = document.getElementById("capsule-text");

    const myLoveMessages = [
        "أنتِ النور اللي ضوّى حياتي، وكل يوم معك هو أحلى يوم بعمري.",
        "لو جمعت كل كلمات الحب بالدنيا، ما توفي حق عيونك الحلوين.",
        "ضحكتك هي الأغنية المفضلة لقلبي، لا تحرميني منها أبداً.",
        "بحبك مش بس لأنك غالية، بحبك لأنك أقرب حد لروحي وتوأمي.",
        "وقت أكون معك، بنسى كل تعب الدنيا. أنتِ راحتي وأماني.",
        "بتعرفي إنك أحلى صدفة بحياتي؟ يا ريتني عرفتك من زمان.",
        "مهما بعدتنا المسافات أو الظروف، رح تضلي بقلبي ملكة متوجة.",
        "الله يخليلي إياكي وما يحرمني من هالصوت وهالحنية.",
        "أنا محظوظ جداً لأنك بحياتي، بحبك يا أغلى ما أملك.",
        "وجودك بيكفيني عن كل العالم، أنتِ عالمي كله."
    ];

    function handleResponse(response) {
        if (response.status === 401) {
            window.location.href = "/";
            throw new Error("Unauthorized");
        }
        return response.json();
    }

    function toggleSidebar(show) {
        if (show) {
            sidebar.classList.add("open");
            sidebarOverlay.classList.add("show");
        } else {
            sidebar.classList.remove("open");
            sidebarOverlay.classList.remove("show");
        }
    }

    if(mobileMenuBtn) mobileMenuBtn.onclick = () => toggleSidebar(true);
    if(closeSidebarBtn) closeSidebarBtn.onclick = () => toggleSidebar(false);
    if(sidebarOverlay) sidebarOverlay.onclick = () => toggleSidebar(false);

    const isDark = localStorage.getItem("darkMode") === "true";
    if (isDark) {
        document.body.classList.add("dark-mode");
        if(themeBtn) themeBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }
    
    if(themeBtn) {
        themeBtn.onclick = () => {
            document.body.classList.toggle("dark-mode");
            const darkModeEnabled = document.body.classList.contains("dark-mode");
            localStorage.setItem("darkMode", darkModeEnabled);
            themeBtn.innerHTML = darkModeEnabled ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
        };
    }

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

    if(capsuleBtn) {
        capsuleBtn.onclick = () => {
            const randomMsg = myLoveMessages[Math.floor(Math.random() * myLoveMessages.length)];
            capsuleText.textContent = randomMsg;
            capsuleModal.classList.add("show");
            triggerHearts(true);
        };
    }

    if(closeModal) {
        closeModal.onclick = () => capsuleModal.classList.remove("show");
        capsuleModal.onclick = (e) => {
            if (e.target === capsuleModal) capsuleModal.classList.remove("show");
        };
    }

    function loadSessions() {
        fetch("/api/sessions")
            .then(handleResponse)
            .then(sessions => {
                sessionsList.innerHTML = "";
                sessions.forEach((session, index) => {
                    const li = document.createElement("li");
                    
                    const titleSpan = document.createElement("span");
                    titleSpan.textContent = session.title;
                    titleSpan.onclick = () => {
                        loadMessages(session.id, li);
                        if (window.innerWidth <= 768) toggleSidebar(false);
                    };
                    
                    const deleteBtn = document.createElement("button");
                    deleteBtn.className = "delete-btn";
                    deleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
                    deleteBtn.onclick = (e) => {
                        e.stopPropagation();
                        if (confirm("متأكدة بدك تمسحي هالمحادثة يا روحي؟ 🥺")) {
                            fetch(`/api/sessions/${session.id}`, { method: "DELETE" })
                                .then(handleResponse)
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
            })
            .catch(err => console.log(err));
    }

    if(newChatBtn) {
        newChatBtn.onclick = () => {
            fetch("/api/new_session", { method: "POST" })
                .then(handleResponse)
                .then(data => {
                    currentSessionId = data.id;
                    chatMessages.innerHTML = "";
                    loadSessions();
                    if (window.innerWidth <= 768) toggleSidebar(false);
                })
                .catch(err => console.log(err));
        };
    }

    function loadMessages(sessionId, liElement) {
        currentSessionId = sessionId;
        document.querySelectorAll("#sessions-list li").forEach(li => li.classList.remove("active"));
        if (liElement) liElement.classList.add("active");

        fetch(`/api/messages/${sessionId}`)
            .then(handleResponse)
            .then(messages => {
                chatMessages.innerHTML = "";
                messages.forEach(msg => appendMessage(msg.sender, msg.text));
                scrollToBottom();
            })
            .catch(err => console.log(err));
    }

    function appendMessage(sender, text) {
        const div = document.createElement("div");
        div.className = `msg-bubble ${sender === 'Hanan' ? 'msg-user' : 'msg-bot'}`;
        
        const textSpan = document.createElement("span");
        textSpan.textContent = text;
        div.appendChild(textSpan);

        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function scrollToBottom() {
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 50);
    }

    function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;
        
        if (!currentSessionId) {
            alert("الرجاء إنشاء محادثة جديدة أولاً.");
            return;
        }

        triggerHearts(false, text);
        appendMessage("Hanan", text);
        userInput.value = "";
        
        const typingId = "typing-" + Date.now();
        const typingHTML = `<div class="typing-indicator" id="${typingId}"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
        chatMessages.insertAdjacentHTML('beforeend', typingHTML);
        scrollToBottom();

        fetch("/api/send_message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: currentSessionId, text: text })
        })
        .then(handleResponse)
        .then(data => {
            const indicator = document.getElementById(typingId);
            if (indicator) indicator.remove();
            
            if (data.reply) {
                appendMessage("AnosBot", data.reply);
            }
        })
        .catch(err => {
            if(err.message !== "Unauthorized") {
                const indicator = document.getElementById(typingId);
                if (indicator) indicator.remove();
                appendMessage("AnosBot", "يا روحي السيرفر مضغوط شوية، ثواني وعيدي الإرسال!");
            }
        });
    }

    if(sendBtn) sendBtn.onclick = sendMessage;
    if(userInput) {
        userInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    }

    if(document.getElementById("sessions-list")) {
        loadSessions();
    }
});
