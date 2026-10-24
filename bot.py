import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# 1. PUT YOUR BOT TOKEN HERE
BOT_TOKEN = "8672250869:AAERnPrc2Gg2xS4H_VxoVlnAds_JX6wGqOY"

# 2. YOUR DETAILS
TELEBIRR_NUMBER = "0935630202"
TELEBIRR_NAME = "Mekasha"
YOUR_TELEGRAM_USERNAME = "https://t.me/Madara_912" # Replace with your username (e.g. @mekasha)

# 3. YOUR ADMIN ID (So the bot forwards screenshots to YOU)
# Message @userinfobot on Telegram to get your ID (e.g., 123456789)
ADMIN_ID = 8327762718 

# 4. DUMMY WEB SERVER (Fixes Render Timeout)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"AVEX Bot is running!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# 5. BOT LOGIC
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Buy PFP Pack ($12)", callback_data="buy_pfp")],
        [InlineKeyboardButton("Buy Anime Edit ($25)", callback_data="buy_edit")],
        [InlineKeyboardButton("Buy CC Pack ($8)", callback_data="buy_cc")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to AVEX! 🚀\n\n"
        "Choose a product below to purchase.",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "buy_pfp":
        product, price = "Neon Cyber PFP Pack", "$12.00"
    elif query.data == "buy_edit":
        product, price = "Cyberpunk Anime Edit", "$25.00"
    elif query.data == "buy_cc":
        product, price = "Cinematic Teal & Orange", "$8.00"
    else:
        return

    message = (
        f"🛒 **{product}**\n"
        f"Price: **{price}**\n\n"
        f"🇪🇹 **Local (Ethiopia):**\n"
        f"Send {price} to Telebirr: `{TELEBIRR_NUMBER}` (Name: {TELEBIRR_NAME}).\n\n"
        f"🌍 **International:**\n"
        f"Message me at {YOUR_TELEGRAM_USERNAME} to pay via PayPal.\n\n"
        f"👇 **After paying, send the screenshot here.**"
    )
    
    await query.message.reply_text(message, parse_mode='Markdown')

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This handles when a user sends a photo (screenshot)
    if update.message.photo:
        await update.message.reply_text(
            "✅ Screenshot received! \n\n"
            "I will verify the payment and send your Redeem Code shortly."
        )
        
        # Forward the screenshot to you (the Admin)
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))

    print("Bot is running...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
