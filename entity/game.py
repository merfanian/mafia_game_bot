from entity.player import *
from entity.role import Citizen, Mafia, HostageTaker, DoctorLecter, Doctor, Detective, Guard, Investigator, Sniper, Role
from utils.telegramcommunicator import TelegramCommunicator as Tc
from utils.utils import find_type_in_list
from entity.exception import BannedException

from utils.telegramcommunicator import TelegramCommunicator


class Game:

    def __init__(self, players: list[Player], tc: TelegramCommunicator):
        self.players = players
        self.mafias: list[Mafia] = [p.role for p in players if isinstance(p.role, Mafia)]
        self.citizens: list[Citizen] = [p.role for p in players if isinstance(p.role, Citizen)]
        self.all = self.mafias + self.citizens
        self.dead: list[Role] = []
        self.days_passed = 0
        self.tc = tc

    def handle_status_inquiry(self):
        decision = self.tc.get_input_from_list("Do you want to get status inquiry?", [True, False], to="Everyone")
        if decision:
            self.tc.send_status_inquiry([d for d in self.dead if isinstance(d, Mafia)],
                                        [d for d in self.dead if isinstance(d, Citizen)])

    def handle_morning_announcement(self, night_killed):
        self.tc.send_message([str(p.player) for p in night_killed], to="Morning Announcements")

    def update_players(self):
        newly_killed = [p for p in self.all if p.is_dead]
        self.dead.extend(newly_killed)
        self.all = [p for p in self.all if not p.is_dead]
        self.mafias = [m for m in self.mafias if not m.is_dead]
        self.citizens = [c for c in self.citizens if not c.is_dead]
        return newly_killed

    def switch_to_night(self):
        # wake mafias and choose a person to shot
        shooter: Mafia = next(iter(self.mafias))
        shooter.kill(
            self.tc.get_input_from_list("Who do you want to shoot at night?", self.citizens, to=shooter.role_name))

        # wake doctor lecter and save a mafia
        drlecter: DoctorLecter = find_type_in_list(DoctorLecter, self.mafias)
        if drlecter:
            drlecter.heal(self.tc.get_input_from_list("Who do you want to save?", self.mafias, to=drlecter.role_name))

        # wake hostage taker and ban a citizen
        hostage_taker: HostageTaker = find_type_in_list(HostageTaker, self.mafias)
        if hostage_taker:
            hostage_taker.block(
                self.tc.get_input_from_list("Who do you want to take as hostage?", self.citizens,
                                            to=hostage_taker.role_name))

        # wake guard and release hostage
        guard: Guard = find_type_in_list(Guard, self.citizens)
        if guard:
            try:
                guard.unblock(self.tc.get_input_from_list("Who do you want to save?", self.all, to=guard.role_name))
            except BannedException:
                self.tc.send_message("You are banned")

        # wake doctor and save a citizen
        doctor: Doctor = find_type_in_list(Doctor, self.citizens)
        if doctor:
            try:
                doctor.heal(self.tc.get_input_from_list("Who do you want to save?", self.all, to=doctor.role_name))
            except BannedException:
                self.tc.send_message("You are banned")

        # wake detective and inquiry about a person
        detective: Detective = find_type_in_list(Detective, self.citizens)
        if detective:
            try:
                self.tc.send_message(
                    detective.detect(
                        self.tc.get_input_from_list("Who do you want to detect?", self.all, to=detective.role_name)))
            except BannedException:
                self.tc.send_message("You are banned")

        # wake investigator and inquiry about two persons
        investigator: Investigator = find_type_in_list(Investigator, self.citizens)
        if investigator:
            try:
                self.tc.send_message(
                    investigator.investigate(
                        self.tc.get_input_from_list("Choose first person", self.all, to=investigator.role_name),
                        self.tc.get_input_from_list("Choose second person", self.all, to=investigator.role_name)))
            except BannedException:
                self.tc.send_message("You are banned")

        # wake sniper
        sniper: Sniper = find_type_in_list(Sniper, self.citizens)
        if sniper:
            try:
                decision = self.tc.get_input_from_list("Do you want to shoot tonight?", [True, False],
                                                       to=sniper.role_name)
                if decision:
                    sniper.kill(self.tc.get_input_from_list("Who do you want to kill?", self.all, to=sniper.role_name))
            except BannedException:
                self.tc.send_message("You are banned")

        [p.pass_night() for p in self.all]

    def switch_to_day(self):
        voter: Role = next(iter(self.all))
        decision = self.tc.get_input_from_list("Do you have kill candidate today?", [True, False],
                                               to="City")
        if decision:
            voter.vote(self.tc.get_input_from_list("Who do you want to kill?", self.all, to="City"))

        [p.pass_day() for p in self.all]

    def start(self):
        while True:
            self.switch_to_night()
            self.handle_morning_announcement(self.update_players())
            self.handle_status_inquiry()
            self.switch_to_day()
            self.update_players()
