import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Configuração de Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Pega o Token das variáveis de ambiente do Render (ou usa o seu token direto caso prefira)
TELEGRAM_TOKEN = os.environ.get("9109101364:AAGErsnxhTa0abSyNe7G_gjLGhbMLcR2be4", "9109101364:AAGErsnxhTa0abSyNe7G_gjLGhbMLcR2be4")

# Mensagem de Boas-Vindas
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛡️ **Global Anti-Scam Shield**\n\n"
        "Welcome! I am your real-time security assistant.\n"
        "Bem-vindo! Eu sou seu assistente de segurança em tempo real.\n\n"
        "📥 **How to use / Como usar:**\n"
        "Forward any suspicious message, text, link, or image to me, and I will analyze if it is a scam or safe!\n\n"
        "Encaminhe qualquer mensagem, texto, link ou imagem suspeita para mim, e eu analisarei se é um golpe ou seguro!"
    )
    
    keyboard = [
        [InlineKeyboardButton("⭐ Go Premium / Assinar Premium", callback_data='premium_info')],
        [InlineKeyboardButton("❓ Help / Ajuda", callback_data='help_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

# Motor de Análise de Risco
def analyze_content(text: str) -> dict:
    text_lower = text.lower()
    
    scam_triggers = [
        "urgent", "urgente", "suspended", "suspensa", "verify your account", "verifique sua conta",
        "winner", "ganhador", "pix", "transfer", "bank", "banco", "crypto", "investment", "lucro garantido",
        "click here", "clique aqui", "claim", "resgatar", "limited time", "tempo limitado", "security alert"
    ]
    
    risk_score = 0

    for trigger in scam_triggers:
        if trigger in text_lower:
            risk_score += 25

    if "http://" in text_lower or "bit.ly" in text_lower or ".xyz" in text_lower or "tinyurl" in text_lower:
        risk_score += 40

    if risk_score >= 50:
        return {
            "title": "🚨 HIGH RISK / ALTO RISCO (GOLPE CONFIRMADO)",
            "message": "This content shows strong patterns of social engineering, phishing, or fraud.\n\nEste conteúdo apresenta fortes padrões de engenharia social, phishing ou fraude.",
            "action": "❌ Do NOT click any links, do NOT send money, and block the sender immediately.\n❌ NÃO clique em links, NÃO envie dinheiro e bloqueie o remetente imediatamente."
        }
    elif risk_score >= 25:
        return {
            "title": "⚠️ WARNING / ATENÇÃO (RISCO MÉDIO)",
            "message": "Suspicious elements detected. Proceed with extreme caution.\n\nElementos suspeitos detectados. Prossiga com extrema cautela.",
            "action": "🔍 Verify through official channels before taking any action.\n🔍 Verifique através de canais oficiais antes de tomar qualquer atitude."
        }
    else:
        return {
            "title": "🟢 SAFE / SEGURO (BAIXO RISCO)",
            "message": "No obvious scam patterns identified in this text.\n\nNenhum padrão óbvio de golpe identificado neste texto.",
            "action": "✅ Always maintain basic security practices.\n✅ Mantenha sempre as práticas básicas de segurança."
        }

# Processador de Mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or update.message.caption or ""
    
    if not user_text:
        await update.message.reply_text("Please send a text message or link to analyze.")
        return

    result = analyze_content(user_text)
    
    response = (
        f"{result['title']}\n\n"
        f"📝 **Analysis / Análise:**\n{result['message']}\n\n"
        f"💡 **Recommended Action / Ação Recomendada:**\n{result['action']}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛡️ Protect a Relative / Proteger um Familiar", callback_data='premium_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)

# Tratamento de Botões
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'premium_info':
        premium_text = (
            "💎 **Premium Plan / Plano Premium**\n\n"
            "• Unlimited daily checks / Checagens diárias ilimitadas\n"
            "• Real-time audio and image scan / Varredura de áudio e imagem\n"
            "• Family Protection Alerts / Alertas de Proteção Familiar\n\n"
            "Price: **$2.99 / month**\n\n"
            "To activate, contact support or click below to subscribe."
        )
        await query.message.reply_text(premium_text, parse_mode='Markdown')
    elif query.data == 'help_info':
        await query.message.reply_text("Forward any message directly to this chat to receive a security audit.")

# Inicialização
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot rodando com sucesso na nuvem...")
    app.run_polling()