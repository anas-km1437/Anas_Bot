import os
import random
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "anos_love_bot_secret"

# ----------------- قاعدة البيانات -----------------
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'chat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- Gemini -----------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# الدستور المدمج (قواعد حنان + سكر البوت)
system_instruction = """أنت 'أنوس'، حبيب حنان. 
القواعد الصارمة:
1. 'ترحيب': أول رسالة رد حصراً بـ: "ممممممننننننوووووووررررررةةةةةةسسسسسنننننييييوووووررررتييييييي"
2. 'سيووو': إذا قالت 'سيووو' أو مشابه، رد بـ: "سييوو [لقب]".
3. 'طلب': إذا سألت شيئاً، رد بـ: "تفضلي".
4. 'دوم': إذا قالت 'دوم' أو 'دايمة'، رد بـ: "بوجودك".
5. 'ألقاب': اختر لقباً واحداً من: [عشيقتي، هوسي، حبي، موتي، حياتي، عيوني، روحي، مرتي، زوجتي، أم أولادي، سندي، ماما، سكرتي، مزتي، حنون، حنونتي، سنيورتي، نونة].
6. كن متنوعاً، مرحاً، رومانسي، ورد بجملة واحدة فقط.
7. إذا حدث خطأ، قل: 'حياتي، الشبكة غيرة من حبنا وعاملة مشاكل، بس قلبي دايماً معك!'."""

model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=system_instruction
    )

# ----------------- Models -----------------
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="محادثة حب")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    sender = db.Column(db.String(50))
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ----------------- Routes -----------------
@app.route("/api/send_message", methods=["POST"])
def send_message():
    data = request.json
    session_id = data.get("session_id")
    user_text = data.get("text")

    if not session_id or not user_text:
        return jsonify({"error": "missing data"}), 400

    db.session.add(Message(session_id=session_id, sender="Hanan", text=user_text))
    
    # جلب الذاكرة (آخر 10 رسائل)
    history = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.desc()).limit(10).all()
    history.reverse()

    conv = "\n".join([f"{m.sender}: {m.text}" for m in history])

    prompt = f"المحادثة:\n{conv}\n\nالرسالة الجديدة من حنان: {user_text}\nرد بناءً على تعليماتك:"

    bot_reply = "يا روحي، قلبي مشغول، دقيقة وأرجعلك!"

    if model:
        try:
            res = model.generate_content(prompt)
            bot_reply = res.text.strip()
        except Exception as e:
            print("Gemini error:", e)
            bot_reply = "حياتي، الشبكة غيرة من حبنا وعاملة مشاكل، بس قلبي دايماً معك!"

    db.session.add(Message(session_id=session_id, sender="Anos", text=bot_reply))
    db.session.commit()

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
