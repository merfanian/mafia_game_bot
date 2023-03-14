import random
from typing import List

from entity.game import Game
from entity.player import Player
from entity.role import GodFather, DoctorLecter, HostageTaker, Doctor, Detective, Investigator, Sniper, Guard, Armored, \
    Role, SimpleMafia, SimpleCitizen
from utils.telegramcommunicator import TelegramCommunicator

SUPPORTED_MAFIA_ROLES = [
    GodFather,
    DoctorLecter,
    HostageTaker,
]

SUPPORTED_CITIZEN_ROLES = [
    Doctor,
    Detective,
    Investigator,
    Sniper,
    Guard,
    Armored
]


class Facilitator:

    def __init__(self, tc: TelegramCommunicator):
        self.tc = tc
        self.mafia_count = None
        self.citizen_count = None
        self.mafia_roles = None
        self.citizen_roles = None
        self.roles = None
        self.players = None
        self.game = None

    @property
    def players_count(self):
        return self.mafia_count + self.citizen_count

    def get_playing_roles(self, count, supported_roles, default_role, message) -> List[Role]:
        roles = []
        names = [r.__name__ for r in supported_roles]
        chosen_names = self.tc.get_multiple_choices_from_list(message, names, threshold=count)
        for name in chosen_names:
            roles.append(next(r for r in supported_roles if r.__name__ == name)())
        roles.extend([default_role() for _ in range(count - len(roles))])
        return roles

    def announce_roles(self):
        for i, p in enumerate(self.players):
            self.tc.get_input_from_list(f"Hand the phone to {p.name}", ["Show my role"])
            sent_msg = self.tc.send_spoiler_message(f"You are {p.role}", to=p.name)
            self.tc.get_input_from_list(f"Got it? ", ["Got it"])
            self.tc.edit_message(sent_msg, f"*{p.name}* knew his/her role right here.")
        else:
            self.tc.get_input_from_list("Hand the phone to the God", ["Start the game"])

    def handle_game_init(self) -> Game:
        self.mafia_count = self.tc.get_number_from_user("How many mafias?")
        self.citizen_count = self.tc.get_number_from_user("How many citizens?")
        self.mafia_roles = self.get_playing_roles(self.mafia_count, SUPPORTED_MAFIA_ROLES, SimpleMafia,
                                                  "Choose mafia roles you would like to have.")
        self.tc.send_list("Mafia roles", self.mafia_roles)
        self.citizen_roles = self.get_playing_roles(self.citizen_count, SUPPORTED_CITIZEN_ROLES, SimpleCitizen,
                                                    "Choose citizen roles you would like to have.")
        self.tc.send_list("Citizen roles", self.citizen_roles)
        self.roles = self.mafia_roles + self.citizen_roles
        random.shuffle(self.roles)
        self.players: List[Player] = []
        for i in range(1, self.players_count + 1):
            self.players.append(
                Player(self.tc.get_str_from_user(f"Player number {i}, Enter player's name:"), self.roles.pop()))

        self.announce_roles()

        self.game = Game(self.players, self.tc)
        return self.game
