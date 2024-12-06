class classproperty:
    """
    Our old friend, the class property.
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, cls):
        return self.fget(cls)
