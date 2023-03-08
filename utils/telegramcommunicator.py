import time


class TelegramCommunicator:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.result = None

    def _store_user_input(self, message):
        self.result = message.text

    def wait_for_result(self):
        while self.result is None:
            time.sleep(1)  # shit
        result = self.result
        self.result = None
        return result

    def get_input_from_list(self, message, l: list, to=None):
        sent_msg = self.send_list(message, l, to)
        self.bot.register_next_step_handler(
            sent_msg, self._store_user_input)
        result = self.wait_for_result()
        return l[int(result) - 1]

    def get_player_from_list(self, message, roles, to=None):
        sent_msg = self.send_list(message, [str(r.player) for r in roles], to)
        self.bot.register_next_step_handler(
            sent_msg, self._store_user_input)
        result = int(self.wait_for_result())
        return roles[result - 1]

    def get_bool_from_user(self, message, to=None) -> bool:
        l = [True, False]
        sent_msg = self.send_list(message, l, to)
        self.bot.register_next_step_handler(sent_msg, self._store_user_input)
        return l[int(self.wait_for_result()) - 1]

    def get_number_from_user(self, message, to=None) -> int:
        sent_msg = self.send_message(message, to=to)
        self.bot.register_next_step_handler(sent_msg, self._store_user_input)
        return int(self.wait_for_result())

    def get_str_from_user(self, message, to=None) -> str:
        sent_msg = self.send_message(message, to=to)
        self.bot.register_next_step_handler(sent_msg, self._store_user_input)
        return str(self.wait_for_result())

    def send_message(self, message, to=None):
        if to:
            message = f"*{to}*:\n\n{message}"
        return self.bot.send_message(self.chat_id, message, parse_mode="Markdown")

    def send_status_inquiry(self, mafias, citizens):
        msg = f"*{len(mafias) + len(citizens)} died*\n"
        msg += f"{len(mafias)} mafias and {len(citizens)} citizens"
        return self.send_message(msg, to="Status Inquiry Result")

    def send_list(self, message, l: list, to=None):
        str = message + "\n"
        for i, item in enumerate(l, start=1):
            str = str + f"{i}. {item}\n"
        return self.send_message(str, to=to)
