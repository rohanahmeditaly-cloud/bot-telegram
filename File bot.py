import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta

# Variabili d'ambiente configurate su Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
PORT = int(os.environ.get("PORT", 10000))

# Orario basato sul tuo PDF (aggiungi le altre date seguendo il formato YYYY-MM-DD)
orario_scolastico = {
    "2026-09-28": (
        "Lunedì 28 settembre 2026 - 4 ICT\n"
        "08:15 - 09:15: ANDREATTA (CDIG2)\n"
        "09:15 - 10:15: ANDREATTA (CMST4)\n"
        "11:25 - 13:25: PETTENUZZO (CDIG2)\n"
        "13:25 - 14:25: TOSIN"
    ),
    "2026-09-29": (
        "Martedì 29 settembre 2026 - 4 ICT\n"
        "08:15 - 10:15: MUNICELLA (CSGGE3)\n"
        "10:15 - 11:15: ANDREATTA (CDIG2)\n"
        "11:25 - 12:25: ZEN (CLING2)\n"
        "12:25 - 14:25: BAGGIO (CDIG2)"
    )
}

def calcola_data(testo_utente: str) -> str:
    oggi = datetime.now()
    testo = testo_utente.lower()
    
    if "oggi" in testo:
        data = oggi
    elif "domani" in testo and "dopo" not in testo:
        data = oggi + timedelta(days=1)
    elif "dopodomani" in testo or "dopo domani" in testo:
        data = oggi + timedelta(days=2)
    elif "lunedì prossimo" in testo:
        giorni_mancanti = (0 - oggi.weekday() + 7) % 7
        data = oggi + timedelta(days=giorni_mancanti if giorni_mancanti != 0 else 7)
    else:
        return None
        
    return data.strftime("%Y-%m-%d")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Chiedimi l'orario (es. 'orario di domani', 'oggi', 'dopodomani').")

async def rispondi_orario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_formattata = calcola_data(update.message.text)
    if data_formattata:
        orario = orario_scolastico.get(data_formattata, "Nessuna lezione trovata per questa data.")
        await update.message.reply_text(orario)
    else:
        await update.message.reply_text("Non ho capito la data. Usa 'oggi', 'domani', 'dopodomani' o 'lunedì prossimo'.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), rispondi_orario))
    
    # Configurazione Webhook per Render
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )