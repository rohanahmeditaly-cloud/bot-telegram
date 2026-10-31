import os
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Fuso orario italiano
TZ_ITALIA = timezone(timedelta(hours=1))

# Calendario reale estratto dal PDF (Formato: YYYY-MM-DD)
CALENDARIO_SCOLASTICO = {
    # --- Settimana dal 28 Settembre al 2 Ottobre ---
    "2026-09-28": "⏰ 08:15 - 09:15 ➔ ANDREATTA\n⏰ 09:15 - 10:15 ➔ ANDREATTA\n⏰ 11:25 - 13:25 ➔ PETTENUZZO\n⏰ 13:25 - 14:25 ➔ TOSIN",
    "2026-09-29": "⏰ 08:15 - 10:15 ➔ MUNICELLA\n⏰ 10:15 - 11:15 ➔ ANDREATTA\n⏰ 11:25 - 12:25 ➔ ZEN\n⏰ 12:25 - 14:25 ➔ BAGGIO",
    "2026-09-30": "⏰ 08:15 - 10:15 ➔ PETTENUZZO\n⏰ 10:15 - 12:25 ➔ TOSIN\n⏰ 12:25 - 13:25 ➔ ANDREATTA\n⏰ 13:25 - 14:25 ➔ BELLO'",
    "2026-10-01": "⏰ 08:15 - 14:25 ➔ BALLOTTO",
    "2026-10-02": "⏰ 08:15 - 09:15 ➔ BASSETTO\n⏰ 09:15 - 10:15 ➔ ZEN\n⏰ 10:15 - 12:25 ➔ PETTENUZZO\n⏰ 12:25 - 13:25 ➔ ZEN",

    # --- Settimana dal 5 al 9 Ottobre ---
    "2026-10-05": "⏰ 08:15 - 11:15 ➔ TOSIN\n⏰ 11:25 - 12:25 ➔ VIGO\n⏰ 12:25 - 14:25 ➔ PETTENUZZO",
    "2026-10-06": "⏰ 08:15 - 10:15 ➔ PETTENUZZO\n⏰ 10:15 - 11:15 ➔ VIGO\n⏰ 11:25 - 12:25 ➔ BAGGIO\n⏰ 12:25 - 14:25 ➔ LEVORATO",
    "2026-10-07": "⏰ 08:15 - 09:15 ➔ ZEN\n⏰ 09:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 12:25 ➔ PETTENUZZO\n⏰ 12:25 - 14:25 ➔ BELLO'",
    "2026-10-08": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 13:25 ➔ LEVORATO\n⏰ 13:25 - 14:25 ➔ ZEN",
    "2026-10-09": "⏰ 08:15 - 09:15 ➔ BASSETTO\n⏰ 09:15 - 10:15 ➔ ZEN\n⏰ 10:15 - 12:25 ➔ LEVORATO\n⏰ 12:25 - 13:25 ➔ BAGGIO",

    # --- Settimana dal 12 al 16 Ottobre ---
    "2026-10-12": "⏰ 08:15 - 10:15 ➔ PETTENUZZO\n⏰ 10:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 12:25 ➔ VIGO\n⏰ 12:25 - 13:25 ➔ ZEN\n⏰ 13:25 - 14:25 ➔ MARTINAGGIA",
    "2026-10-13": "⏰ 08:15 - 10:15 ➔ MUNICELLA\n⏰ 10:15 - 12:25 ➔ BAGGIO\n⏰ 12:25 - 14:25 ➔ PETTENUZZO",
    "2026-10-14": "⏰ 08:15 - 09:15 ➔ ZEN\n⏰ 09:15 - 10:15 ➔ PETTENUZZO\n⏰ 10:15 - 11:15 ➔ BASSETTO\n⏰ 11:25 - 13:25 ➔ BELLO\n⏰ 13:25 - 14:25 ➔ ZEN",
    "2026-10-15": "⏰ 08:15 - 14:25 ➔ BALLOTTO",
    "2026-10-16": "⏰ 08:15 - 09:15 ➔ BASSETTO\n⏰ 09:15 - 10:15 ➔ ANDREATTA\n⏰ 10:15 - 11:15 ➔ LEVORATO\n⏰ 11:25 - 12:25 ➔ ZEN\n⏰ 12:25 - 13:25 ➔ BAGGIO",

    # --- Settimana dal 19 al 23 Ottobre ---
    "2026-10-19": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 13:25 ➔ VIGO\n⏰ 13:25 - 14:25 ➔ MARTINAGGIA",
    "2026-10-20": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 12:25 ➔ PETTENUZZO\n⏰ 12:25 - 14:25 ➔ LEVORATO",
    "2026-10-21": "⏰ 08:15 - 10:15 ➔ PETTENUZZO\n⏰ 10:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 12:25 ➔ ANDREATTA\n⏰ 12:25 - 14:25 ➔ BELLO'",
    "2026-10-22": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 12:25 ➔ LEVORATO\n⏰ 12:25 - 13:25 ➔ ANDREATTA",

    # --- Settimana dal 26 al 30 Ottobre ---
    "2026-10-26": "⏰ 08:15 - 10:15 ➔ ANDREATTA\n⏰ 10:15 - 11:15 ➔ BASSETTO\n⏰ 11:25 - 12:25 ➔ ZEN\n⏰ 12:25 - 14:25 ➔ PETTENUZZO",
    "2026-10-27": "⏰ 08:15 - 10:15 ➔ MUNICELLA\n⏰ 10:15 - 12:25 ➔ PETTENUZZO\n⏰ 12:25 - 14:25 ➔ LEVORATO",
    "2026-10-28": "⏰ 08:15 - 10:15 ➔ PETTENUZZO\n⏰ 10:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 12:25 ➔ ANDREATTA\n⏰ 12:25 - 14:25 ➔ BELLO'",
    "2026-10-29": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 12:25 ➔ LEVORATO\n⏰ 12:25 - 13:25 ➔ BASSETTO",
    "2026-10-30": "⏰ 08:15 - 09:15 ➔ MARTINAGGIA\n⏰ 09:15 - 11:15 ➔ ANDREATTA\n⏰ 11:25 - 12:25 ➔ ZEN\n⏰ 12:25 - 13:25 ➔ LEVORATO",

    # --- Settimana dal 2 al 6 Novembre ---
    "2026-11-02": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 12:25 ➔ PETTENUZZO\n⏰ 12:25 - 13:25 ➔ ANDREATTA\n⏰ 13:25 - 14:25 ➔ MARTINAGGIA",
    "2026-11-03": "⏰ 08:15 - 10:15 ➔ PETTENUZZO\n⏰ 10:15 - 12:25 ➔ TOSIN\n⏰ 12:25 - 14:25 ➔ LEVORATO",
    "2026-11-04": "⏰ 08:15 - 09:15 ➔ LEVORATO\n⏰ 09:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 12:25 ➔ ANDREATTA\n⏰ 12:25 - 14:25 ➔ BELLO'",
    "2026-11-05": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 12:25 ➔ LEVORATO\n⏰ 12:25 - 14:25 ➔ TOSIN",
    "2026-11-06": "⏰ 08:15 - 09:15 ➔ MARTINAGGIA\n⏰ 09:15 - 10:15 ➔ ZEN\n⏰ 10:15 - 11:15 ➔ ANDREATTA\n⏰ 11:25 - 12:25 ➔ BASSETTO\n⏰ 12:25 - 13:25 ➔ LEVORATO",

    # --- Settimana dal 9 al 13 Novembre ---
    "2026-11-09": "⏰ 08:15 - 10:15 ➔ ANDREATTA\n⏰ 10:15 - 11:15 ➔ ZEN\n⏰ 11:25 - 12:25 ➔ VIGO\n⏰ 12:25 - 14:25 ➔ PETTENUZZO",
    "2026-11-10": "⏰ 08:15 - 10:15 ➔ MUNICELLA\n⏰ 10:15 - 11:15 ➔ TOSIN\n⏰ 11:25 - 12:25 ➔ ANDREATTA\n⏰ 12:25 - 14:25 ➔ LEVORATO",
    "2026-11-11": "⏰ 08:15 - 09:15 ➔ TOSIN\n⏰ 09:15 - 10:15 ➔ BASSETTO\n⏰ 10:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 12:25 ➔ ANDREATTA\n⏰ 12:25 - 14:25 ➔ BELLO'",
    "2026-11-12": "⏰ 08:15 - 09:15 ➔ ANDREATTA\n⏰ 09:15 - 10:15 ➔ BASSETTO\n⏰ 10:15 - 12:25 ➔ LEVORATO\n⏰ 12:25 - 13:25 ➔ ANDREATTA",
    "2026-11-13": "⏰ 08:15 - 09:15 ➔ MARTINAGGIA\n⏰ 09:15 - 11:15 ➔ ANDREATTA\n⏰ 11:25 - 12:25 ➔ ZEN\n⏰ 12:25 - 13:25 ➔ BAGGIO",

    # --- Settimana dal 16 al 20 Novembre ---
    "2026-11-16": "⏰ 08:15 - 09:15 ➔ ZEN\n⏰ 09:15 - 10:15 ➔ ANDREATTA\n⏰ 10:15 - 11:15 ➔ PETTENUZZO\n⏰ 11:25 - 12:25 ➔ VIGO\n⏰ 12:25 - 13:25 ➔ ANDREATTA",
    "2026-11-17": "⏰ 08:15 - 10:15 ➔ LEVORATO\n⏰ 10:15 - 11:15 ➔ TOSIN\n⏰ 11:25 - 12:25 ➔ ANDREATTA\n⏰ 12:25 - 13:25 ➔ ANDREATTA",
    "2026-11-18": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 14:25 ➔ BELLO'",
    "2026-11-19": "⏰ 08:15 - 09:15 ➔ ZEN\n⏰ 09:15 - 11:15 ➔ BAGGIO\n⏰ 11:25 - 14:25 ➔ LEVORATO",
    "2026-11-20": "⏰ 09:15 - 10:15 ➔ ANDREATTA\n⏰ 10:15 - 11:15 ➔ LEVORATO\n⏰ 11:25 - 13:25 ➔ TOSIN",

    # --- Settimana dal 23 al 27 Novembre ---
    "2026-11-23": "⏰ 08:15 - 10:15 ➔ PETTENUZZO\n⏰ 10:15 - 11:15 ➔ ANDREATTA\n⏰ 11:25 - 12:25 ➔ VIGO\n⏰ 12:25 - 13:25 ➔ ZEN",

    # --- Dicembre ---
    "2026-12-13": "⏰ 08:15 - 10:15 ➔ TOSIN\n⏰ 10:15 - 11:15 ➔ ANDREATTA\n⏰ 11:25 - 12:25 ➔ VIGO\n⏰ 12:25 - 14:25 ➔ PETTENUZZO"
}

NOMI_GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]

def genera_messaggio_orario(titolo: str, data_dt: datetime) -> str:
    key_data = data_dt.strftime("%Y-%m-%d")
    data_visiva = data_dt.strftime("%d/%m/%Y")
    nome_giorno = NOMI_GIORNI[data_dt.weekday()].capitalize()

    # Controlla se è sabato o domenica
    if data_dt.weekday() >= 5:
        return f"✨ *{titolo}*\n📅 *{nome_giorno} {data_visiva}*\n───────────────────\n\n🎉 Nessuna lezione (Fine settimana)\n\n───────────────────"

    testo_orario = CALENDARIO_SCOLASTICO.get(key_data, "❌ Nessun orario trovato per questa data nel calendario.")

    risposta = (
        f"✨ *{titolo}*\n"
        f"📅 *{nome_giorno} {data_visiva}*\n"
        f"───────────────────\n\n"
        f"{testo_orario}\n\n"
        f"───────────────────"
    )

    if "LEVORATO" in testo_orario.upper() or "BAGGIO" in testo_orario.upper():
        risposta += "\n\n⚠️ *Meglio che stai a casa*"

    return risposta

def calcola_giorno(testo_utente: str) -> tuple[int, datetime]:
    ora_italiana = datetime.now(TZ_ITALIA)
    testo = testo_utente.lower().strip()

    if "oggi" in testo:
        target_date = ora_italiana
    elif "domani" in testo and "dopo" not in testo:
        target_date = ora_italiana + timedelta(days=1)
    elif "dopodomani" in testo or "dopo domani" in testo:
        target_date = ora_italiana + timedelta(days=2)
    else:
        giorno_trovato = None
        mancanti_map = {
            "lunedi": 0, "lunedì": 0,
            "martedi": 1, "martedì": 1,
            "mercoledi": 2, "mercoledì": 2,
            "giovedi": 3, "giovedì": 3,
            "venerdi": 4, "venerdì": 4,
            "sabato": 5,
            "domenica": 6
        }

        for nome, idx in mancanti_map.items():
            if nome in testo:
                giorno_trovato = idx
                break

        if giorno_trovato is not None:
            giorni_mancanti = (giorno_trovato - ora_italiana.weekday() + 7) % 7
            if giorni_mancanti == 0 and "prossim" in testo:
                giorni_mancanti = 7
            target_date = ora_italiana + timedelta(days=giorni_mancanti)
        else:
            return None, None

    return target_date.weekday(), target_date

def trova_prossima_lezione(professore: str) -> str:
    ora_italiana = datetime.now(TZ_ITALIA)
    professore = professore.upper()

    for offset in range(60):  # Scansiona i prossimi 60 giorni nel calendario
        giorno_corrente = ora_italiana + timedelta(days=offset)
        key_data = giorno_corrente.strftime("%Y-%m-%d")
        orario_testo = CALENDARIO_SCOLASTICO.get(key_data, "")

        if professore in orario_testo.upper():
            nome_g = NOMI_GIORNI[giorno_corrente.weekday()].capitalize()
            data_str = giorno_corrente.strftime("%d/%m/%Y")

            if offset == 0:
                quando = "oggi"
            elif offset == 1:
                quando = "domani"
            elif offset == 2:
                quando = "dopodomani"
            elif offset < 7:
                quando = f"questo {nome_g}"
            else:
                quando = f"{nome_g} {data_str}"

            return f"👨‍🏫 Avrai *{professore.capitalize()}* *{quando}* ({data_str})."

    return f"❌ Nessuna lezione con *{professore.capitalize()}* trovata nel calendario nei prossimi giorni."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Ciao! Benvenuto nel bot Orario Scolastico*\n\n"
        "Chiedimi l'orario scrivendo ad esempio:\n"
        "• `oggi`, `domani`, `dopodomani`\n"
        "• `lunedì`, `martedì`, `mercoledì`, `giovedì`, `venerdì`\n\n"
        "📌 *Comandi veloci:*\n"
        "/siam - Orario di domani\n"
        "/levorato - Prossima lezione con Levorato\n"
        "/baggio - Prossima lezione con Baggio",
        parse_mode="Markdown"
    )

async def siam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ora_italiana = datetime.now(TZ_ITALIA)
    domani = ora_italiana + timedelta(days=1)
    risposta = genera_messaggio_orario("Hey guys questo è l'orario di domani", domani)
    await update.message.reply_text(risposta, parse_mode="Markdown")

async def levorato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    risposta = trova_prossima_lezione("LEVORATO")
    await update.message.reply_text(risposta, parse_mode="Markdown")

async def baggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    risposta = trova_prossima_lezione("BAGGIO")
    await update.message.reply_text(risposta, parse_mode="Markdown")

async def rispondi_orario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    giorno_index, data_calcolata = calcola_giorno(update.message.text)

    if giorno_index is not None:
        risposta = genera_messaggio_orario("Hey guys questo è l'orario richiesto", data_calcolata)
        await update.message.reply_text(risposta, parse_mode="Markdown")
    else:
        await update.message.reply_text("❓ Non ho capito. Scrivi ad esempio 'oggi', 'domani', 'martedì' o 'venerdì'.")

if __name__ == '__main__':
    if not TOKEN:
        print("ERRORE: TELEGRAM_TOKEN non trovato!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("siam", siam))
        app.add_handler(CommandHandler("levorato", levorato))
        app.add_handler(CommandHandler("baggio", baggio))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), rispondi_orario))

        print("Bot avviato...")
        app.run_polling()
