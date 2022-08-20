class Event(list):
    # https://stackoverflow.com/a/2022629
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)
