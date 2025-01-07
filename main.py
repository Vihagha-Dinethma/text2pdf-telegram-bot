import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters)
from fpdf import FPDF
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

PDF_LANG, PDF_TITLE, PDF_TXT_COLOR, PDF_TEXT, SUMMARY = range(5)
    
async def start(update: Update, context:
  ContextTypes.DEFAULT_TYPE) -> int:
    
    keyboard = [
        [InlineKeyboardButton('DejaVuSansCondensed', callback_data='DejaVuSansCondensed ,DejaVuSansCondensed')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select a font and language \n\nformat: <font> - <language>', reply_markup=reply_markup)
    
    return PDF_LANG
    
async def pdf_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  
    query = update.callback_query
    await query.answer()
    context.user_data['pdf_lang'] = query.data
    
    await query.edit_message_text('Enter title for your pdf')
    
    return PDF_TITLE
    
async def pdf_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    context.user_data['pdf_title'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton('Black - Black', callback_data='Black - Black,0,0,0,0,0,0'), InlineKeyboardButton('Red - Black', callback_data='Red - Black,242,0,0,0,0,0')], 
        [InlineKeyboardButton('Red - Blue', callback_data='Red - Blue,242,0,0,6,0,180'),
        InlineKeyboardButton('Black - Blue', callback_data='Black - Blue,0,0,0,6,0,180')], 
        [InlineKeyboardButton('Red - Purple', callback_data='Red - Purple,242,0,0,141,0,180'), InlineKeyboardButton('Black - Purple', callback_data='Black - Purple,0,0,0,141,0,180')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select a title and text colors \n\nformat: <title color> - <text color>', reply_markup=reply_markup)
    
    return PDF_TXT_COLOR
    
async def pdf_txt_color(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  
    query = update.callback_query
    await query.answer()
    context.user_data['pdf_txt_color'] = query.data
    
    await query.edit_message_text('Enter text for the pdf')

    return PDF_TEXT
    
async def pdf_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  
    context.user_data['pdf_text'] = update.message.text
    
    await summary(update, context)
    
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  
    selections = context.user_data
    
    chat_id = update.effective_chat.id
    
    lang = selections.get('pdf_lang')
    splitted = lang.split(",", 1)
    lang_txt = splitted[0].strip()
    lang_ttf = splitted[1].strip()
    
    txt_color = selections.get('pdf_txt_color')
    splitted = txt_color.split(",")
    color_txt = splitted[0].strip()
    RT = int(splitted[1].strip())
    GT = int(splitted[2].strip())
    BT = int(splitted[3].strip())
    R = int(splitted[4].strip())
    G = int(splitted[5].strip())
    B = int(splitted[6].strip())
    
    title = selections.get('pdf_title')
    
    txt = selections.get('pdf_text')
    
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font(f'{lang_ttf}', '', f'{lang_ttf}.ttf', uni=True)
    pdf.set_font(f'{lang_ttf}', '', 18)
    pdf.set_text_color(RT, GT, BT)
    pdf.cell(0, 6, f'{title}', 0, 0, 'C')
    pdf.ln(10)
    pdf.set_font(f'{lang_ttf}', '', 14)
    pdf.set_text_color(R, G, B)
    pdf.write(8, txt)
    pdf.ln()
    pdf.output(f'{title}.pdf', 'F')
    document = open(f'{title}.pdf', 'rb')
    
    cap_text = (f"`PDF_DESCRIPTION\n\nPDF name: {title}.pdf\n\nPDF language: {lang_txt}\n\nPDF text color: {color_txt}`")
    
    
    await context.bot.send_document(chat_id, document, caption=cap_text, parse_mode='MarkdownV2')
    
    
    
    await update.message.reply_text('enter /cancel after this message')
    
    return ConversationHandler.END
    
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  
    await update.message.reply_text('enter /start to start again')
    
    return ConversationHandler.END
    
    
def main() -> None:
  
    application = Application.builder().token("YOUR-BOT-TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PDF_LANG: [CallbackQueryHandler(pdf_lang)],
            PDF_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pdf_title)],
            PDF_TXT_COLOR: [CallbackQueryHandler(pdf_txt_color)],
            PDF_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, pdf_text)],
            SUMMARY: [MessageHandler(filters.ALL, summary)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.add_handler(CommandHandler('start', start))

    application.run_polling()


if __name__ == '__main__':
    main()