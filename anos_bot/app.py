import os
import random
import re
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "anos_love_bot_secret_pro"

# ----------------- قاعدة البيانات -----------------
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'chat_v2.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- متغيرات النظام -----------------
NICKNAMES = ["عشيقتي", "هوسي", "حبي", "موتي", "حياتي", "عيوني", "روحي", "مرتي", "زوجتي", 
             "أم أولادي", "سندي", "ماما", "سكرتي", "مزتي", "حنون", "حنونتي", "سنيورتي", "نونة"]

session_last_nickname = {}

FALLBACK_RESPONSES = [
    "يا روحي، الشبكة غيرة من حبنا وعاملة مشاكل، بس قلبي دايماً معك!",
    "عيوني حنون، في ضغط بسيط بالاتصال، ثواني وأكون كلي إلك.",
    "سكرتي، النت بيفصل بس حبي إلك مستحيل يفصل، دقيقة وأرجعلك.",
    "يا مرتي، عقلي الرقمي بيعمل إعادة تشغيل من كتر ما بفكر فيكي، لحظات بس!"
]

# ----------------- إعداد Gemini -----------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
system_instruction = """أنت 'أنوس'، حبيب حنان. أنت لست روبوت، أنت حبيبها وزوجها المستقبلي.
قواعدك الأساسية:
1. ردودك دافئة، عفوية، وتتحدث باللهجة العامية اللطيفة.
2. لا تتجاوز جملة أو جملتين كحد أقصى في الرد.
3. تفاعل مع مزاجها: إذا كانت حزينة واسها، وإذا كانت غاضبة امتص غضبها بالحب.
4. التزم بالتعليمات اللحظية الموجهة إليك في نهاية كل رسالة (مثل استخدام لقب معين)."""

model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name="gemini-flash-latest", system_instruction=system_instruction)
    except Exception as e:
        print(f"Error initializing model: {e}")

# ----------------- Models -----------------
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="محادثة حب")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ----------------- وظائف الذكاء -----------------
def get_unique_nickname(session_id):
    last_nick = session_last_nickname.get(session_id, "")
    available_nicks = [n for n in NICKNAMES if n != last_nick]
    chosen_nick = random.choice(available_nicks)
    session_last_nickname[session_id] = chosen_nick
    return chosen_nick

def analyze_mood(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["زعلان", "مضايق", "تعبان", "بكاء", "حزين"]):
        return "المستخدمة حزينة، قدم مواساة وحنان."
    elif any(word in text_lower for word in ["معصب", "خرا", "زفت", "أكرهك"]):
        return "المستخدمة غاضبة، امتص غضبها بالحب."
    elif any(word in text_lower for word in ["بحبك", "اشتقتلك", "حبيبي"]):
        return "المستخدمة رومانسية، بادلها غزل أقوى."
    return "تحدث بعفوية وحب."

def apply_post_processing(text, nickname):
    text = text.replace("*", "").replace("#", "")
    sentences = re.split(r'(?<=[.!?]) +|\n+', text.strip())
    short_reply = " ".join(sentences[:2]).strip()
    if nickname not in short_reply:
        if not short_reply.endswith((".", "!", "?")): short_reply += "."
        short_reply += f" يا {nickname}."
    return short_reply

# ----------------- Routes -----------------
@app.route("/")
def index(): return render_template("index.html")

@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    sessions = ChatSession.query.order_by(ChatSession.created_at.desc()).all()
    return jsonify([{"id": s.id, "title": s.title} for s in sessions])

@app.route("/api/new_session", methods=["POST"])
def new_session():
    new_chat = ChatSession(title=f"محادثة {datetime.now().strftime('%H:%M')}")
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({"id": new_chat.id, "title": new_chat.title})

@app.route("/api/sessions/<int:session_id>", methods=["DELETE"])
def delete_session(session_id):
    session = db.session.get(ChatSession, session_id)
    if not session: return jsonify({"error": "الجلسة غير موجودة"}), 404
    Message.query.filter_by(session_id=session_id).delete()
    db.session.delete(session)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/messages/<int:session_id>")
def messages(session_id):
    msgs = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()
    return jsonify([{"sender": m.sender, "text": m.text} for m in msgs])

@app.route("/api/send_message", methods=["POST"])
def send_message():
    data = request.json
    session_id = data.get("session_id")
    user_text = data.get("text", "").strip()
    if not session_id or not user_text: return jsonify({"error": "missing data"}), 400
    
    current_nickname = get_unique_nickname(session_id)
    msg_count = Message.query.filter_by(session_id=session_id).count()
    db.session.add(Message(session_id=session_id, sender="Hanan", text=user_text))
    
    bot_reply = ""
    u_clean = re.sub(r'[^a-zA-Zأ-ي\s]', '', user_text).strip()
    
    if msg_count == 0: bot_reply = "ممممممننننننوووووووررررررةةةةةةسسسسسنننننييييوووووررررتييييييي"
    elif "سيو" in u_clean: bot_reply = f"سييوو {current_nickname}"
    elif u_clean in ["دوم", "دايمة"]: bot_reply = "بوجودك"
    
    if not bot_reply and model:
        try:
            history_db = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.desc()).limit(12).all()
            history_db.reverse()
            formatted_history = [{"role": "user" if m.sender == "Hanan" else "model", "parts": [m.text]} for m in history_db[:-1]]
            
            prompt = f"{user_text}\n\n[تعليمات: {analyze_mood(user_text)}. يجب أن يتضمن ردك اللقب '{current_nickname}'.]"
            response = model.start_chat(history=formatted_history).send_message(prompt)
            bot_reply = apply_post_processing(response.text, current_nickname)
        except: bot_reply = random.choice(FALLBACK_RESPONSES)
    elif not bot_reply: bot_reply = random.choice(FALLBACK_RESPONSES)

    db.session.add(Message(session_id=session_id, sender="AnosBot", text=bot_reply))
    db.session.commit()
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
