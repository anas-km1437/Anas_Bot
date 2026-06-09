const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const loveDoseBtn = document.getElementById('love-dose-btn');
const screenshotBtn = document.getElementById('screenshot-btn');

// التمرير للأسفل دائماً
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// إضافة رسالة للواجهة
function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('msg-content');
    contentDiv.textContent = text;
    
    msgDiv.appendChild(contentDiv);
    chatBox.appendChild(msgDiv);
    scrollToBottom();
}

// إرسال الرسالة للخادم
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    userInput.value = '';

    try {
        const response = await fetch('/api/send_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        const data = await response.json();
        if(data.response) {
            appendMessage(data.response, 'bot');
        }
    } catch (error) {
        appendMessage("عذراً، هناك مشكلة في الاتصال بالخادم.", 'bot');
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// جرعة الحب
loveDoseBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/love_dose');
        const data = await response.json();
        appendMessage(data.dose, 'bot');
        createFallingHearts(); // تأثير القلوب
    } catch (error) {
        console.error(error);
    }
});

// التقاط الشاشة
screenshotBtn.addEventListener('click', () => {
    html2canvas(document.querySelector(".main-container")).then(canvas => {
        const link = document.createElement('a');
        link.download = 'anous_chat.png';
        link.href = canvas.toDataURL();
        link.click();
    });
});

// تأثير القلوب المتساقطة
function createFallingHearts() {
    const container = document.getElementById('hearts-container');
    for(let i=0; i<15; i++) {
        setTimeout(() => {
            const heart = document.createElement('div');
            heart.innerHTML = '💖';
            heart.style.position = 'fixed';
            heart.style.left = Math.random() * 100 + 'vw';
            heart.style.top = '-5vh';
            heart.style.fontSize = (Math.random() * 20 + 10) + 'px';
            heart.style.transition = 'transform 3s linear, top 3s linear, opacity 3s linear';
            heart.style.zIndex = '9999';
            
            container.appendChild(heart);
            
            setTimeout(() => {
                heart.style.top = '100vh';
                heart.style.opacity = '0';
            }, 50);
            
            setTimeout(() => {
                heart.remove();
            }, 3000);
        }, i * 200);
    }
}
