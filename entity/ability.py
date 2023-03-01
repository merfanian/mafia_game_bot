from abc import ABC


class VotingAbility(ABC):
    def vote(self, role):
        role.choose()


class InvestigativeAbility(ABC):
    def investigate(self, first_role, sec_role) -> bool:
        return True if first_role.investigate_result() == sec_role.investigate_result() else False


class DetectiveAbility(ABC):
    def detect(self, role) -> bool:
        return role.investigate_result()


class PreventionAbility(ABC):
    def block(self, role) -> None:
        role.ban()


class GuardingAbility(ABC):
    def unblock(self, role) -> None:
        role.unban()


class ProtectiveAbility(ABC):
    def heal(self, role) -> None:
        role.protect()


class KillingAbility(ABC):
    def kill(self, role) -> None:
        role.shoot()


class NegotiateAbility(ABC):
    def negotiate(self, role):
        pass
