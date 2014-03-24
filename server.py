import gevent

from gevent.pool import Pool

pool = Pool(2)

class Pretty(object):
    def __repr__(self):
        return "<{} : {}>".format(self.__class__.__name__, self.name)

class Person(Pretty):
    def __init__(self, name, room = None):
        self.name = name
        self.room = room

class Item(Pretty):
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Room(Pretty):
    def __init__(self, name, description, items = None, people = None):
        self.name = name
        self.description = description
        self.items = items or []
        self.people = people or []
        self.north = self.south = self.east = self.west = None

class Mansion(Pretty):
    def __init__(self, rooms):
        self.rooms = rooms
        self.people = {}
        for i in self.rooms:
            for p in i.people:
                self.people[p] = i
        
def main():
    # Items
    knife = Item("Knife", "A rusty and blunt knife")
    ladle = Item("Ladle", "A wooden ladle")
    carafe = Item("Carafe", "A crystal carafe. Surprisingly undamaged and clean")
    sword = Item("Ornamental sword", "A very well made but ancient sword")
    # Rooms
    garden = Room("Garden", "This is an old an unkempt garden. Weeds peek out from crumbling statues and dry fountains")
    hallway = Room("Hallway", "A high roofed hallway now empty and foreboding", items = [sword])
    dining = Room("Dining room", "A room that must once have seen many feasts now broken and unusable", items = [carafe])
    kitchen = Room("Kitchen", "Mouldy and damp, this kitchen is not even a shadow of it's former self", items = [knife, ladle])
    # Lay out the rooms.
    garden.north = hallway
    hallway.south = garden
    hallway.north = dining
    dining.south = hallway
    dining.east = kitchen
    kitchen.west = dining
    
    m = Mansion([garden, hallway, dining, kitchen])
    


if __name__ == '__main__':
    import sys
    sys.exit(main())

