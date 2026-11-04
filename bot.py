import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from google import genai
from google.genai import types

# Configuração de Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Chaves de Acesso via Variáveis de Ambiente
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9109101364:AAGErsnxhTa0abSyNe7G_gjLGhbMLcR2be4")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6JhqFe4sJ6ToqquSt3beGvUV1IvKBMTGnVmeTb6k0Et1w")

# Inicializa o cliente oficial do Google GenAI
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Mensagem de Boas-Vindas
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛡️ **Global Anti-Scam Shield (Powered by Gemini AI)**\n\n"
        "Welcome! I use advanced AI to analyze suspicious texts, links, and scams in real-time.\n"
        "Bem-vindo! Uso IA avançada para analisar textos suspeitos, links e golpes em tempo real.\n\n"
        "📥 **How to use / Como usar:**\n"
        "Forward any suspicious message or link to me!"
    )
    
    keyboard = [
        [InlineKeyboardButton("⭐ Go Premium / Assinar Premium", callback_data='premium_info')],
        [InlineKeyboardButton("❓ Help / Ajuda", callback_data='help_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

# Motor de Análise com Google Gemini
def analyze_with_gemini(text: str) -> str:
    prompt = f"""
    You are an expert cybersecurity and anti-fraud AI assistant. Analyze the following message or text forwarded by a user to check if it's a scam, phishing, social engineering, or a legitimate communication.
    
    Message to analyze: "{text}"
    
    Provide your response structured clearly with:
    1. Status: [🚨 HIGH RISK / GOLPE CONFIRMADO, ⚠️ WARNING / RISCO MÉDIO, or 🟢 SAFE / SEGURO]
    2. Analysis: Why is it dangerous or safe? (Explain briefly in English and Portuguese).
    3. Action: Clear recommended action for the user.
    """
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logging.error(f"Erro ao chamar o Gemini: {e}")
        return "⚠️ Erro temporário ao analisar com a IA. Por favor, tente novamente em instantes."

# Processador de Mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or update.message.caption or ""
    
    if not user_text:
        await update.message.reply_text("Please send a text message or link to analyze.")
        return

    # Mensagem de carregamento
    processing_msg = await update.message.reply_text("🔍 Analyzing with Gemini AI / Analisando com IA...")

    # Análise real via Gemini
    ai_verdict = analyze_with_gemini(user_text)
    
    keyboard = [
        [InlineKeyboardButton("🛡️ Protect a Relative / Proteger um Familiar", callback_data='premium_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=processing_msg.message_id,
        text=ai_verdict,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# Tratamento de Botões
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'premium_info':
        premium_text = (
            "💎 **Premium Plan / Plano Premium**\n\n"
            "• Unlimited AI checks / Checagens ilimitadas por IA\n"
            "• Real-time image & audio scan / Varredura de imagem e áudio\n"
            "• Family Protection Alerts / Alertas de Proteção Familiar\n\n"
            "Price: **$2.99 / month**"
        )
        await query.message.reply_text(premium_text, parse_mode='Markdown')
    elif query.data == 'help_info':
        await query.message.reply_text("Forward any message directly to this chat to receive a security audit powered by Google Gemini.")

# Inicialização
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot com Gemini AI rodando na nuvem com sucesso...")
    app.run_polling()
