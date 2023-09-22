import requests, PyPDF2, os

from PyPDF2.errors import PdfReadError
from datetime import datetime as dt
from time import strftime as date

from Config import TOKEN

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


def download(day:str, month:str) -> None:
    r = requests.get(f'https://ркэ.рф/assets/rasp/{day}{month}2023.pdf')
    open(f'{day}{month}.pdf', 'wb').write(r.content)


def get_lessons(day:str, month:str, sen:bool) -> bool | list | int:
    try:
        pdf = PyPDF2.PdfReader(f'{day}{month}.pdf')
    except PdfReadError:
        os.remove(f'{day}{month}.pdf')
        return 0
    for page_num in range(len(pdf.pages)):
        if 'ИС-303' in pdf.pages[page_num].extract_text():
            os.remove(f'{day}{month}.pdf')
            return True
    os.remove(f'{day}{month}.pdf')
    day_week = dt.now().weekday()+1
    if not sen:
        day_week += 1
    match day_week:
        case 1:
            return [ ('1', 'Разговоры о важном', 'A3'),
                     ('2', 'Web-apps', '210'),
                     ('3', 'Психология', '301'),
                     ('4', 'Сети', '404') ]
        case 2:
            return [ ('1', 'Сети', '404'),
                     ('2', 'Мат', '207'),
                     ('3', 'Web-apps', '210'),
                     ('4', 'Web-apps', '210') ]
        case 3:
            return [ ('0', 'Анг яз', '419'),
                     ('1', 'Web-apps', '210') ]
        case 4:
            return [ ('0', 'Web-apps', '210'),
                     ('1', 'Стандарт', '407') ]
        case 5:
            return [ ('1', 'Психология', '301'),
                     ('2', 'Web-apps', '210'),
                     ('3', 'Физ-ра', '407') ]
        case 6:
            return [ ('1', 'Мат', '207'),
                     ('2', 'Сети', '404'),
                     ('3', 'Стандарт', '407') ]


def parse_data(args: list, sen: bool=False) -> tuple[str, str]:
    if args == []:
        day = date('%d')
    else:
        day = args[0]
    if not sen:
        day = int(day) + 1
    if int(day) < 10:
        day = f'0{day}'
    return day, date('%m')


def parse_lessons(value: (bool | list | int)) -> str:
    if value == 0: return 'Ошибка в открытии pdf'
    if value is True:
        return 'Замена!'
    lessons = str()
    for lesson in value:
        lessons += f'{lesson[0]} - {lesson[1]} - {lesson[2]}\n'
    return lessons


async def get_lessons_bot(update: Update, 
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    day, month = parse_data(context.args)
    download(day, month)
    replaced_or_lessons = get_lessons(day, month, False)
    lessons = parse_lessons(replaced_or_lessons)
    await update.message.reply_text(lessons)


async def get_lessons_now(update: Update, 
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = 'Сегодня: ' + date('%d.%m') + ' - ' + date('%A')
    await update.message.reply_text(msg)
    day, month = parse_data([], True)
    download(day, month)
    replaced_or_lessons = get_lessons(day, month, True)
    lessons = parse_lessons(replaced_or_lessons)
    await update.message.reply_text(lessons)
    

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("pari_na", get_lessons_bot))
    app.add_handler(CommandHandler("pari_sen", get_lessons_now))
    app.run_polling()
