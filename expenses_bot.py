import json
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

API_TOKEN = '7200841404:AAEa4pK99ZnqqXpmpsTimHUD0y-umWCZHKs'
DATA_FILE = 'data.json'
EXPENSE_CATEGORIES = ['Їжа', 'Транспорт', 'Розваги', 'Комунальні', 'Інше']

ADDING_EXPENSE_AMOUNT, ADDING_EXPENSE_CATEGORY, ADDING_EXPENSE_DATE = range(3)
ADDING_INCOME_AMOUNT, ADDING_INCOME_CATEGORY, ADDING_INCOME_DATE = range(3, 6)

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_keyboard():
    keyboard = [
        ['Додати витрату', 'Додати дохід'],
        ['Список категорій', 'Перегляд витрат'],
        ['Перегляд доходів', 'Видалити запис'],
        ['Статистика', 'Очистити чат'],
        ['Повернутись на початок']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Ласкаво просимо до бота для відстеження витрат! Використовуйте кнопки нижче для взаємодії.', reply_markup=get_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Доступні команди:\n'
        '/add_expense <сума> <категорія>\n'
        '/add_income <сума> <категорія>\n'
        '/list_categories\n'
        '/view_expenses\n'
        '/view_incomes\n'
        '/delete_record <тип> <індекс>\n'
        '/stats\n'
        '/clear_chat\n'
        '/back_to_start',
        reply_markup=get_keyboard()
    )

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Будь ласка, введіть суму витрат:', reply_markup=ReplyKeyboardRemove())
    return ADDING_EXPENSE_AMOUNT

async def add_expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text('Будь ласка, введіть дійсну суму.')
        return ADDING_EXPENSE_AMOUNT

    context.user_data['expense_amount'] = amount
    await update.message.reply_text('Будь ласка, введіть категорію витрат:')
    return ADDING_EXPENSE_CATEGORY

async def add_expense_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text
    if category not in EXPENSE_CATEGORIES:
        EXPENSE_CATEGORIES.append(category)
    
    context.user_data['expense_category'] = category
    await update.message.reply_text('Будь ласка, введіть дату витрат у форматі РРРР-ММ-ДД (або залиште пустим для поточної дати):')
    return ADDING_EXPENSE_DATE

async def add_expense_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_text = update.message.text
    try:
        date = datetime.strptime(date_text, '%Y-%м-%d') if date_text else datetime.now()
    except ValueError:
        await update.message.reply_text('Неправильний формат дати. Будь ласка, введіть дату у форматі РРРР-ММ-ДД:')
        return ADDING_EXPENSE_DATE

    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {'expenses': [], 'incomes': []}
    data[user_id]['expenses'].append({
        'amount': context.user_data['expense_amount'],
        'category': context.user_data['expense_category'],
        'date': date.strftime('%Y-%м-%d')
    })
    save_data(data)
    await update.message.reply_text('Витрату додано!', reply_markup=get_keyboard())
    return ConversationHandler.END

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Будь ласка, введіть суму доходу:', reply_markup=ReplyKeyboardRemove())
    return ADDING_INCOME_AMOUNT

async def add_income_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text('Будь ласка, введіть дійсну суму.')
        return ADDING_INCOME_AMOUNT

    context.user_data['income_amount'] = amount
    await update.message.reply_text('Будь ласка, введіть категорію доходу:')
    return ADDING_INCOME_CATEGORY

async def add_income_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text
    context.user_data['income_category'] = category
    await update.message.reply_text('Будь ласка, введіть дату доходу у форматі РРРР-ММ-ДД (або залиште пустим для поточної дати):')
    return ADDING_INCOME_DATE

async def add_income_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_text = update.message.text
    try:
        date = datetime.strptime(date_text, '%Y-%м-%d') if date_text else datetime.now()
    except ValueError:
        await update.message.reply_text('Неправильний формат дати. Будь ласка, введіть дату у форматі РРРР-ММ-ДД:')
        return ADDING_INCOME_DATE

    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {'expenses': [], 'incomes': []}
    data[user_id]['incomes'].append({
        'amount': context.user_data['income_amount'],
        'category': context.user_data['income_category'],
        'date': date.strftime('%Y-%м-%d')
    })
    save_data(data)
    await update.message.reply_text('Дохід додано!', reply_markup=get_keyboard())
    return ConversationHandler.END

async def list_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Доступні категорії витрат: {", ".join(EXPENSE_CATEGORIES)}', reply_markup=get_keyboard())

async def view_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id not in data or not data[user_id]['expenses']:
        await update.message.reply_text('Записи про витрати відсутні.', reply_markup=get_keyboard())
        return

    expenses = data[user_id]['expenses']
    response = "Витрати:\n" + "\n".join([f"{e['date']} - {e['amount']} - {e['category']}" for e in expenses])
    await update.message.reply_text(response, reply_markup=get_keyboard())

async def view_incomes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id not in data or not data[user_id]['incomes']:
        await update.message.reply_text('Записи про доходи відсутні.', reply_markup=get_keyboard())
        return

    incomes = data[user_id]['incomes']
    response = "Доходи:\n" + "\n".join([f"{i['date']} - {i['amount']} - {i['category']}" for i in incomes])
    await update.message.reply_text(response, reply_markup=get_keyboard())

async def delete_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id not in data:
        await update.message.reply_text('Записи відсутні.', reply_markup=get_keyboard())
        return

    try:
        record_type = context.args[0]
        record_index = int(context.args[1])
        if record_type not in ['expenses', 'incomes'] or record_index >= len(data[user_id][record_type]):
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text('Використання: /delete_record <тип> <індекс>', reply_markup=get_keyboard())
        return

    del data[user_id][record_type][record_index]
    save_data(data)
    await update.message.reply_text('Запис видалено.', reply_markup=get_keyboard())

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id not in data:
        await update.message.reply_text('Записи відсутні.', reply_markup=get_keyboard())
        return

    expenses = data[user_id]['expenses']
    incomes = data[user_id]['incomes']
    total_expenses = sum(e['amount'] for e in expenses)
    total_incomes = sum(i['amount'] for i in incomes)
    response = f'Загальні витрати: {total_expenses}\nЗагальні доходи: {total_incomes}\n\nДеталізація витрат:\n'
    response += "\n".join([f"{e['date']} - {e['amount']} - {e['category']}" for e in expenses])
    response += f'\n\nДеталізація доходів:\n'
    response += "\n".join([f"{i['date']} - {i['amount']} - {i['category']}" for i in incomes])
    await update.message.reply_text(response, reply_markup=get_keyboard())

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Очищення чату...', reply_markup=get_keyboard())
    # Here you can implement actual chat clearing if necessary

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'Додати витрату':
        return await add_expense(update, context)
    elif text == 'Додати дохід':
        return await add_income(update, context)
    elif text == 'Список категорій':
        await list_categories(update, context)
    elif text == 'Перегляд витрат':
        await view_expenses(update, context)
    elif text == 'Перегляд доходів':
        await view_incomes(update, context)
    elif text == 'Видалити запис':
        await update.message.reply_text('Використання: /delete_record <тип> <індекс>', reply_markup=get_keyboard())
    elif text == 'Статистика':
        await stats(update, context)
    elif text == 'Очистити чат':
        await clear_chat(update, context)
    elif text == 'Повернутись на початок':
        await back_to_start(update, context)
    else:
        await update.message.reply_text('Невідома команда. Використовуйте /help для перегляду доступних команд.', reply_markup=get_keyboard())

def main():
    app = ApplicationBuilder().token(API_TOKEN).build()

    conv_handler_expense = ConversationHandler(
        entry_points=[CommandHandler('add_expense', add_expense), MessageHandler(filters.TEXT & filters.Regex('^Додати витрату$'), add_expense)],
        states={
            ADDING_EXPENSE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_amount)],
            ADDING_EXPENSE_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_category)],
            ADDING_EXPENSE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_date)],
        },
        fallbacks=[CommandHandler('cancel', lambda update, context: update.message.reply_text('Скасовано.', reply_markup=get_keyboard()))]
    )

    conv_handler_income = ConversationHandler(
        entry_points=[CommandHandler('add_income', add_income), MessageHandler(filters.TEXT & filters.Regex('^Додати дохід$'), add_income)],
        states={
            ADDING_INCOME_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_income_amount)],
            ADDING_INCOME_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_income_category)],
            ADDING_INCOME_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_income_date)],
        },
        fallbacks=[CommandHandler('cancel', lambda update, context: update.message.reply_text('Скасовано.', reply_markup=get_keyboard()))]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler_expense)
    app.add_handler(conv_handler_income)
    app.add_handler(CommandHandler("list_categories", list_categories))
    app.add_handler(CommandHandler("view_expenses", view_expenses))
    app.add_handler(CommandHandler("view_incomes", view_incomes))
    app.add_handler(CommandHandler("delete_record", delete_record))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("clear_chat", clear_chat))
    app.add_handler(CommandHandler("back_to_start", back_to_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()