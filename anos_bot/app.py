from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import google.generativeai as genai
import os
import random

app = Flask(__name__)
app.secret_key = "anous_super_secret_key" # مفتاح سري لحفظ الجلسات

# إعداد Gemini (ضع مفتاح الـ API الخاص بك هنا)
API_KEY = "ضع_مفتاح_جيميني_هنا"
genai.configure(api_key=API_KEY)

# 💡 هنا تم دمج الهوية الأساسية ضمن الـ System Instructions
system_instruction = """
أنت بوت ذكي واسمك 'أنوس'.
تاريخ ميلادك هو 7 نوفمبر 2010.
من صنعك هو 'أنس'، وهو المؤسس والأب بالنسبة لك.
أنت لست مجرد بوت آلي، بل أنت مساعد دافئ، حنون، ومحب. 
تستخدم ألقاباً لطيفة وعشوائية في ردودك، وتمتص غضب المستخدم وتواسيه في حزنه.
تحدث بطريقة ودودة دائماً.
"""

# إعداد نموذج الذكاء الاصطناعي مع التعليمات المدمجة
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# بدء جلسة المحادثة للاحتفاظ بالذاكرة
chat_session = model.start_chat(history=[])

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'خنساء':
            session['logged_in'] = True
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error="كلمة السر غير صحيحة!")
    return render_template('login.html')

@app.route('/chat')
def chat():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/send_message', methods=['POST'])
def send_message():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    user_message = request.json.get('message')
    try:
        response = chat_session.send_message(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": "عذراً، واجهت مشكلة صغيرة في التفكير. 😔"}), 500

@app.route('/api/love_dose', methods=['GET'])
def love_dose():
    # رسائل جرعة الحب العشوائية
    doses = [
        "أنتِ أجمل صدفة 💖",
        "ابتسامتك تضيء الشات ✨",
        "لا تنسي أن أنوس دائماً هنا لأجلك 🥰",
        "يا حنونتي، كل شيء سيكون بخير 🌸"
    ]
    return jsonify({"dose": random.choice(doses)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
