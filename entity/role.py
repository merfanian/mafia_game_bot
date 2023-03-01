from abc import ABC, abstractmethod

from entity.ability import KillingAbility, NegotiateAbility, PreventionAbility, ProtectiveAbility, DetectiveAbility, \
    GuardingAbility, InvestigativeAbility, VotingAbility
from entity.exception import BannedException


class Role(VotingAbility, ABC):
    def __init__(self):
        self.died = False
        self.shot = False
        self.protected = False
        self.banned = False
        self.kicked = False
        self.player = None
        self.voted = False
        self.has_day_shield = False

    def pass_night(self):
        if self.kicked:
            self.died = True
            return

        if self.shot and not self.protected:
            self.died = True
            return

        self.protected = False
        self.shot = False
        self.banned = False

    def pass_day(self):
        if self.voted and not self.has_day_shield:
            self.died = True
            return
        if self.voted and self.has_day_shield:
            self.has_day_shield = False

        self.voted = False

    def set_player(self, player):
        self.player = player

    def __str__(self):
        return str(self.player)

    @property
    def role_name(self):
        return type(self).__name__

    @property
    @abstractmethod
    def investigate_result(self):
        pass

    def shoot(self):
        self.shot = True

    def protect(self):
        self.protected = True

    def ban(self):
        self.banned = True

    def unban(self):
        self.banned = False

    def choose(self):
        self.voted = True

    @property
    def is_dead(self):
        return self.died


class Citizen(Role, ABC):
    def investigate_result(self):
        return False


class Mafia(Role, KillingAbility, ABC):
    def investigate_result(self):
        return True


class GodFather(Mafia):
    def investigate_result(self):
        return False

    def pass_night(self):
        self.protected = True
        super(GodFather, self).pass_night()


class SimpleMafia(Mafia):
    pass


class Negotiator(Mafia, NegotiateAbility):
    pass


class Nato(Mafia):
    pass


class HostageTaker(Mafia, PreventionAbility):
    def block(self, role) -> None:
        super(HostageTaker, self).block(role)


class DoctorLecter(Mafia, ProtectiveAbility):
    def heal(self, role) -> None:
        if self.banned:
            raise BannedException()
        return super(DoctorLecter, self).heal(role)


class Doctor(Citizen, ProtectiveAbility):
    def heal(self, role) -> None:
        if self.banned:
            raise BannedException()
        return super(Doctor, self).heal(role)


class Detective(Citizen, DetectiveAbility):
    def detect(self, role) -> bool:
        if self.banned:
            raise BannedException()
        return super(Detective, self).detect(role)


class Guard(Citizen, GuardingAbility):
    def unblock(self, role) -> None:
        if self.banned:
            raise BannedException()
        super(Guard, self).unblock(role)


class Armored(Citizen):
    def pass_night(self):
        self.protected = True
        super(Armored, self).pass_night()


class Investigator(Citizen, InvestigativeAbility):
    def investigate(self, first_role, sec_role) -> bool:
        if self.banned:
            raise BannedException()
        return super(Investigator, self).investigate(first_role, sec_role)


class Sniper(Citizen, KillingAbility):
    def kill(self, role) -> None:
        if self.banned:
            raise BannedException()
        if isinstance(role, Mafia):
            super(Sniper, self).kill(role)
        else:
            self.kicked = True
