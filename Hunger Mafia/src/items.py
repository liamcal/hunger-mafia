from collections import defaultdict
import sys
import inspect



class Item:
    def __init__(self, name, bonuses = defaultdict(int), ability = None, uses = None):
        self.name = name
        self.ability = ability
        self.bonuses = bonuses
        self.uses = uses
        self.usage = "Active" if uses is not None else "Passive"
    def __str__(self):
        return "{} Item: {}".format(self.usage, self.name) + (", Uses: {}".format(self.uses) if self.uses is not None else "")
    def __repr__(self):
        return str(self)

    def use(self):
        self.uses -= 1

#Passive Items
class HeavyArmour(Item):
    def __init__(self):
        super().__init__("Heavy Armour", defaultdict(int, {'Defence' : 2, 'Agility' : -1}))


class LightArmour(Item):
    def __init__(self):
        super().__init__("Light Armour", defaultdict(int, {'Defence' : 1}))


class BroadSword(Item):
    def __init__(self):
        super().__init__("Broad Sword", defaultdict(int, {'Strength' : 2, 'Agility' : -1}))


class Dagger(Item):
    def __init__(self):
        super().__init__("Dagger", defaultdict(int, {'Strength' : 1}))


class LuckySword(Item):
    def __init__(self):
        super().__init__("Lucky Sword", defaultdict(int, {'Strength' : 2, "Luck" : 1}))

class LuckyArmour(Item):
    def __init__(self):
        super().__init__("Lucky Armour", defaultdict(int, {'Defence' : 2, "Luck" : 1}))

class RunningShoes(Item):
    def __init__(self):
        super().__init__("Running Shoes", defaultdict(int, {'Agility' : 1}))


class LuckyCharm(Item):
    def __init__(self):
        super().__init__("Lucky Charm", defaultdict(int, {'Luck' : 1}))


#Boost Items
class StrengthSerum(Item):
    def __init__(self):
        super().__init__("Strength Serum", defaultdict(int, {'Strength' : 2}), ability = "StrengthSerum", uses = 1)


class DefenceSerum(Item):
    def __init__(self):
        super().__init__("Defence Serum", defaultdict(int, {'Defence' : 2}), ability = "DefenceSerum", uses = 1)


class AgilitySerum(Item):
    def __init__(self):
        super().__init__("Agility Serum", defaultdict(int, {'Agility' : 2}), ability = "AgilitySerum", uses = 1)


class LuckSerum(Item):
    def __init__(self):
        super().__init__("Luck Serum", defaultdict(int, {'Luck' : 2}), ability = "LuckSerum", uses = 1)



class Telescope(Item):
    def __init__(self):
        super().__init__("Telescope", ability = "Investigate", uses = 5)


class ScoutDrone(Item):
    def __init__(self):
        super().__init__("Scout Drone", ability = "Follow", uses = 1)


class Medpack(Item): #No self use
    def __init__(self):
        super().__init__("Medpack", ability = "Protect", uses = 5)


class Medicine(Item):
    def __init__(self):
        super().__init__("Medicine", ability = "Heal", uses = 1)


class TrapKit(Item):
    def __init__(self):
        super().__init__("Trap Kit", ability = "Trap", uses = 3)


class Trap(Item):
    def __init__(self):
        super().__init__("Trap", ability = "Trap", uses = 1)


class PoisonDart(Item):
    def __init__(self):
        super().__init__("Poison Dart", ability = "Poison", uses = 1)


class StickyBombs(Item):
    def __init__(self):
        super().__init__("Sticky Bombs", ability = "Bomb", uses = 1)




def create_item(item_name):
    return item_lookup[item_name]()

#Reflection is cool yo
item_lookup = {name:obj for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)}
