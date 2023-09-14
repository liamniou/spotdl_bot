import datetime
import logging as log
import os
import signal
import subprocess
import sys
import telebot


AUTHORIZED_USERS = [
    int(x) for x in os.getenv("AUTHORIZED_USERS", "294967926,191151492").split(",")
]

bot = telebot.TeleBot(
    os.getenv("TELEGRAM_BOT_TOKEN"),
    threaded=False,
    parse_mode="Markdown",
)


def signal_handler(signal_number):
    print("Received signal " + str(signal_number) + ". Trying to end tasks and exit...")
    bot.stop_polling()
    sys.exit(0)


def log_and_send_message_decorator(fn):
    def wrapper(message):
        bot.send_message(message.chat.id, f"Executing your command, please wait...")
        log.info("[FROM {}] [{}]".format(message.chat.id, message.text))
        if message.chat.id in AUTHORIZED_USERS:
            reply = fn(message)
        else:
            reply = "Sorry, this is a private bot"
        log.info("[TO {}] [{}]".format(message.chat.id, reply))
        try:
            bot.send_message(message.chat.id, reply)
        except Exception as e:
            log.warning(f"Something went wrong:\n{e}")
            bot.send_message(
                message.chat.id, "Sorry, I can't send you reply. Report it to @Lestarby"
            )

    return wrapper


@bot.message_handler(
    func=lambda m: m.text is not None and m.text.startswith(("https://"))
)
@log_and_send_message_decorator
def download(message):
    bot.reply_to(message, "Downloading...")
    download_dir = f'/Plex/Music/spotdl/{datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")}/'
    process_output = subprocess.run(
        [
            "spotdl",
            "download",
            message.text,
            "--output",
            download_dir + "{artist} - {title}.{output-ext}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    output = process_output.stdout.strip()
    log.info(output)

    return "Completed"


def main():
    log.basicConfig(level=log.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("Bot was started.")
    signal.signal(signal.SIGINT, signal_handler)
    log.info("Starting bot polling...")
    bot.polling()


if __name__ == "__main__":
    main()
