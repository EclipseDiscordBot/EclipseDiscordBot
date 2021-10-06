from constants import emojis
from constants.economy import basic


class EconomyException(Exception):
    pass


class NotEnoughMoneyError(EconomyException):
    def __init__(self, user):
        super().__init__()
        self.string = f"Sorry {user.mention}, you don't have enough money or you're exceeding the limit!"

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
        self.string = f"{emojis.laughing} {user.mention}, That's a invalid amount of {basic.currency_emoji}"

    def __str__(self):
        return self.string


def convert_to_money(input_cash, balance, minimum, user):
    input_cash = str(input_cash).lower()
    if input_cash == "max" or input_cash == "all":
        return balance
    elif input_cash == "min":
        return minimum
    try:
        input_cash = int(input_cash)
    except ValueError:
        if input_cash[-1] == "k":
            input_cash = input_cash[0:-1] + "000"
            try:
                input_cash = int(input_cash)
            except ValueError:
                raise InvalidMoneyException(user)
    if input_cash > balance:
        raise NotEnoughMoneyError(user)
    elif input_cash < minimum:
        raise NegativeMoneyException(user)
    try:
        input_cash = int(input_cash)
    except ValueError:
        raise InvalidMoneyException(user)
    return input_cash
