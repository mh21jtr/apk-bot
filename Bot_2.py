import os
import zipfile
import shutil
import telebot
import google.generativeai as genai

# إعداد التوكن والمفتاح الجديد المحدث
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8750826069:AAFHmF1iwof2jem1mhBRwB8mGuLFBTcLDZo")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6I7ABz23QDRcaWuDI4JmrT5plnIs2U0sFiUAvmmx7x1sQ")

genai.configure(api_key=GEMINI_API_KEY)
model  genai.GenerativeModel('gemini-2.5-flash')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = "🔥 أهلاً بك يا بطل في باتشر الـ APK والملفات الذكي عبر الاستضافة السحابية! أرسل لي ملف APK أو كود وسأقوم بتعديله بالكامل."
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['document'])
def handle_apk_patcher(message):
    try:
        file_name = message.document.file_name
        
        if not file_name.endswith('.apk'):
            bot.reply_to(message, "⚠️ يا بطل، من فضلك أرسل ملف بصيغة `.apk` لتعديله.")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(file_name, 'wb') as f:
            f.write(downloaded_file)
            
        user_prompt = message.caption if message.caption else "قم بفحص وتعديل هذا التطبيق وتحسينه بالكامل."
        msg = bot.reply_to(message, "🧠 جاري فك ضغط الـ APK ومعالجة الأكواد بالذكاء الاصطناعي...")
        
        extract_dir = "extracted_apk_ai"
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)
        
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(('.html', '.js', '.json', '.xml', '.txt', '.smali')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as rf:
                            content = rf.read()
                            
                        if len(content) > 15000:
                            continue
                            
                        ai_response = model.generate_content(
                            f"أنت خبير هندسة عكسية وتعديل تطبيقات أندرويد. طلب المستخدم: '{user_prompt}'. عدل هذا الملف وأرجع الكود كاملاً فقط بدون أي شروحات إضافية:\n\n{content}"
                        )
                        
                        if ai_response and ai_response.text:
                            new_content = ai_response.text.strip()
                            if new_content.startswith("```"):
                                new_content = "\n".join(new_content.split("\n")[1:-1])
                                
                            with open(file_path, 'w', encoding='utf-8') as wf:
                                wf.write(new_content)
                    except Exception:
                        continue
                        
        output_apk = "ai_patched_" + file_name
        with zipfile.ZipFile(output_apk, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for foldername, subfolders, filenames in os.walk(extract_dir):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, extract_dir)
                    zip_out.write(filepath, arcname)
                    
        with open(output_apk, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"✅ تم تعديل الـ APK بنجاح عبر الاستضافة السحابية بالمفتاح الجديد!\nالطلب: `{user_prompt}`")
            
        shutil.rmtree(extract_dir)
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة الـ APK:\n`{str(e)}`")

print("🤖 بوت باتشر الـ APK السحابي يعمل الآن بالمفتاح الجديد...")
bot.infinity_polling()
                          
