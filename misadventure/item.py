from misadventure.bag import LockedBag


class Item:
    """A generic item object that can be referred to by a number of names."""

    def __init__(self, name, *aliases):
        self.name = name
        self.aliases = tuple(
            label.lower()
            for label in (name,) + aliases
        )

    def __repr__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join(repr(n) for n in self.aliases)
        )

    def __str__(self):
        return self.name


class Key(Item):
    def __init__(self, name, keycode, *aliases):
        super().__init__(name, aliases)
        self.keycode = keycode

    def fits(self, lockable: LockedBag):
        if lockable.keycode == self.keycode:
            return True
        return False
