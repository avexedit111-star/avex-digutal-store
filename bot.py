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
YOUR_TELEGRAM_USERNAME = "@Madara_912" 

# 3. YOUR ADMIN ID
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
        f"👇 **After paying, send the screenshot here with a caption containing the word 'PAID'.**\n"
        f"*(Example: '12 USD PAID')*"
    )
    
    await query.message.reply_text(message, parse_mode='Markdown')

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        caption = update.message.caption
        
        # THE FILTER: Check if the caption exists and has the required word
        if not caption or "PAID" not in caption.upper():
            await update.message.reply_text(
                "⚠️ **Action Rejected:**\n\n"
                "You must type the word **PAID** in the text box along with the amount before sending the screenshot.\n"
                "*(Example: 12 USD PAID)*"
            )
            return # Stop right here, do not forward

        # If it passes the filter, forward to you
        await update.message.reply_text(
            f"✅ Screenshot received with note: '{caption}'\n\n"
            "I will verify the payment and send your download link shortly."
        )
        
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
