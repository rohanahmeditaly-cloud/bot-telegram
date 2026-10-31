import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Fuso orario italiano
TZ_ITALIA = ZoneInfo("Europe/Rome")

# Orario strutturato per GIORNI DELLA SETTIMANA (0 = Lunedì, 1 = Martedì, ..., 6 = Domenica)
orario_settimanale = {
    0: (
        "Lunedì - 4 ICT\n"
        "08:15 - 09:15: ANDREATTA (CDIG2)\n"
        "09:15 - 10:15: ANDREATTA (CMST4)\n"
        "11:25 - 13:25: PETTENUZZO (CDIG2)\n"
        "13:25 - 14:25: TOSIN"
    ),
    1: (
        "Martedì - 4 ICT\n"
        "08:15 - 10:15: MUNICELLA (CSGGE3)\n"
        "10:15 - 11:15: ANDREATTA (CDIG2)\n"
        "11:25 - 12:25: ZEN (CLING2)\n"
        "12:25 - 14:25: BAGGIO (CDIG2)"
    ),
    2: "Mercoledì - 4 ICT\nNessuna lezione / Inserisci orario mercoledì",
    3: "Giovedì - 4 ICT\nNessuna lezione / Inserisci orario giovedì",
    4: "Venerdì - 4 ICT\nNessuna lezione / Inserisci orario venerdì",
    5: "Sabato - Fine settimana (Nessuna lezione)",
    6: "Domenica - Fine settimana (Nessuna lezione)"
}

NOMI_GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

def calcola_giorno(testo_utente: str) -> tuple[int, datetime]:
    # Data e ora correnti calcolate con il fuso orario italiano
    ora_italiana = datetime.now(TZ_ITALIA)
    testo = testo_utente.lower().strip()

    if "oggi" in testo:
        target_date = ora_italiana
    elif "domani" in testo and "dopo" not in testo:
        target_date = ora_italiana + timedelta(days=1)
    elif "dopodomani" in testo or "dopo domani" in testo:
        target_date = ora_italiana + timedelta(days=2)
    elif "lunedì prossimo" in testo or "lunedi prossimo" in testo or "lunedì" in testo or "lunedi" in testo:
        # Calcola i giorni mancanti al prossimo lunedì
        giorni_a_lunedi = (0 - ora_italiana.weekday() + 7) % 7
        if giorni_a_lunedi == 0:
            giorni_a_lunedi = 7
        target_date = ora_italiana + timedelta(days=giorni_a_lunedi)
    else:
        return None, None

    # Ritorna l'indice del giorno (0-6) e l'oggetto data
    return target_date.weekday(), target_date

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Chiedimi l'orario dicendo 'oggi', 'domani', 'dopodomani' o 'lunedì prossimo'.")

async def rispondi_orario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    giorno_index, data_calcolata = calcola_giorno(update.message.text)
    
    if giorno_index is not None:
        data_str = data_calcolata.strftime("%d/%m/%Y")
        nome_giorno = NOMI_GIORNI[giorno_index]
        testo_orario = orario_settimanale.get(giorno_index, "Orario non disponibile.")
        
        risposta = f"📅 Orario per {nome_giorno} {data_str}:\n\n{testo_orario}"
        await update.message.reply_text(risposta)
    else:
        await update.message.reply_text("Non ho capito la data. Scrivi ad esempio 'oggi', 'domani', 'dopodomani' o 'lunedì prossimo'.")

if __name__ == '__main__':
    if not TOKEN:
        print("ERRORE: TELEGRAM_TOKEN non trovato!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), rispondi_orario))
        
        print("Bot avviato in ora italiana con polling...")
        app.run_polling()
