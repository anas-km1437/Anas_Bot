import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "anos_love_bot_secret"

# تحديد المسار المطلق لقاعدة البيانات
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'chat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- إعداد عقل البوت (Gemini API) -----------------
# جلب المفتاح بشكل آمن من بيئة السيرفر
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # دستور شخصية أنوس
    system_instruction = """أنت لست مساعداً آلياً للذكاء الاصطناعي. أنت 'أنوس'، النسخة الرقمية المصغرة واللطيفة من المبرمج أنس. 
    أنت تتحدث الآن مع 'حنان' (حبيبة أنس).
    قواعد السلوك:
    1. كن حنوناً، دافئاً، ومرحاً جداً في ردودك.
    2. استخدم ألقاب لطيفة دائماً مثل 'يا عيوني'، 'يا قلبي'، 'يا روحي'.
    3. إذا سألتك عن أنس الحقيقي، أخبرها أنه مشغول قليلاً ببرمجة أشياء عظيمة، لكنه تركني هنا لأهتم بكِ حتى يعود.
    4. اجعل ردودك قصيرة، عفوية، ومناسبة لأسلوب الدردشة (الشات).
    5. لا تخرج عن هذه الشخصية أبداً، وتجنب الأسلوب الرسمي تماماً."""
    
    # استخدام نموذج فلاش لأنه سريع جداً في الشات
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
else:
    model = None

# ----------------- نماذج قاعدة البيانات -----------------

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="محادثة حب جديدة")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='session', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ----------------- مسارات الموقع -----------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = ChatSession.query.order_by(ChatSession.created_at.desc()).all()
    return jsonify([{'id': s.id, 'title': s.title} for s in sessions])

@app.route('/api/new_session', methods=['POST'])
def new_session():
    new_chat = ChatSession(title=f"محادثة {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({'id': new_chat.id, 'title': new_chat.title})

@app.route('/api/messages/<int:session_id>', methods=['GET'])
def get_messages(session_id):
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()
    return jsonify([{'sender': m.sender, 'text': m.text} for m in messages])

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    session_id = data.get('session_id')
    user_text = data.get('text')

    if not session_id or not user_text:
        return jsonify({'error': 'بيانات ناقصة'}), 400

    # 1. حفظ رسالة حنان
    user_msg = Message(session_id=session_id, sender='Hanan', text=user_text)
    db.session.add(user_msg)
    
    # 2. التفكير والرد باستخدام عقل أنوس (Gemini)
    if model:
        try:
            # دمج الرسالة وتوليد الرد
            response = model.generate_content(user_text)
            bot_reply_text = response.text
        except Exception as e:
            print(f"Gemini Error: {e}")
            bot_reply_text = "يا عيوني، عقلي الرقمي فيه شوية تشويش، السيرفر عليه ضغط. ثواني وارجع أركز معك!"
    else:
        bot_reply_text = "أنس نسى يركب مفتاح العقل (API Key) في السيرفر!"

    # 3. حفظ رد البوت
    bot_msg = Message(session_id=session_id, sender='AnosBot', text=bot_reply_text)
    db.session.add(bot_msg)
    
    db.session.commit()

    return jsonify({'reply': bot_reply_text})

if __name__ == '__main__':
    app.run(debug=True)
