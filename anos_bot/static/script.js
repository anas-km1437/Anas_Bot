let currentSessionId = null;

const loveQuotes = [
    "أنت لست جزءاً مني، أنت كلي وعالمي الصغير. 🌸",
    "كل نبضة في قلبي تخبرك كم أنا محظوظ بوجودك. ✨",
    "لا يهمني هذا العالم، ما دمت ممسكاً بيدي. 🥺",
    "ضحكتك هي الموسيقى المفضلة لقلبي دائماً. 💕",
    "وجودك بجانبي يجعل كل شيء صعب يبدو سهلاً وجميلاً."
];

document.addEventListener("DOMContentLoaded", () => {
    // تفعيل الثيم المحفوظ بالمتصفح
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    
    loadSessions();
});

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
}

function loadSessions() {
    fetch('/api/sessions')
        .then(res => res.json())
        .then(sessions => {
            const list = document.getElementById("sessionsList");
            list.innerHTML = "";
            sessions.forEach(s => {
                const item = document.createElement("div");
                item.classList.add("session-item");
                if(s.id === currentSessionId) item.classList.add("active");
                item.innerText = s.title;
                item.onclick = () => selectSession(s.id, s.title);
                list.appendChild(item);
            });
        });
}

function createNewSession() {
    fetch('/api/sessions', { method: 'POST' })
        .then(res => res.json())
        .then(session => {
            currentSessionId = session.id;
            loadSessions();
            selectSession(session.id, session.title);
        });
}

function selectSession(id, title) {
    currentSessionId = id;
    document.getElementById("chatTitle").innerText = title;
    
    // تمييز العنصر النشط
    document.querySelectorAll('.session-item').forEach(item => item.classList.remove('active'));
    loadMessages(id);
}

function loadMessages(sessionId) {
    fetch(`/api/sessions/${sessionId}/messages`)
        .then(res => res.json())
        .then(messages => {
            const container = document.getElementById("messagesContainer");
            container.innerHTML = "";
            
            messages.forEach(m => {
                appendMessage(m.sender, m.text);
            });
            scrollToBottom();
        });
}

function appendMessage(sender, text) {
    const container = document.getElementById("messagesContainer");
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    msgDiv.innerText = text;
    container.appendChild(msgDiv);
    scrollToBottom();
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

function sendMessage() {
    const input = document.getElementById("userInput");
    const text = input.value.trim();
    if (!text) return;

    if (!currentSessionId) {
        alert("من فضلك اختر محادثة أولاً أو اضغط على محادثة جديدة! 💕");
        return;
    }

    appendMessage('user', text);
    input.value = "";

    showTypingIndicator();

    fetch(`/api/sessions/${currentSessionId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
    })
    .then(res => res.json())
    .then(data => {
        removeTypingIndicator();
        appendMessage('bot', data.text);
    })
    .catch(() => {
        removeTypingIndicator();
    });
}

function showTypingIndicator() {
    removeTypingIndicator();
    const container = document.getElementById("messagesContainer");
    const indicator = document.createElement("div");
    indicator.id = "typingIndicator";
    indicator.classList.add("typing-indicator");
    indicator.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;
    container.appendChild(indicator);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById("typingIndicator");
    if (indicator) indicator.remove();
}

function scrollToBottom() {
    const container = document.getElementById("messagesContainer");
    container.scrollTop = container.scrollHeight;
}

// كبسولة الحب واحتفالية تساقط القلوب
function openLoveCapsule() {
    const randomQuote = loveQuotes[Math.floor(Math.random() * loveQuotes.length)];
    appendMessage('bot', randomQuote);
    
    // إطلاق تأثير القلوب المتساقطة
    for (let i = 0; i < 15; i++) {
        setTimeout(createHeart, i * 150);
    }
}

function createHeart() {
    const heart = document.createElement("div");
    heart.classList.add("heart-fall");
    heart.innerText = ["❤️", "💖", "💝", "💕", "🌸"][Math.floor(Math.random() * 5)];
    heart.style.left = Math.random() * 100 + "vw";
    heart.style.animationDuration = Math.random() * 2 + 2 + "s";
    document.body.appendChild(heart);
    
    setTimeout(() => { heart.remove(); }, 4000);
}

// التقاط لقطة شاشة للمحادثة وتحميلها كصورة للذكريات
function captureChat() {
    const container = document.getElementById("messagesContainer");
    html2canvas(container, { backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--bg-primary').trim() })
    .then(canvas => {
        const link = document.createElement('a');
        link.download = `ذكرياتنا_${new Date().toLocaleDateString()}.png`;
        link.href = canvas.toDataURL();
        link.click();
    });
}