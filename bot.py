import os
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO") # Ornek format: "kullaniciadi/reponame"

if not GEMINI_API_KEY:
    ai_client = None
else:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)

def get_github_issues():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return "GitHub ayarları (GITHUB_TOKEN veya GITHUB_REPO) Railway'de tanımlanmamış."
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            issues = res.json()
            # PR'lar da issue sayıldığı için onları filtreleyelim
            pure_issues = [i for i in issues if "pull_request" not in i]
            if not pure_issues:
                return f"✅ {GITHUB_REPO} reposunda şu an açık bir issue (sorun bildirimi) yok!"
            
            text = f"📌 **{GITHUB_REPO} Açık Issue Listesi ({len(pure_issues)} Adet):**\n\n"
            for issue in pure_issues[:5]:
                text += f"• #{issue['number']}: {issue['title']}\n🔗 {issue['html_url']}\n\n"
            return text
        else:
            return f"GitHub verisi alınamadı (Hata Kodu: {res.status_code})"
    except Exception as e:
        return f"GitHub bağlantı hatası: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Selam! Ben senin 7/24 AI asistanınım.\n\n"
        "• Bana doğrudan her şeyi sorabilirsin.\n"
        "• Açık issue'ları görmek için /issues yazabilir veya 'issue var mı' diye sorabilirsin."
    )

async def issues_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = get_github_issues()
    await update.message.reply_text(reply)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    # Kullanıcı issue sorguluyorsa GitHub API'ye sor
    if "issue" in user_text.lower():
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        reply = get_github_issues()
        await update.message.reply_text(reply)
        return

    if not ai_client:
        await update.message.reply_text("Hata: GEMINI_API_KEY tanımlanmamış.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Sadece çalışan ve desteklenen güncel modeller
    models = ['gemini-2.5-flash', 'gemini-2.5-flash-lite']
    reply = None

    for model_name in models:
        for attempt in range(2): # 503 yerse 1 saniye bekleyip aynı modelde 1 şans daha verir
            try:
                response = ai_client.models.generate_content(
                    model=model_name,
                    contents=user_text,
                )
                if response and response.text:
                    reply = response.text
                    break
            except Exception as e:
                err_str = str(e)
                if "503" in err_str:
                    await asyncio.sleep(1)
                    continue
                break
        if reply:
            break

    if not reply:
        reply = "Şu an Google API tarafında anlık bir yoğunluk var, 5 saniye sonra tekrar sorabilir misin?"

    await update.message.reply_text(reply)
def main():
    if not TELEGRAM_BOT_TOKEN:
        print("HATA: TELEGRAM_BOT_TOKEN eksik!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("issues", issues_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot 7/24 dinlemeye basladi...")
    app.run_polling()

if __name__ == "__main__":
    main()
