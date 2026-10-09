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

async def start(update: Update, context: Update):
    await update.message.reply_text("Selam! Ben senin 7/24 AI asistanınım, hazırım!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ai_client:
        await update.message.reply_text("Hata: GEMINI_API_KEY tanımlanmamış.")
        return

    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Doğrudan güncel model çağrısı
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
        )
        reply = response.text or "Yanıt üretilemedi."
    except Exception as e:
        reply = f"[SÜRÜM V2 HATASI]: {str(e)}"
        
    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("HATA: TELEGRAM_BOT_TOKEN eksik!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot dinlemeye basladi...")
    app.run_polling()

if __name__ == "__main__":
    main()
