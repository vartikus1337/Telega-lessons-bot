import requests, PyPDF2

from datetime import datetime as dt
from time import strftime as date
from Config import TOKEN

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


def download(day:str, month:str) -> None:
    r = requests.get(f'https://ркэ.рф/assets/rasp/{day}{month}20231.pdf')
    open(f'{day}{month}.pdf', 'wb').write(r.content)


def parse_date(day:str, month:str) -> tuple[str, str]:
    if int(day) < 10: day = f'0{day}'
    return day, month


def get_lessons(day:str, month:str) -> bool | list:
    pdf = PyPDF2.PdfReader(f'{day}{month}.pdf')
    for page_num in range(len(pdf.pages)):
        if 'ИС-303' in pdf.pages[page_num].extract_text():
            return True
    day_week = dt.now().weekday()
    match day_week: 
        # TODO:
        # вместо print написать пары в list с номером и кабинетом
        case 1:
            print('Понедельник')
        case 2:
            print('Вторник')
        case 3:
            print('Среда')
        case 4:
            print('Четверг')
        case 5:
            print('Пятница')
        case 6:
            print('Суббота')


async def get_lessons_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print('Тыкнута <Получить пары>')
    month = date('%m')
    if context.args == []: print('args нет'); day = date('%d')
    else: print('args есть'); day = context.args[0]
    day, month = parse_date(day, month)
    download(day, month)
    replaced = get_lessons(day, month)
    if replaced is True:
        await update.message.reply_text('Замена!')
    else:
        pass 
    # TODO:
    #  Тут Дописать вывод с get_lessons


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("pari_na", get_lessons_bot))
    app.run_polling()

    # TODO:
    # Пары на сегодня
