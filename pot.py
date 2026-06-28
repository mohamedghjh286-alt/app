import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# =========================
# إعدادات البوت
# =========================

TOKEN = "8803704528:AAGjXIZkZgprZZXfl2QaicT-XgCjiPk3LJk"
CHANNEL = "@medo_channel"

bot = telebot.TeleBot(TOKEN)

user_state = {}
user_data = {}

processed_calls = set()

# =========================
# إخفاء الرقم
# =========================

def mask_number(number):
    number = str(number)

    if len(number) < 7:
        return "****"

    return number[:3] + "****" + number[-3:]


# =========================
# /start
# =========================

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    user_state[chat_id] = "photo"
    user_data[chat_id] = {}

    bot.send_message(chat_id, "📸 ابعت صورة الإثبات")


# =========================
# استقبال الصورة
# =========================

@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    chat_id = message.chat.id

    if user_state.get(chat_id) != "photo":
        return

    user_data[chat_id]["photo"] = message.photo[-1].file_id
    user_state[chat_id] = "number"

    bot.send_message(chat_id, "📱 ابعت الرقم المحول إليه")


# =========================
# استقبال النصوص
# =========================

@bot.message_handler(content_types=['text'])
def receive_text(message):
    chat_id = message.chat.id

    if chat_id not in user_state:
        return

    state = user_state[chat_id]

    if state == "number":

        user_data[chat_id]["number"] = message.text
        user_state[chat_id] = "id"

        bot.send_message(chat_id, "🆔 ابعت ID المستخدم")

    elif state == "id":

        user_data[chat_id]["id"] = message.text
        user_state[chat_id] = "amount"

        bot.send_message(chat_id, "💰 ابعت المبلغ")

    elif state == "amount":

        user_data[chat_id]["amount"] = message.text
        user_state[chat_id] = "method"

        markup = InlineKeyboardMarkup(row_width=2)

        markup.add(
            InlineKeyboardButton("🟥 فودافون كاش", callback_data="Vodafone Cash"),
            InlineKeyboardButton("🟦 اتصالات كاش", callback_data="Etisalat Cash"),
            InlineKeyboardButton("🟧 أورنج كاش", callback_data="Orange Cash"),
            InlineKeyboardButton("🟪 WE Pay", callback_data="WE Pay"),
            InlineKeyboardButton("🟡 Binance", callback_data="Binance"),
            InlineKeyboardButton("🟢 USDT (TRC20)", callback_data="USDT")
        )

        bot.send_message(chat_id, "💳 اختر طريقة الدفع:", reply_markup=markup)


# =========================
# اختيار طريقة الدفع
# =========================

@bot.callback_query_handler(func=lambda call: True)
def handle_method(call):

    chat_id = call.message.chat.id
    call_id = call.id

    if call_id in processed_calls:
        return

    processed_calls.add(call_id)

    bot.answer_callback_query(call.id)

    if user_state.get(chat_id) != "method":
        return

    user_data[chat_id]["method"] = call.data
    data = user_data[chat_id]

    caption = f"""💰 إثبات تحويل جديد

👤 ID: {data['id']}
📱 الرقم: {mask_number(data['number'])}
💵 المبلغ: {data['amount']} جنيه
💳 الطريقة: {data['method']}

✅ تم التنفيذ بنجاح
"""

    buttons = InlineKeyboardMarkup(row_width=2)
    buttons.add(
        InlineKeyboardButton("🤖 الدخول للبوت", url="https://t.me/medo_add_bot"),
        InlineKeyboardButton("💬 الدعم", url="https://t.me/medo_add")
    )

    bot.send_photo(
        CHANNEL,
        data["photo"],
        caption=caption,
        reply_markup=buttons
    )

    bot.edit_message_text(
        "✅ تم نشر الإثبات بنجاح",
        chat_id,
        call.message.message_id
    )

    user_state.pop(chat_id, None)
    user_data.pop(chat_id, None)


# =========================
# تشغيل البوت
# =========================

print("Bot is running...")
bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)