import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "anos_love_bot_secret"

# تحديد المسار المطلق لضمان عمل قاعدة البيانات على Render بدون أخطاء صلاحيات
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'chat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- نماذج قاعدة البيانات -----------------

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="محادثة جديدة")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='session', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)  # 'Hanan' أو 'AnosBot'
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# إنشاء الجداول تلقائياً داخل البيئة الصحيحة
with app.app_context():
    db.create_all()

# ----------------- مسارات الموقع (Routes) -----------------

@app.route('/')
def index():
    return render_template('index.html')

# جلب كل المحادثات للقائمة الجانبية
@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = ChatSession.query.order_by(ChatSession.created_at.desc()).all()
    return jsonify([{'id': s.id, 'title': s.title} for s in sessions])

# إنشاء محادثة جديدة
@app.route('/api/new_session', methods=['POST'])
def new_session():
    new_chat = ChatSession(title=f"محادثة {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({'id': new_chat.id, 'title': new_chat.title})

# جلب رسائل محادثة معينة
@app.route('/api/messages/<int:session_id>', methods=['GET'])
def get_messages(session_id):
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()
    return jsonify([{'sender': m.sender, 'text': m.text} for m in messages])

# استقبال الرسائل والرد المبدئي
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
    
    # 2. رد البوت المؤقت (بيتطور لاحقاً إلى AI بكامل أسلوبك)
    bot_reply_text = f"أنا نسخة أنوس البرمجية، استلمت رسالتكِ الجميلة: ({user_text})، أنس مشغول شوي وبيرجع لكِ فوراً أول ما يخلص!"
    
    # 3. حفظ رد البوت
    bot_msg = Message(session_id=session_id, sender='AnosBot', text=bot_reply_text)
    db.session.add(bot_msg)
    
    db.session.commit()

    return jsonify({'reply': bot_reply_text})

if __name__ == '__main__':
    app.run(debug=True)
