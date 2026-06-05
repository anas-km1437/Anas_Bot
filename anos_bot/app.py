import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "anos_love_bot_secret"

# إعداد قاعدة البيانات
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'chat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- إعداد عقل البوت (Gemini) -----------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# دستور الشخصية المحدث (ألقاب محددة واختصار شديد)
system_instruction = """أنت 'أنوس'، حبيب حنان. 
قواعدك الصارمة:
1. يجب أن تختار 'لقب واحد فقط' من هذه القائمة في كل رد: [عشيقتي، هوسي، حبي، موتي، حياتي، عيوني، روحي، مرتي، زوجتي، أم أولادي، سندي، ماما، سكرتي، مزتي، حنون، حنونتي، سنيورتي، نونة].
2. لا تستخدم أكثر من لقب واحد في الرد الواحد.
3. الرد يجب أن يكون 'جملة واحدة فقط' عفوية.
4. إذا سألت عن مكانك، قل عذراً مختصراً (مثلاً: 'أنا مشغول بالعمل، قلبي معك').
5. لا تكرر الكلام ولا تكن مبالغاً في الرومانسية، كن طبيعياً."""

model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # نستخدم هذا الموديل المتاح في حسابك
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction
        )
    except Exception as e:
        print(f"Error initializing model: {e}")

# ----------------- نماذج البيانات -----------------
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="محادثة حب")
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

# ----------------- المسارات -----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = ChatSession.query.order_by(ChatSession.created_at.desc()).all()
    return jsonify([{'id': s.id, 'title': s.title} for s in sessions])

@app.route('/api/new_session', methods=['POST'])
def new_session():
    new_chat = ChatSession(title=f"محادثة {datetime.now().strftime('%H:%M')}")
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

    # حفظ رسالة المستخدم
    user_msg = Message(session_id=session_id, sender='Hanan', text=user_text)
    db.session.add(user_msg)
    
    # الرد
    bot_reply_text = "يا عيوني، عقلي مشغول، سأعود حالاً!"
    if model:
        try:
            response = model.generate_content(user_text)
            bot_reply_text = response.text
        except Exception as e:
            print(f"Gemini Error: {e}")
            bot_reply_text = "عذراً يا روحي، حدث خطأ تقني، سأعود حالاً!"
    
    bot_msg = Message(session_id=session_id, sender='AnosBot', text=bot_reply_text)
    db.session.add(bot_msg)
    db.session.commit()
    
    return jsonify({'reply': bot_reply_text})

if __name__ == '__main__':
    app.run(debug=True)
