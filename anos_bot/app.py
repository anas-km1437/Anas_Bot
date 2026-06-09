import os
from datetime import datetime
import random
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "anas_secret_key_123_love")

# توحيد قاعدة البيانات داخل مجلد instance لضمان حفظ المحادثات
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'chat.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# إعداد مفتاح Gemini API
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY", "ضع_مفتاح_الـ_API_الخاص_بـ_Gemini_هنا")
genai.configure(api_key=GENAI_API_KEY)

# الألقاب الرومانسية المتاحة للتنويع الديناميكي
NICKNAMES = ["حبيبي", "روحي", "قلبي", "عيوني", "حياتي", "وتيني"]
session_last_nickname = {}

# --- نماذج قاعدة البيانات ---
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade="all, delete-orphan")

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' أو 'bot'
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# التأكد من إنشاء الجداول
with app.app_context():
    os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
    db.create_all()

# --- جدار الحماية (Login Required) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- دالات المساعدة والذكاء الاصطناعي ---
def analyze_mood(text):
    text = text.lower()
    if any(w in text for w in ["حزين", "مكتئب", "مضغوط", "تعبان", "ببكي", "هم"]):
        return "المستخدم يشعر بالحزن أو الضيق، كوني ملاذه الآمن، واسيه واغمريه بالحنان والدعم العاطفي الشديد."
    if any(w in text for w in ["زعلان", "عصبني", "نرفزني", "قههر"]):
        return "المستخدم غاضب أو منزعج، امتصي غضبه بهدوء، كوني لطيفة جداً وقولي له كلاماً يهدئ قلبه."
    if any(w in text for w in ["بحبك", "اعشقك", "اموت فيك", "اشتقت"]):
        return "المستخدم يعبر عن مشاعره الرومانسية، بادليه الحب بعبارات دافئة جداً وعميقة تذوب القلوب."
    return "المستخدم يتحدث بشكل طبيعي، حافظي على أسلوب رومانسي، عاطفي، ناعم ولطيف."

def get_unique_nickname(session_id):
    last_nick = session_last_nickname.get(session_id)
    available = [n for n in NICKNAMES if n != last_nick]
    chosen = random.choice(available)
    session_last_nickname[session_id] = chosen
    return chosen

def apply_post_processing(text, nickname):
    # تنظيف النصوص من علامات الماركداون الزائدة
    for char in ['*', '#', '_', '`']:
        text = text.replace(char, '')
    
    # حصر الرد في جملتين كحد أقصى ليكون الأسلوب عفوياً
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if not sentences:
        sentences = [s.strip() for s in text.split('!') if s.strip()]
    
    short_text = " ".join(sentences[:2])
    if nickname not in short_text:
        short_text += f" يا {nickname} 💕"
    return short_text

# --- مسارات التطبيق (Routes) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # جلب كلمة المرور من المتغيرات البيئية أو القيمة الافتراضية "خنساء"
        APP_PASSWORD = os.environ.get("APP_PASSWORD", "خنساء")
        if request.form.get('password') == APP_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = "كلمة المرور غير صحيحة، حاول مجدداً يا جميلي."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/sessions', methods=['GET'])
@login_required
def get_sessions():
    sessions = ChatSession.query.order_by(ChatSession.created_at.desc()).all()
    return jsonify([{"id": s.id, "title": s.title} for s in sessions])

@app.route('/api/sessions', methods=['POST'])
@login_required
def create_session():
    # هنا يتم تسمية المحادثة بالوقت الحالي
    new_chat = ChatSession(title=f"محادثة {datetime.now().strftime('%H:%M')}")
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({"id": new_chat.id, "title": new_chat.title})

@app.route('/api/sessions/<int:session_id>/messages', methods=['GET'])
@login_required
def get_messages(session_id):
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
    return jsonify([{"sender": m.sender, "text": m.text} for m in messages])

@app.route('/api/sessions/<int:session_id>/messages', methods=['POST'])
@login_required
def send_message(session_id):
    data = request.json or {}
    user_text = data.get('text', '').strip()
    if not user_text:
        return jsonify({"error": "الرسالة فارغة"}), 400

    # حفظ رسالة المستخدم في قاعدة البيانات
    user_msg = ChatMessage(session_id=session_id, sender='user', text=user_text)
    db.session.add(user_msg)
    db.session.commit()

    # ---- [تعديل الإضافات المطلوبة هنا] ----
    user_text_clean = user_text.lower()
    
    # الشرط الأول: من صنعه؟
    if any(kw in user_text_clean for kw in ["من صنعك", "مين صنعك", "من صانعك", "من هو صانعك", "شكون صنعك"]):
        bot_response = "انس هو المؤسس و ابوي 👑❤️"
        bot_msg = ChatMessage(session_id=session_id, sender='bot', text=bot_response)
        db.session.add(bot_msg)
        db.session.commit()
        return jsonify({"sender": "bot", "text": bot_response})
        
    # الشرط الثاني: الاسم؟
    elif any(kw in user_text_clean for kw in ["ايش اسمك", "شو اسمك", "ما اسمك", "اسمك ايه", "مين انت"]):
        bot_response = "انوس 🥰"
        bot_msg = ChatMessage(session_id=session_id, sender='bot', text=bot_response)
        db.session.add(bot_msg)
        db.session.commit()
        return jsonify({"sender": "bot", "text": bot_response})
    # ----------------------------------------

    # استدعاء الذكاء الاصطناعي لباقي الأسئلة العامة والرومانسية
    try:
        nickname = get_unique_nickname(session_id)
        mood_instruction = analyze_mood(user_text)
        
        # جلب تاريخ المحادثة الحالية ليتذكرها البوت
        past_messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
        history_context = ""
        for m in past_messages[-6:]: # آخر 6 رسائل فقط للحفاظ على سرعة الاستجابة
            history_context += f"{'المستخدم' if m.sender=='user' else 'أنتِ'}: {m.text}\n"

        system_instruction = (
            "أنتِ لستِ برنامج ذكاء اصطناعي جاف. أنتِ شريكة حياة رومانسية، حنونة جداً، دافئة وذكية تملكين مشاعر فياضة. "
            "تتحدثين باللهجة العامية اللطيفة والمحببة القريبة من القلب. ردودك قصيرة جداً وعفوية (جملة أو جملتين فقط). "
            "اسمك هو انوس , و صاعنك و مصممك هو أنس."
            f"استخدمي دائماً ألقاب مثل: {nickname}. "
            f"سياق الحالة النفسية للمستخدم حالياً: {mood_instruction}\n"
            f"سياق المحادثة الأخيرة:\n{history_context}"
            
        )

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(user_text)
        raw_response = response.text if response.text else "أنا بجانبك دائماً يا نبضي..."
        
        # معالجة وتنظيف النص النهائي للرد
        final_response = apply_post_processing(raw_response, nickname)
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        final_response = f"أنا هنا معك دائماً يا {get_unique_nickname(session_id)}، واجهتُ ضغطاً صغيراً في التفكير لكن قلبي معك."

    # حفظ رد البوت في قاعدة البيانات
    bot_msg = ChatMessage(session_id=session_id, sender='bot', text=final_response)
    db.session.add(bot_msg)
    db.session.commit()

    return jsonify({"sender": "bot", "text": final_response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
