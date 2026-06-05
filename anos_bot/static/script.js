let currentSessionId = null;

// عناصر الواجهة الأساسية
const sidebar = document.getElementById('sidebar');
const toggleSidebar = document.getElementById('toggleSidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const sessionsList = document.getElementById('sessionsList');
const newChatBtn = document.getElementById('newChatBtn');
const messagesContainer = document.getElementById('messagesContainer');
const welcomeScreen = document.getElementById('welcomeScreen');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');

// التحكم في فتح وإغلاق المنيو في الجوال
toggleSidebar.addEventListener('click', () => sidebar.classList.toggle('active'));
sidebarOverlay.addEventListener('click', () => sidebar.classList.remove('active'));

// جلب كل المحادثات عند فتح الموقع أول مرة
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const sessions = await response.json();
        sessionsList.innerHTML = '';
        
        sessions.forEach(session => {
            const div = document.createElement('div');
            div.className = `session-item ${currentSessionId === session.id ? 'active' : ''}`;
            div.textContent = session.title;
            div.addEventListener('click', () => {
                selectSession(session.id);
                sidebar.classList.remove('active'); // إغلاق السايدبار بالجوال بعد الاختيار
            });
            sessionsList.appendChild(div);
        });
    } catch (err) {
        console.error("فشل في جلب المحادثات:", err);
    }
}

// إنشاء محادثة جديدة
newChatBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/new_session', { method: 'POST' });
        const newSession = await response.json();
        currentSessionId = newSession.id;
        await loadSessions();
        selectSession(newSession.id);
    } catch (err) {
        console.error("فشل في إنشاء محادثة جديدة:", err);
    }
});

// اختيار محادثة معينة وعرض رسائلها
async function selectSession(sessionId) {
    currentSessionId = sessionId;
    
    // تحديث الحالة النشطة في القائمة الجانبية
    document.querySelectorAll('.session-item').forEach(item => item.classList.remove('active'));
    loadSessions(); // لتحديث الكلاس النشط

    if (welcomeScreen) welcomeScreen.style.display = 'none';
    messagesContainer.innerHTML = ''; // تنظيف الشاشة للرسائل الجديدة

    try {
        const response = await fetch(`/api/messages/${sessionId}`);
        const messages = await response.json();
        
        messages.forEach(msg => {
            appendMessage(msg.sender === 'Hanan' ? 'user' : 'bot', msg.text);
        });
        scrollToBottom();
    } catch (err) {
        console.error("فشل في جلب الرسائل:", err);
    }
}

// إضافة فقاعة رسالة داخل صندوق الشات
function appendMessage(sender, text) {
    if (welcomeScreen) welcomeScreen.style.display = 'none';
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${sender}`;
    bubble.textContent = text;
    messagesContainer.appendChild(bubble);
    scrollToBottom();
}

// النزول التلقائي لأسفل الشات مع كل رسالة جديدة
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// إرسال الرسالة عبر الفورم
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // إذا لم تكن هناك محادثة مفتوحة، ننشئ واحدة تلقائياً أولاً
    if (!currentSessionId) {
        try {
            const response = await fetch('/api/new_session', { method: 'POST' });
            const newSession = await response.json();
            currentSessionId = newSession.id;
            await loadSessions();
        } catch (err) {
            console.error(err);
            return;
        }
    }

    // عرض رسالة المستخدم فوراً
    appendMessage('user', text);
    userInput.value = '';

    try {
        const response = await fetch('/api/send_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId, text: text })
        });
        const data = await response.json();
        
        // عرض رد البوت
        appendMessage('bot', data.reply);
    } catch (err) {
        console.error("خطأ أثناء إرسال الرسالة:", err);
        appendMessage('bot', "حدث خطأ ما في الاتصال بالسيرفر.");
    }
});

// تشغيل جلب المحادثات بمجرد تحميل الصفحة
window.addEventListener('DOMContentLoaded', loadSessions);