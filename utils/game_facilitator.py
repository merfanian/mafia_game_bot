import random
from typing import List

from entity.game import Game
from entity.player import Player
from entity.role import GodFather, DoctorLecter, HostageTaker, Doctor, Detective, Investigator, Sniper, Guard, Armored, \
    Role, SimpleMafia, SimpleCitizen

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

    def __init__(self, tc):
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

    def get_playing_roles(self, count, supported_roles, default_role) -> List[Role]:
        roles = []
        for role in supported_roles:
            if count - len(roles) > 0:
                if self.tc.get_input_from_list(f"Do you want to have {role.__name__} in the game?", [True, False]):
                    roles.append(role())
        else:
            roles.extend([default_role() for _ in range(count - len(roles))])
        return roles

    def handle_game_init(self) -> Game:
        self.mafia_count = self.tc.get_number_from_user("How many mafias?")
        self.citizen_count = self.tc.get_number_from_user("How many citizens?")
        self.mafia_roles = self.get_playing_roles(self.mafia_count, SUPPORTED_MAFIA_ROLES, SimpleMafia)
        self.tc.send_list("Mafia roles", self.mafia_roles)
        self.citizen_roles = self.get_playing_roles(self.citizen_count, SUPPORTED_CITIZEN_ROLES, SimpleCitizen)
        self.tc.send_list("Citizen roles", self.citizen_roles)
        self.roles = self.mafia_roles + self.citizen_roles
        random.shuffle(self.roles)
        self.players: List[Player] = []
        for i in range(1, self.players_count + 1):
            self.players.append(
                Player(self.tc.get_str_from_user(f"Player number {i}, Enter player's name:"), self.roles.pop()))

        self.tc.send_list("Players", [p.details for p in self.players])

        self.game = Game(self.players, self.tc)
        return self.game
