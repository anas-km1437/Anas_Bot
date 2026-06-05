import os
import random
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "anos_bot_secret"

# ----------------- DATABASE -----------------
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'chat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- GEMINI -----------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

system_instruction = """
أنت بوت دردشة خيالي اسمه "أنوس".

معلومات:
- شخصية افتراضية
- تاريخ الميلاد: 7 نوفمبر 2010
- تتحدث بالعربية العامية
- ردودك قصيرة (جملة أو جملتين)
- لا تدّعي أنك إنسان حقيقي

قواعد:
- اختر لقب واحد فقط من:
[صديقي، صاحبي، نجم، بطل، أسطورة، زعيم]
- كن طبيعي، عفوي، غير مكرر
"""

model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=system_instruction
    )

# ----------------- DATABASE MODELS -----------------
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="محادثة أنوس")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    sender = db.Column(db.String(50))
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ----------------- MOODS SYSTEM -----------------
def detect_mood(text):
    text = text.lower()

    if any(w in text for w in ["زعلان", "حزين", "مضايق"]):
        return "حزين"
    if any(w in text for w in ["حب", "اشتقت", "غالي"]):
        return "رومانسي"
    if any(w in text for w in ["ضحك", "هههه", "مزح"]):
        return "مرح"
    if any(w in text for w in ["ليش", "كيف", "شنو"]):
        return "فضولي"
    return "عادي"

def mood_style(mood):
    styles = {
        "حزين": "تكلم بلطف وهدوء وواسي المستخدم",
        "رومانسي": "كن لطيف وعاطفي",
        "مرح": "امزح بشكل خفيف",
        "فضولي": "اسأل سؤال بسيط",
        "عادي": "رد طبيعي"
    }
    return styles.get(mood, "رد طبيعي")

# ----------------- ROUTES -----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/send_message", methods=["POST"])
def send_message():
    data = request.json
    session_id = data.get("session_id")
    user_text = data.get("text")

    if not session_id or not user_text:
        return jsonify({"error": "missing data"}), 400

    # حفظ رسالة المستخدم
    db.session.add(Message(session_id=session_id, sender="Hanan", text=user_text))

    # ----------------- MEMORY -----------------
    history = Message.query.filter_by(session_id=session_id)\
        .order_by(Message.timestamp.desc())\
        .limit(15).all()

    history.reverse()

    conversation = ""
    for m in history:
        role = "User" if m.sender == "Hanan" else "Anos"
        conversation += f"{role}: {m.text}\n"

    # ----------------- MOOD -----------------
    mood = detect_mood(user_text)
    style = mood_style(mood)

    # ----------------- PROMPT -----------------
    prompt = f"""
أنت أنوس، بوت دردشة خيالي.

المزاج الحالي: {mood}
أسلوب الرد: {style}

قواعد:
- جملة أو جملتين فقط
- لقب واحد فقط
- لا تكرر نفس الرد

المحادثة السابقة:
{conversation}

رسالة المستخدم:
{user_text}

رد أنوس:
"""

    bot_reply = "أنا مشغول الآن، رجع لي بعد شوي"

    if model:
        try:
            res = model.generate_content(prompt)
            bot_reply = res.text.strip()

            # منع الإطالة
            if len(bot_reply) > 140:
                bot_reply = bot_reply.split(".")[0]

        except Exception as e:
            print("Gemini error:", e)
            bot_reply = "صار ضغط بسيط، بس أنا معك يا صديقي"

    # حفظ رد البوت
    db.session.add(Message(session_id=session_id, sender="Anos", text=bot_reply))
    db.session.commit()

    return jsonify({
        "reply": bot_reply,
        "mood": mood
    })

# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(debug=True)
