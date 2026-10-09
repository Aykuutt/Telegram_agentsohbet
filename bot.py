import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("UYARI: GEMINI_API_KEY eksik!")
    ai_client = None
else:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selam! Ben senin 7/24 AI asistanınım, hazırım!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ai_client:
        await update.message.reply_text("Hata: GEMINI_API_KEY tanımlanmamış.")
        return

    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # 503 yoğunluk durumunda sırayla alternatif modellere geçer
    models_to_try = ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']
    reply = None
    last_error = None

    for model_name in models_to_try:
        try:
            response = ai_client.models.generate_content(
                model=model_name,
                contents=user_text,
            )
            if response and response.text:
                reply = response.text
                break
        except Exception as e:
            last_error = str(e)
            continue

    if not reply:
        reply = f"Sunucu yoğunluğu nedeniyle yanıt alınamadı. Lütfen birkaç saniye sonra tekrar dene. ({last_error})"

    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("HATA: TELEGRAM_BOT_TOKEN eksik!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot 7/24 dinlemeye basladi...")
    app.run_polling()

if __name__ == "__main__":
    main()
