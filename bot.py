import logging
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes

# 1. PUT YOUR BOT TOKEN HERE (From BotFather)
BOT_TOKEN = "8672250869:AAERnPrc2Gg2xS4H_VxoVlnAds_JX6wGqOY"

# 2. PUT YOUR SECRET REDEEM CODES HERE
# These MUST match the codes in your index.html file!
REDEEM_CODES = {
    "PFP": "AVEX-PFP-001",
    "EDIT": "AVEX-EDIT-002",
    "CC": "AVEX-CC-003"
}

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
        "Choose a product below to purchase using Telegram Stars.\n"
        "Once paid, you will receive a Redeem Code to unlock your files on our website.",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "buy_pfp":
        await context.bot.send_invoice(
            chat_id=query.message.chat_id, title="Neon Cyber PFP Pack", description="10 high-res avatars.",
            payload="pfp_payload", provider_token="", currency="XTR", prices=[LabeledPrice(label="PFP", amount=100)]
        )
    elif query.data == "buy_edit":
        await context.bot.send_invoice(
            chat_id=query.message.chat_id, title="Cyberpunk Anime Edit", description="15-second 4K edit.",
            payload="edit_payload", provider_token="", currency="XTR", prices=[LabeledPrice(label="Edit", amount=200)]
        )
    elif query.data == "buy_cc":
        await context.bot.send_invoice(
            chat_id=query.message.chat_id, title="Cinematic Teal & Orange", description="Hollywood-grade LUT.",
            payload="cc_payload", provider_token="", currency="XTR", prices=[LabeledPrice(label="CC", amount=80)]
        )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True) # Automatically approve

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    
    if payload == "pfp_payload":
        code = REDEEM_CODES["PFP"]
        await update.message.reply_text(f"✅ Payment Received!\n\nYour Redeem Code is: `{code}`\n\nGo to https://avexedit111-star.github.io/avex-digital-store/ and click 'Redeem' in the top menu.", parse_mode='Markdown')
    elif payload == "edit_payload":
        code = REDEEM_CODES["EDIT"]
        await update.message.reply_text(f"✅ Payment Received!\n\nYour Redeem Code is: `{code}`\n\nGo to https://avexedit111-star.github.io/avex-digital-store/ and click 'Redeem' in the top menu.", parse_mode='Markdown')
    elif payload == "cc_payload":
        code = REDEEM_CODES["CC"]
        await update.message.reply_text(f"✅ Payment Received!\n\nYour Redeem Code is: `{code}`\n\nGo to https://avexedit111-star.github.io/avex-digital-store/ and click 'Redeem' in the top menu.", parse_mode='Markdown')

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
