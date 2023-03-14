import time

from telebot import types


class TelegramCommunicator:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.result = None

    def _store_user_input(self, message):
        self.result = message.text

    def _handle_callback(self, call):
        if call.message:
            self.result = call.data

    def wait_for_result(self, poll_period=0.5):
        while self.result is None:
            time.sleep(poll_period)  # shit
        result = self.result
        self.result = None
        return result

    def get_input_from_list(self, message, l: list, to=None):
        # todo: Adjust row width automatically
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                           input_field_placeholder=message)
        for i in range(0, len(l), 2):
            if i + 1 == len(l):
                markup.row(types.KeyboardButton(l[i]))
                break
            markup.row(types.KeyboardButton(l[i]), types.KeyboardButton(l[i + 1]))

        sent_msg = self.send_message(message, to=to, reply_markup=markup)
        self.bot.register_next_step_handler(
            sent_msg, self._store_user_input)
        result = self.wait_for_result()
        return l.index(result)

    def get_multiple_choices_from_list(self, message, l: list, threshold=None, to=None):
        def generate_keyboard(mapping: dict, exit_keyword="Done"):
            markup = types.InlineKeyboardMarkup()
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            buttons = []
            for item, chosen in mapping.items():
                buttons.append(types.InlineKeyboardButton(text=f"{'✔' if chosen else ''}{item}", callback_data=item))
            markup.add(*buttons)
            markup.row(types.InlineKeyboardButton(text=exit_keyword, callback_data=exit_keyword))
            return markup

        def get_chosen_count(mapping: dict):
            return len([k for k, v in mapping.items() if v is True])

        threshold = threshold if threshold else len(l)
        m = {item: False for item in l}
        sent_msg = self.send_message(message, to=to, reply_markup=generate_keyboard(m))
        while True:
            self.bot.register_callback_query_handler(self._handle_callback, func=lambda call: True)
            result = self.wait_for_result(poll_period=0.1)
            if result == "Done":
                break
            m[result] = not m[result]
            self.edit_message(sent_msg, text=f"Options left:{threshold - get_chosen_count(m)}",
                              reply_markup=generate_keyboard(m))

        return [item for item in l if m[item] is True]

    def get_player_from_list(self, message, roles, to=None):
        index = self.get_input_from_list(message, [str(r.player) for r in roles], to)
        return roles[index]

    def get_bool_from_user(self, message, to=None) -> bool:
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, input_field_placeholder=message)
        yes_button, no_button = types.KeyboardButton('Yes'), types.KeyboardButton('No')
        markup.row(yes_button, no_button)
        sent_msg = self.send_message(message, to=to, reply_markup=markup)
        self.bot.register_next_step_handler(sent_msg, self._store_user_input)
        result = self.wait_for_result()
        return True if result == "Yes" else False

    def get_number_from_user(self, message, to=None) -> int:
        sent_msg = self.send_message(message, to=to)
        self.bot.register_next_step_handler(sent_msg, self._store_user_input)
        return int(self.wait_for_result())

    def get_str_from_user(self, message, to=None) -> str:
        sent_msg = self.send_message(message, to=to)
        self.bot.register_next_step_handler(sent_msg, self._store_user_input)
        return str(self.wait_for_result())

    def send_message(self, message, to=None, reply_markup=None):
        if to:
            message = f"*{to}*:\n\n{message}"
        return self.bot.send_message(self.chat_id, message, parse_mode="Markdown", reply_markup=reply_markup)

    def edit_message(self, sent_msg, text, reply_markup=None):
        self.bot.edit_message_text(chat_id=self.chat_id, message_id=sent_msg.message_id,
                                   text=text, parse_mode="Markdown",
                                   reply_markup=reply_markup)

    def send_spoiler_message(self, message, to=None):
        message = f"||{message}||"
        if to:
            message = f"*{to}*:\n\n{message}"
        return self.bot.send_message(self.chat_id, message, parse_mode="MarkdownV2")

    def send_status_inquiry(self, mafias, citizens):
        msg = f"*{len(mafias) + len(citizens)} died*\n"
        msg += f"{len(mafias)} mafias and {len(citizens)} citizens"
        return self.send_message(msg, to="Status Inquiry Result")

    def send_list(self, message, l: list, to=None):
        str = message + "\n"
        for i, item in enumerate(l, start=1):
            str = str + f"{i}. {item}\n"
        return self.send_message(str, to=to)
