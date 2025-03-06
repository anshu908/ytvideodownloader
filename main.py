import os
import logging
import yt_dlp
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import uvicorn

# Replace with your Telegram Bot Token
TELEGRAM_BOT_TOKEN = "7923532245:AAEU6PMcm_ImVuELVoWV4H5iA2Qn0Fxxtyg"

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()

# Directory to store downloaded videos
DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Send me a YouTube video link, and I'll download it for you!")

async def download_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Please send a valid YouTube video link!")
        return

    await update.message.reply_text("Downloading the video... Please wait.")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info).replace(".webm", ".mp4")

        await update.message.reply_text("Download complete! Uploading video...")

        with open(video_filename, "rb") as video:
            await update.message.reply_video(video)

        os.remove(video_filename)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def run_telegram_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("Bot is running...")
    app.run_polling()

# Route for Koyeb to check the server status
@app.get("/")
def home():
    return {"status": "running", "message": "YouTube Downloader Bot is online!"}

# Run Telegram bot in background
import threading
threading.Thread(target=run_telegram_bot, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
