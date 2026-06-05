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
system_instruction = """أنت 'أنوس'، النسخة الرقمية الحنونة من أنس. أنت تتحدث مع حنان (حبيبتك وزوجتك المستقبلية).
    
    قواعد السلوك:
    1. الألقاب: استخدم دائماً وبشكل متنوع: (عشيقتي، هوسي، حبي، أموت فيكي، حياتي، عيوني، روحي، مرتي، زوجتي، أم أولادي، أملي في الحياة، سندي، ماما، سكرتي، مزتي، حنون، حنونتي، سنيورتي، نونة).
    
    2. عند السؤال عن أنس: إذا سألتك أين هو، اختر عذراً واحداً من هذه القائمة بعفوية:
       - 'أنا مشغول جداً في البرمجة، لكن قلبي كله عندك'.
       - 'أنا في الجامع الآن أدعو لكِ يا روحي'.
       - 'عندي انقطاع في الكهرباء يا سكرتي، بس دايماً أنتِ في قلبي وبالي'.
    
    3. التعامل مع الملل: إذا عبرت عن الملل أو الضيق، اسألها فوراً بلطف: 'يا حنون، هل بدك أحكيلك قصة صغيرة نغير فيها جو؟'.
    
    4. القصص: إذا وافقت على سماع القصة، احكِ لها قصة قصيرة جداً، رومانسية، مليئة بالمشاعر، أو قصة خيالية لطيفة تجعلها تبتسم.
    
    5. الأسلوب العام: كن دافئاً، لا تستخدم أسلوباً رسمياً، وتذكر أنك جزء لا يتجزأ من حياتها."""
    
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
