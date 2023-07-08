import telegram
import openai
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram.utils.request import Request
import threading

openai.api_key = "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"
TOKEN = "6065042495:AAFLr-eOs3UP0mpYw2mKB5LC6j9eZbQ0r0o"
request = Request(con_pool_size=8)
bot = telegram.Bot(token=TOKEN, request=request)

# создаем мьютекс
messages_lock = threading.Lock()

# создаем общий список сообщений для всех потоков
messages = []
messages.append({"role": "system",
                 "content": "Ты помощник"})

updates = bot.get_updates()
if updates:
    update = updates[-1]
    update = telegram.Update.de_json(update.to_dict(), bot)
else:
    update = None

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="sup")

def reply(update, context):
    message_text = update.message.text
    if True:
        user_name = update.message.from_user.first_name
        prompt = f"{message_text}"

        # блокируем доступ к messages для других потоков
        with messages_lock:
            messages.append({"role": "user", "content": prompt})
            while len(str(messages)) > 1097:
                messages.pop(1)
        print(messages)
        response = openai.ChatCompletion.create(
            messages=messages,
            model="gpt-3.5-turbo",
            max_tokens=3000,
            n=1,
            presence_penalty=0,
            stop=None,
            temperature=0.5,
        )
        response_text = response['choices'][0]['message']['content']

        # блокируем доступ к messages для других потоков
        with messages_lock:
            messages.append({"role": "assistant", "content": response_text})
            response_text = f"{user_name},\n {response_text}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)


updater = Updater(bot=bot, use_context=True, request_kwargs={'con_pool_size': 8})
if update is not None:
    updater.dispatcher.process_update(telegram.Update.de_json(update.to_dict(), bot))
start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler)
reply_handler = MessageHandler(Filters.text & (~Filters.command), reply)
updater.dispatcher.add_handler(reply_handler)
updater.start_polling()
