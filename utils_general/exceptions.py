class UnknownBotException(Exception):
    def __init__(self, message='Ups, something goes wrong with the bot :(. Try again)'):
        self.message = message
        super(UnknownBotException, self).__init__(self.message)


class DatabaseUnknownException(Exception):
    def __init__(self, message='Ups, something goes wrong with connection :(. Try again)'):
        self.message = message
        super(DatabaseUnknownException, self).__init__(self.message)
