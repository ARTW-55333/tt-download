import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    filters
)
from config import BOT_TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Welcome to TikTok Downloader Bot*\n\n"
        "📥 Send me any TikTok link and I’ll give you:\n"
        "• HD Video (No Watermark)\n"
        "• Normal Video (No Watermark)\n"
        "• MP3 Audio Only\n\n"
        "Paste your TikTok URL below 👇"
    )

    await update.message.reply_markdown(text)


# Handle incoming TikTok URLs
async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "tiktok.com" not in url:
        await update.message.reply_text("❌ Send a valid TikTok URL.")
        return

    waiting = await update.message.reply_text("⏳ Fetching video info...")

    api = f"https://www.tikwm.com/api/?url={url}"

    try:
        data = requests.get(api).json()

        if data["code"] != 0:
            await waiting.edit_text("❌ Could not fetch video.")
            return

        context.user_data["video_data"] = data["data"]

        # Buttons for resolution + mp3
        keyboard = [
            [InlineKeyboardButton("🎥 HD (No Watermark)", callback_data="hd")],
            [InlineKeyboardButton("🎥 Normal (No Watermark)", callback_data="normal")],
            [InlineKeyboardButton("🔊 MP3 (Audio Only)", callback_data="mp3")]
        ]

        markup = InlineKeyboardMarkup(keyboard)

        await waiting.edit_text(
            "Choose download format 👇",
            reply_markup=markup
        )

    except:
        await waiting.edit_text("❌ Error. Try again later.")


# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = context.user_data.get("video_data")

    if not data:
        await query.message.edit_text("❌ Session expired. Send the link again.")
        return

    choice = query.data

    if choice == "hd":
        file_url = data["hdplay"] if data["hdplay"] else data["play"]
        caption = "🎥 HD Video (No Watermark)"
    elif choice == "normal":
        file_url = data["play"]
        caption = "🎥 Normal Quality (No Watermark)"
    elif choice == "mp3":
        file_url = data["music"]
        caption = "🔊 MP3 Audio"
    else:
        return

    await query.edit_message_text("⬆️ Uploading your file...")

    try:
        if choice == "mp3":
            await query.message.reply_audio(audio=file_url, caption=caption)
        else:
            await query.message.reply_video(video=file_url, caption=caption)

    except Exception as e:
        await query.message.reply_text("❌ Error while sending file. Try another link.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
