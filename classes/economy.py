from constants import emojis


class EconomyException(Exception):
    pass


class NotEnoughMoneyError(EconomyException):
    def __init__(self, user):
        super().__init__()
        self.string = f"Sorry {user.mention}, you don't have enough money!"

    def __str__(self):
        return self.string


class NegativeMoneyException(EconomyException):
    def __init__(self, user):
        super().__init__()
        self.string = f"{emojis.laughing} {user.mention}, You think you can trick me into accepting less than minimum?"

    def __str__(self):
        return self.string


class InvalidMoneyException(EconomyException):
    def __init__(self, user):
        super().__init__()
        self.string = f"{emojis.laughing} {user.mention}, That's a invalid amount of $$$"

    def __str__(self):
        return self.string


def convert_to_money(input_cash, balance, minimum, user):
    if input_cash == "max" or input_cash == "all":
        return balance
    elif input_cash == "min":
        return minimum
    try:
        input_cash = int(input_cash)
    except ValueError:
        raise InvalidMoneyException(user)
    if input_cash > balance:
        raise NotEnoughMoneyError(user)
    elif input_cash < minimum:
        raise NegativeMoneyException(user)
    try:
        return int(input_cash)
    except ValueError:
        raise InvalidMoneyException(user)
