import time


class TelegramCommunicator:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.result = None

    def _get_item_from_list(self, message):
        self.result = message.text

    def get_input_from_list(self, message, l: list, to=None):
        str = message + "\n"
        for i, item in enumerate(l, start=1):
            str = str + f"{i}. {item}\n"
        sent_msg = self.send_message(str, to=to)
        self.bot.register_next_step_handler(
            sent_msg, self._get_item_from_list)

        while (self.result is None):
            time.sleep(1)  # shit
        result = self.result
        self.result = None
        return l[int(result) - 1]

    def send_message(self, message, to=None):
        if to:
            message = f"*{to}*:\n\n{message}"
        return self.bot.send_message(self.chat_id, message, parse_mode="Markdown")

    def send_status_inquiry(self, mafias, citizens):
        msg = f"*{len(mafias) + len(citizens)} died*\n"
        msg += f"{len(mafias)} mafias and {len(citizens)} citizens"
        self.send_message(msg, to="Status Inquiry Result")
