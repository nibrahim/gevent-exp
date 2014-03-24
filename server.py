from gevent import Greenlet
from gevent.server import StreamServer

class Pretty(object):
    def __repr__(self):
        return "<{} : {}>".format(self.__class__.__name__, self.name)

class Person(Pretty, Greenlet):
    def __init__(self, name, socket, room = None, items = None):
        Greenlet.__init__(self)
        self.name = name
        self.room = room
        self.items = items or []
        self.socket = socket
    
    def send(self, message):
        self.socket.send(message+"\n")

    
    def inventory(self):
        return "You are carrying \n" + "\n".join(" %s"%x.name for x in self.items) + "\n"
        

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


class Mansion():
    def __init__(self, rooms):
        self.rooms = rooms
        self.people = {}
        for r in self.rooms:
            for p in r.people:
                self.people[p] = r

    def place(self, person, room):
        print "Placing %s in %s"%(person, room)
        self.people[person] = room
        person.room = room
        room.people.append(person)
    
    def remove(self, person):
        print "%s is leaving"%person
        person.room.people.remove(person)
        del self.people[person]

    def move(self, person, room):
        if not room:
            r = "I'm afraid you can't go that way"
        else:
            r = "You move into the %s"%room.name
            self.people[person] = room
            person.room.people.remove(person)
            person.room = room
            person.room.people.append(person)
        return r

    
    def room_info(self, person):
        info =  """You are currently in the {}.
        
{}""".format(person.room.name, person.room.description)

        things = ""
        if person.room.items:
            things = "I can see the following things here - {}".format(", ".join(x.name for x in person.room.items))
        
        people = ""
        if [x for x in person.room.people if x is not person]:
            people = "The following people are in the room - {}".format(", ".join(x.name for x in person.room.people if x is not person))
        
        return "\n".join([info, things, people])

    def pick_up(self, person, item_name):
        item = [x for x in person.room.items if x.name == item_name]
        item = item and item[0]
        if item:
            person.room.items.remove(item)
            person.items.append(item)
            return "You pick up the %s\n"%item.name
        else:
            return "I see no %s here"%item_name
            
    def send_message(self, frm, to, message):
        if to in [x.name for x in frm.room.people]:
            to = [x for x in frm.room.people if x.name == to][0]
            to.send("%s says '%s'"%(frm.name, message))
            return "Let's see if %s heard you"%to.name
        else:
            return "I don't see %s here\n"%to
                
    
    def handle(self, socket, remote):
        print "Received connection on %s"%socket
        socket.send("What is your name?\n")
        name = socket.recv(2048).strip()
        p = Person(name = name, socket = socket)
        print "Created %s"%p
        self.place(p, self.rooms[0])
        socket.send(self.room_info(p))
        while True:
            socket.send("\nWhat do you want to do now?\n")
            command = socket.recv(2048).strip()
            if command == "quit":
                socket.send("Goodbye\n")
                self.remove(p)
                return
            if command == "look":
                socket.send(self.room_info(p))
            if command in ["north", "south", "east", "west"]:
                socket.send(self.move(p, getattr(p.room, command)))
            if command == "inventory":
                socket.send(p.inventory())
            if command.startswith("get"):
                verb, item = command.split()
                socket.send(self.pick_up(p, item))
            if command.startswith("say"):
                verb, person, message = command.split(None, 2)
                socket.send(self.send_message(p, person, message))
            
        
def main():
    # Items
    knife = Item("Knife", "A rusty and blunt knife")
    ladle = Item("Ladle", "A wooden ladle")
    carafe = Item("Carafe", "A crystal carafe. Surprisingly undamaged and clean")
    sword = Item("Sword", "A very well made but ancient sword")
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
    server = StreamServer(('127.0.0.1', 5000), m.handle)
    print "Server ready"
    server.serve_forever()


if __name__ == '__main__':
    import sys
    sys.exit(main())

