import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Fuso orario italiano
TZ_ITALIA = ZoneInfo("Europe/Rome")

# Orario scolastico per giorno della settimana (0 = Lunedì, 1 = Martedì, ..., 6 = Domenica)
# Rimosse le sigle delle materie/aule tra parentesi
orario_settimanale = {
    0: (
        "08:15 - 09:15: ANDREATTA\n"
        "09:15 - 10:15: ANDREATTA\n"
        "11:25 - 13:25: PETTENUZZO\n"
        "13:25 - 14:25: TOSIN"
    ),
    1: (
        "08:15 - 10:15: MUNICELLA\n"
        "10:15 - 11:15: ANDREATTA\n"
        "11:25 - 12:25: ZEN\n"
        "12:25 - 14:25: BAGGIO"
    ),
    2: (
        "08:15 - 10:15: LEVORATO\n"
        "10:15 - 12:25: TOSIN"
    ),
    3: (
        "08:15 - 10:15: MUNICELLA\n"
        "10:15 - 12:25: PETTENUZZO"
    ),
    4: (
        "08:15 - 10:15: ZEN\n"
        "10:15 - 12:25: BAGGIO"
    ),
    5: "Nessuna lezione (Fine settimana)",
    6: "Nessuna lezione (Fine settimana)"
}

NOMI_GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]

def calcola_giorno(testo_utente: str) -> tuple[int, datetime]:
    ora_italiana = datetime.now(TZ_ITALIA)
    testo = testo_utente.lower().strip()

    # Riconoscimento "oggi", "domani", "dopodomani"
    if "oggi" in testo:
        target_date = ora_italiana
    elif "domani" in testo and "dopo" not in testo:
        target_date = ora_italiana + timedelta(days=1)
    elif "dopodomani" in testo or "dopo domani" in testo:
        target_date = ora_italiana + timedelta(days=2)
    else:
        # Riconoscimento giorni della settimana
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

    for offset in range(14):  # Controlla i prossimi 14 giorni
        giorno_corrente = ora_italiana + timedelta(days=offset)
        idx_giorno = giorno_corrente.weekday()
        orario_testo = orario_settimanale.get(idx_giorno, "")

        if professore in orario_testo.upper():
            nome_g = NOMI_GIORNI[idx_giorno].capitalize()
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
                quando = f"{nome_g} della settimana prossima"

            return f"Avrai {professore.capitalize()} **{quando}** ({nome_g} {data_str})."

    return f"Nessuna lezione con {professore.capitalize()} programmata nei prossimi giorni."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ciao! Chiedimi l'orario dicendo ad esempio 'oggi', 'domani', 'martedì' o 'venerdì'.\n\n"
        "Comandi speciali disponibili:\n"
        "/siam - Orario di domani\n"
        "/levorato - Prossima lezione di Levorato\n"
        "/baggio - Prossima lezione di Baggio"
    )

async def siam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ora_italiana = datetime.now(TZ_ITALIA)
    domani = ora_italiana + timedelta(days=1)
    giorno_idx = domani.weekday()
    
    nome_giorno = NOMI_GIORNI[giorno_idx]
    data_str = domani.strftime("%d/%m/%Y")
    orario = orario_settimanale.get(giorno_idx, "Nessuna lezione.")

    risposta = f"Hey guys questo e orario di domani ({nome_giorno} {data_str}):\n\n{orario}"
    
    if "LEVORATO" in orario.upper() or "BAGGIO" in orario.upper():
        risposta += "\n\nMeglio che stai a casa"

    await update.message.reply_text(risposta)

async def levorato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    risposta = trova_prossima_lezione("LEVORATO")
    await update.message.reply_text(risposta, parse_mode="Markdown")

async def baggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    risposta = trova_prossima_lezione("BAGGIO")
    await update.message.reply_text(risposta, parse_mode="Markdown")

async def rispondi_orario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    giorno_index, data_calcolata = calcola_giorno(update.message.text)

    if giorno_index is not None:
        data_str = data_calcolata.strftime("%d/%m/%Y")
        nome_giorno = NOMI_GIORNI[giorno_index]
        testo_orario = orario_settimanale.get(giorno_index, "Orario non disponibile.")

        risposta = f"Hey guys questo e orario di {nome_giorno} {data_str}:\n\n{testo_orario}"

        # Se tra le lezioni c'è Levorato o Baggio, aggiunge la frase finale
        if "LEVORATO" in testo_orario.upper() or "BAGGIO" in testo_orario.upper():
            risposta += "\n\nMeglio che stai a casa"

        await update.message.reply_text(risposta)
    else:
        await update.message.reply_text("Non ho capito la data. Scrivi ad esempio 'oggi', 'domani', 'martedì' o 'venerdì'.")

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

        print("Bot avviato in modalità Polling...")
        app.run_polling()
