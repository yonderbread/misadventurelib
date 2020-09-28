from copy import deepcopy

from misadventure.bag import Bag
from misadventure.lib import InvalidState, InvalidDirection, InvalidCommand, Collection


class RoomState:
    def __init__(self, description: str = '', *names: str):
        self.names = Collection()
        self.description = description if not description or len(description) == 0 else description.strip()

        self._directions = {}
        self.bag = Bag()

        if len(names) > 0:
            self.add_names(names)

    def __str__(self):
        return self.description

    def add_names(self, *names):
        self.names.add(names)

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


class Room(RoomState):
    """A generic room object that can be used by game code."""
    """Can have multiple states that can be switched"""

    def __init__(self):
        self._current_state = None
        self._states = {}

    def add_state(self, name: str, state: RoomState, pass_directions=False):
        self._states[name] = state

    def get_state(self, name: str):
        if name in self._states:
            return self._states[name]
        raise InvalidState(f'Room {self.names[0]} does not have a state called %r')

    def set_state(self, name: str):
        state = self.get_state(name)
        if not state:
            return False
        self._current_state = state
        return True

    @property
    def current_state(self):
        return self._current_state


Room.add_direction('north', 'south')
Room.add_direction('east', 'west')
