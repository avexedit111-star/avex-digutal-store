import logging
import os
import sys
import threading
import hashlib
import io
import firebase_admin
from firebase_admin import credentials, firestore
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from PIL import Image
import pytesseract

# ==========================================
# 1. YOUR CONFIGURATION (EDIT THESE LINES)
# ==========================================
BOT_TOKEN = "8672250869:AAERnPrc2Gg2xS4H_VxoVlnAds_JX6wGqOY"
TELEBIRR_NUMBER = "0935630202"
TELEBIRR_NAME = "Mekasha"
YOUR_TELEGRAM_USERNAME = "@Madara_912" 
ADMIN_ID = 8327762718 # REPLACE WITH YOUR REAL ID FROM @userinfobot

# ==========================================
# 2. INITIALIZE FIREBASE
# ==========================================
try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase connected successfully!")
except Exception as e:
    print(f"Failed to connect to Firebase: {e}")
    db = None

# ==========================================
# 3. DUMMY WEB SERVER (For Render)
# ==========================================
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

# ==========================================
# 4. BOT LOGIC
# ==========================================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Buy PFP Pack ($12)", callback_data="buy_pfp")],
        [InlineKeyboardButton("Buy Anime Edit ($25)", callback_data="buy_edit")],
        [InlineKeyboardButton("Buy CC Pack ($8)", callback_data="buy_cc")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to AVEX! 🚀\n\nChoose a product below to purchase.", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "buy_pfp": product, price = "Neon Cyber PFP Pack", "$12.00"
    elif query.data == "buy_edit": product, price = "Cyberpunk Anime Edit", "$25.00"
    elif query.data == "buy_cc": product, price = "Cinematic Teal & Orange", "$8.00"
    else: return

    message = (
        f"🛒 **{product}**\nPrice: **{price}**\n\n"
        f"Send {price} to Telebirr: `{TELEBIRR_NUMBER}` (Name: {TELEBIRR_NAME}).\n"
        f"👇 **After paying, send the screenshot here with the word 'PAID' in the caption.**"
    )
    await query.message.reply_text(message, parse_mode='Markdown')

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    caption = update.message.caption
    
    # Filter 1: Check Caption
    if not caption or "PAID" not in caption.upper():
        await update.message.reply_text("⚠️ **Rejected:** You must type 'PAID' in the caption.")
        return

    if not db:
        await update.message.reply_text("⚠️ Database error. Please contact admin.")
        return

    # Filter 2: Duplicate Check (Hash)
    file_id = update.message.photo[-1].file_id
    new_file = await context.bot.get_file(file_id)
    image_bytes = await new_file.download_as_bytearray()
    image_hash = hashlib.sha256(image_bytes).hexdigest()

    doc_ref = db.collection('used_receipts').document(image_hash)
    if doc_ref.get().exists:
        await update.message.reply_text("🚨 **Scam Alert:** This exact screenshot has already been used.")
        return

    # Filter 3: Image Recognition (OCR)
    try:
        image = Image.open(io.BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image).lower()
        keywords = ["telebirr", "transaction", "successful", "birr"]
        if not any(word in extracted_text for word in keywords):
            await update.message.reply_text("❌ **Rejected:** This image does not look like a valid Telebirr receipt.")
            return
    except Exception as e:
        print(f"OCR Error: {e}")
        await update.message.reply_text("❌ **Rejected:** Could not read the image.")
        return

    # Passed all filters
    doc_ref.set({'used_by': update.effective_user.id, 'timestamp': firestore.SERVER_TIMESTAMP})
    await update.message.reply_text("✅ Screenshot verified and received! Admin will process your order shortly.")
    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)

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
