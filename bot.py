import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

# Çevre değişkenlerinden anahtarları çek
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini istemcisini başlat
ai_client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selam! Ben senin yapay zeka asistanınım. İstediğin her şeyi sorabilirsin!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Kullanıcıya yazıyor simgesi göster
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Gemini modeline soruyu yönelt
        response = ai_client.models.generate_content(
            model = 'gemini-3.8-flash' ,
            contents=user_text,
        )
        reply = response.text or "Bir yanıt oluşturamadım."
    except Exception as e:
        reply = f"Hata oluştu: {str(e)}"
        
    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        print("HATA: TELEGRAM_BOT_TOKEN veya GEMINI_API_KEY eksik!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot 7/24 dinlemeye başladı...")
    app.run_polling()

if __name__ == "__main__":
    main()
