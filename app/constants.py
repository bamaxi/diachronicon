class NoDate:
    def __lt__(self, other):
        return True

    def __gt__(self, other):
        return False


NO_DATE = NoDate()
