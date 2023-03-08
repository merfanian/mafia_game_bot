class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        role.set_player(self)

    def __str__(self):
        return self.name

    @property
    def details(self):
        return " ".join([self.name, str(self.role)])
