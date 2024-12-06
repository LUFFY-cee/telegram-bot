import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from transformers import pipeline
from diffusers import StableDiffusionPipeline
import torch
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Telegram bot token is not set. Please provide a valid token in your .env file.")

# Load AI models
text_model = pipeline("text2text-generation", model="google/flan-t5-xxl")
image_model = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-1.0-inpainting-0.1")
image_model.to("cuda" if torch.cuda.is_available() else "cpu")

# Bot functions
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا! أرسل نصًا، اطلب صورة، كود Python، ملف نصي، أو تطبيق وسأساعدك.")

def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()

    # Handle "صورة"
    if "صورة" in user_input:
        prompt = user_input.replace("صورة", "").strip()
        update.message.reply_text("جارٍ إنشاء الصورة...")
        try:
            image = image_model(prompt).images[0]
            file_path = "output_image.png"
            image.save(file_path)
            update.message.reply_photo(photo=open(file_path, "rb"))
            os.remove(file_path)  # Clean up
        except Exception as e:
            update.message.reply_text(f"حدث خطأ أثناء إنشاء الصورة: {e}")

    # Handle "كود" or "Python"
    elif "كود" in user_input or "python" in user_input:
        prompt = f"Write a Python code to: {user_input.replace('كود', '').strip()}"
        try:
            response = text_model(prompt, max_length=200, num_return_sequences=1)
            code = response[0]['generated_text']
            file_name = "generated_code.py"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(code)
            update.message.reply_text("تم إنشاء الكود وحفظه في ملف Python.")
            update.message.reply_document(document=open(file_name, "rb"))
            os.remove(file_name)  # Clean up
        except Exception as e:
            update.message.reply_text(f"حدث خطأ أثناء إنشاء الكود: {e}")

    # Handle "إنشاء ملف"
    elif "إنشاء ملف" in user_input:
        file_name = "output.txt"
        content = user_input.replace("إنشاء ملف", "").strip()
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(content)
            update.message.reply_text(f"تم إنشاء الملف النصي: {file_name}")
            update.message.reply_document(document=open(file_name, "rb"))
            os.remove(file_name)  # Clean up
        except Exception as e:
            update.message.reply_text(f"حدث خطأ أثناء إنشاء الملف: {e}")

    # Handle other inputs
    else:
        try:
            response = text_model(user_input, max_length=200, num_return_sequences=1)
            update.message.reply_text(response[0]['generated_text'])
        except Exception as e:
            update.message.reply_text(f"حدث خطأ أثناء معالجة النص: {e}")

# Set up the bot
def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
