import uuid

from sibr import database


DEFAULT_STARTING_MONEY = 420


class Wallet:

    def __init__(self, id_, owner, money):
        self.id_ = id_
        self.owner = owner
        self.money = money

    @classmethod
    def load_by_id(cls, id_):
        wallet = database.get_wallet(id_=id_)
        if not wallet:
            return None
        return cls(wallet['id'], wallet['owner'], wallet['money'])

    @classmethod
    def load_by_owner(cls, owner):
        wallet = database.get_wallet(owner=owner)
        if not wallet:
            return None
        return cls(wallet['id'], wallet['owner'], wallet['money'])

    @classmethod
    def new(cls, owner, money=DEFAULT_STARTING_MONEY):
        return cls(str(uuid.uuid4()), owner, money)

    def save(self):
        database.set_wallet(self.id_, self.owner, self.money)

    def adjust(self, amount):
        self.money += amount
