from copy import deepcopy

from misadventure.bag import Bag
from misadventure.lib import InvalidDirection, InvalidCommand


class RoomState:
    def __init__(self, description: str = ''):
        self._directions = {}
        self.names = []
        self.description = description if not description or len(description) == 0 else description.strip()

    def add_name(self, name):


    def add_direction(self, forward, reverse):
        for direction in (forward, reverse):
            if not direction.islower():
                raise InvalidCommand('Invalid direction %r: directions must be all lowercase.')
            if direction in Room.directions:
                raise KeyError('Direction %r is already defined.')

            self._directions[forward] = reverse
            self._directions[reverse] = forward

            setattr(self, forward, None)
            setattr(self, reverse, None)

    def __str__(self):
        return


class Room:
    """A generic room object that can be used by game code."""

    _states = {}

    def __init__(self, description):
        self.description = description.strip()

        # Copy class Bags to instance variables
        for k, v in vars(type(self)).items():
            if isinstance(v, Bag):
                setattr(self, k, deepcopy(v))

    def __str__(self):
        return self.description

    def exit(self, direction):
        """Get the exit of a room in a given direction.

        Return None if the room has no exit in a direction.

        """
        if direction not in self._directions:
            raise KeyError('%r is not a direction' % direction)
        return getattr(self, direction, None)

    def exits(self):
        """Get a list of directions to exit the room."""
        return sorted(d for d in self._directions if getattr(self, d))

    def __setattr__(self, name, value):
        if isinstance(value, Room):
            if name not in self._directions:
                raise InvalidDirection(
                    '%r is not a direction you have declared.\n\n' +
                    'Try calling Room.add_direction(%r, <opposite>) ' % name +
                    ' where <opposite> is the return direction.'
                )
            reverse = self._directions[name]
            object.__setattr__(self, name, value)
            object.__setattr__(value, reverse, self)
        else:
            object.__setattr__(self, name, value)

    @property
    def directions(self):
        return self._directions


Room.add_direction('north', 'south')
Room.add_direction('east', 'west')
