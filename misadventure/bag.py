import random


class Bag(set):
    """A collection of Items, such as in an inventory.

    Behaves very much like a set, but the 'in' operation is overloaded to
    accept a str item name, and there is a ``take()`` method to remove an item
    by name.

    """

    def find(self, name):
        """Find an object in the bag by name, but do not remove it.

        Return None if the name does not match.

        """
        for item in self:
            if name.lower() in item.aliases:
                return item
        return None

    def __contains__(self, v):
        """Return True if an Item is present in the bag.

        If v is a str, then find the item by name, otherwise find the item by
        identity.

        """
        if isinstance(v, str):
            return bool(self.find(v))
        else:
            return set.__contains__(v)

    def take(self, name):
        """Remove an Item from the bag if it is present.

        If multiple names match, then return one of them.

        Return None if no item matches the name.

        """
        obj = self.find(name)
        if obj is not None:
            self.remove(obj)
        return obj

    def get_random(self):
        """Choose an Item from the bag at random, but don't remove it.

        Return None if the bag is empty.

        """
        if not self:
            return None
        which = random.randrange(len(self))
        for index, obj in enumerate(self):
            if index == which:
                return obj

    def take_random(self):
        """Remove an Item from the bag at random, and return it.

        Return None if the bag is empty.

        """
        obj = self.get_random()
        if obj is not None:
            self.remove(obj)
        return obj
