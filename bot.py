from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from transformers import pipeline
from diffusers import StableDiffusionPipeline
import torch
import requests

# تحميل النماذج
text_model = pipeline("text2text-generation", model="google/flan-t5-xxl")
video_model = pipeline("text-to-video", model="Tencent/HunyuanVideo")
image_model = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-1.0-inpainting-0.1")
image_model.to("cuda")  # نقل النموذج إلى GPU إذا كان متاحًا

# وظائف البوت
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا! أرسل نصًا، اطلب فيديو، صورة، كود Python، ملف نصي، أو تطبيق وسأساعدك.")

def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()

    # إذا كان النص يحتوي على كلمة "فيديو"
    if "فيديو" in user_input:
        prompt = user_input.replace("فيديو", "").strip()
        update.message.reply_text("جارٍ إنشاء الفيديو...")
        video = video_model(prompt)
        video.save("output_video.mp4")
        update.message.reply_video(video=open("output_video.mp4", "rb"))

    # إذا كان النص يحتوي على كلمة "صورة"
    elif "صورة" in user_input:
        prompt = user_input.replace("صورة", "").strip()
        update.message.reply_text("جارٍ إنشاء الصورة...")
        image = image_model(prompt).images[0]
        image.save("output_image.png")
        update.message.reply_photo(photo=open("output_image.png", "rb"))

    # إذا كان النص يحتوي على "كود" أو "python"
    elif "كود" in user_input or "python" in user_input:
        prompt = f"Write a Python code to: {user_input.replace('كود', '').strip()}"
        response = text_model(prompt, max_length=200, num_return_sequences=1)
        code = response[0]['generated_text']
        file_name = "generated_code.py"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)
        update.message.reply_text("تم إنشاء الكود وحفظه في ملف Python.")
        update.message.reply_document(document=open(file_name, "rb"))

    # إذا كان النص يحتوي على "إنشاء ملف"
    elif "إنشاء ملف" in user_input:
        file_name = "output.txt"  # اسم الملف الافتراضي
        content = user_input.replace("إنشاء ملف", "").strip()  # محتوى الملف
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        update.message.reply_text(f"تم إنشاء الملف النصي: {file_name}")
        update.message.reply_document(document=open(file_name, "rb"))

    # إذا كان النص يحتوي على "تحميل تطبيق" أو "لعبة"
    elif "تحميل" in user_input or "لعبة" in user_input or "تطبيق" in user_input:
        query = user_input.replace("تحميل", "").replace("لعبة", "").replace("تطبيق", "").strip()
        update.message.reply_text(f"جارٍ البحث عن ملف: {query}...")
        # مثال: يمكنك تحسين البحث بدمج API خارجي لجلب الملفات أو الروابط
        # هنا يتم إرسال رابط افتراضي
        file_url = "https://example.com/download_sample_file"  # رابط وهمي
        file_name = query.replace(" ", "_") + ".apk"  # مثال لتسمية الملف
        response = requests.get(file_url)
        with open(file_name, "wb") as f:
            f.write(response.content)
        update.message.reply_text(f"تم تنزيل الملف: {file_name}")
        update.message.reply_document(document=open(file_name, "rb"))

    else:
        response = text_model(user_input, max_length=200, num_return_sequences=1)
        update.message.reply_text(response[0]['generated_text'])

# إعداد البوت
def main():
    TOKEN = "7476380097:AAH2xAG8ynSC-wXiRSTx9i4IUihQIg0cT-o"  # ضع توكن البوت هنا
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()