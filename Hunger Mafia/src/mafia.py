import random
import math
import csv
import pickle
import inspect
import items

from datetime import datetime
import os

from collections import defaultdict

### 3 Prime numbers were crowdsourced from the FB group:
###     2, 2, 11
### Posted https://www.facebook.com/groups/mafiatalk/permalink/1426529537387496/
### The primers were multiplied to create a "base seed": 44
### The following code was used to 20 random ints
### >>> import random
### >>> import sys
### >>> n = sys.maxsize
### >>> random.seed(44)
### >>> seeds = [random.randint(0,n) for i in range(20)]
### The results have been listed below.
### The first of these seeds will be used for character generation
### The remaining will be used for each day of interactions


SEEDS = [2151912510308904607,
    7001809708520175019,
    5341588635875806718,
    4144733424624790250,
    1847996772488648164,
    5589041337376663636,
    6609180008168331154,
    6250142495147320794,
    5215440844834605935,
    2933925388415541400,
    4980649371989803730,
    5818628277182135931,
    5344152360886571796,
    355845256498772596,
    1767436721077155009,
    8782614287306659312,
    3515592806304924800,
    2398862801835107410,
    801415449963703942,
    6816332173560420283]
### A comma-seperated string of each seed value has been SHA1 hashed
### >>> import hashlib
### >>> sha = hashlib.sha1(b'2151912510308904607,7001809708520175019,5341588635875806718,4144733424624790250,1847996772488648164,5589041337376663636,6609180008168331154,6250142495147320794,5215440844834605935,2933925388415541400,4980649371989803730,5818628277182135931,5344152360886571796,6355845256498772596,1767436721077155009,8782614287306659312,3515592806304924800,2398862801835107410,801415449963703942,6816332173560420283').hexdigest()
### The resulting hash is
###     fd20c9208265cafb24329e0bc3457617d9da469e
### Posted https://www.facebook.com/groups/mafiatalk/permalink/1426539054053211/

ATTRIBUTES = ["Strength", "Defence", "Agility", "Luck"]
TRACE = True

def invnormalcdf(x, mu = 0, sigma = 1):
    z = (x - mu) / sigma
    return 1 - ((1.0 + math.erf(z / math.sqrt(2.0)))/2)

def pickle_obj(path, obj):
    with open(path, "wb") as f:
        pickle.dump(obj,f)
def unpickle_obj(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def write_player_file(path, player_dicts):
    with open(path, 'w', newline='') as f:
        wrt = csv.DictWriter(f, ["Name"] + ATTRIBUTES + ["Holding"])
        wrt.writeheader()
        wrt.writerows(player_dicts)


def print_results(name, target, roll):
    result = "Pass" if roll >= target else "Fail"
    print("{} Check. Target: {}, Roll: {}, Result: {}".format(name, target, roll, result))

def getBlankDD():
    return defaultdict(int)

class Player:
    def __init__(self, name, preferences, advantage):
        self.name = name
        self.preferences = preferences
        self.inventory = []
        self.status = defaultdict(list)
        self.actions = defaultdict(list)
        self.action_bonus = defaultdict(getBlankDD)
        self.response_bonus = [2,1,0] if advantage else [1,0,0]
        self.is_kingpin = False
        self.is_career = False
        self.is_alive = True
        self.stats = self._initialise_stats()
        self.id = None
        self.district = None
        self.death_text = None



    def __repr__(self):
        return self.name
    def __str__(self):
        return "{}: {}, District: {}{}.\n\tStrength: {Strength}, Defence: {Defence}, Agility: {Agility}, Luck: {Luck}".format(self.name, ("Living" if self.is_alive else "Dead"), self.district, (", Career" if self.is_career else ""), **self.stats) + ("\n\tHolding: {}".format(self.inventory) if self.inventory else "")

    def get_dict(self):
        return dict({"Name": self.name, "Holding":", ".join(i.name for i in self.inventory)}, **self.stats)

    def _initialise_stats(self):
        calculated_stats = {a:0 for a in ATTRIBUTES}
        for _ in range(20):
            calculated_stats[random.choice(ATTRIBUTES)] += 1
        bonuses = self._calculate_response_bonuses()
        for b in bonuses:
            calculated_stats[b] += bonuses[b]
        return calculated_stats

    def _calculate_response_bonuses(self):
        bonuses = [0,0,0]
        for _ in range(7):
            bonuses[random.choice(range(3))] += 1
        bonuses = [sum(x) for x in zip(sorted(bonuses, reverse=True), self.response_bonus)]
        b = {self.preferences[i]:bonuses[i] for i in range(3)}
        return b

    def _apply_luck(self):
        return 1 if random.random() >= invnormalcdf(self.stats['Luck'],7,3) else 0

    def _get_item_bonus(self,stat):
        result = sum(x.bonuses[stat] for x in self.inventory if x.usage == "Passive")
        return result if result is not None else 0

    def get_stat(self,stat, debug = False):
        a,b,c,d = self.stats[stat], self._apply_luck(), self.action_bonus[CURRENT_PHASE][stat], self._get_item_bonus(stat)
        x = a + b + c + d
        if debug:
            print("{} has a {} stat of {}, ({})".format(self.name, stat, x, [a,b,c,d]))
        return x

    def record_action(self, action, target = None):
        if target is None:
            target = self
        self.actions[CURRENT_PHASE].append((action, target))
        print("Recording action {} {} {}".format(self.name, action, target.name))

    def held_bombs(self):
        return self.get_usable_items("Bomb")

    def set_dead(self, killer = None):
        self.is_alive = False
        print("{} is now dead".format(self.name))
        if killer is not None:
            grenades = self.held_bombs()
            if grenades:
                self.use_item(grenades[0])
                self.bomb(killer, threshold = 0.25)


    def hide(self):
        self.record_action('Hide')
        self.action_bonus[CURRENT_PHASE]['Agility'] += 4
        print("{} successfully hides".format(self.name))

    def guard(self):
        self.record_action('Guard')
        self.action_bonus[CURRENT_PHASE]['Defence'] += 2
        print("{} successfully guards".format(self.name))


    def get_usable_items(self, ability_name):
        return [i for i in self.inventory if i.ability == ability_name and i.uses]

    def drink_serum(self, serum):
        self.record_action('Drink ' + serum.name)
        for stat in serum.bonuses:
            self.action_bonus[CURRENT_PHASE][stat] += serum.bonuses[stat]
        self.use_item(serum)
        print("{} successfully drinks {}".format(self.name, serum.name))


    def add_item(self, item):
        self.inventory.append(item)

    def use_item(self, item):
        if not item.uses:
            print("{} tried to use {}, but failed as it has no more uses: {}".format(player.name, item.name, item.uses))
        else:
            item.use()
            print ("{} used {}, remaining uses: {}".format(self.name, item.name, item.uses))
            if not item.uses:
                print("{} is destroyed".format(item.name))
                self.inventory.remove(item)

    def apply_status(self, status):
        self.status[CURRENT_PHASE].append(status)

    def poison_death_check(self):
        if CURRENT_PHASE < 3:
            return False
        return any("Poisoned" in self.status[i] for i in range(1, CURRENT_PHASE - 2))

    def heal_poison(self):
        for i in range(1, CURRENT_PHASE):
            if "Poisoned" in self.status[i]:
                print("{} was poisoned on Night {}".format(self.name, CURRENT_PHASE))
                self.status[i] = [x for x in self.status[i] if x != "Poisoned"]
                print("{} has been healed of Poisoning.".format(self.name))

    def action_on_cooldown(self, action):
        for i in range(CURRENT_PHASE - 3, CURRENT_PHASE + 1):
            if i > 0:
                if self.actions[i]:
                    if any(m[0] == action for m in self.actions[i]):
                        print("{} has used {} on Night {}".format(self.name, action, i))
                        return True
        return False
        # return any(action in self.actions[CURRENT_PHASE - i] for i in range(4) if CURRENT_PHASE - i > 0)


    def can_perform_any_action(self):
        return "Trapped" not in self.status[CURRENT_PHASE] and self.is_alive

    def is_protected(self):
        return "Protected" in self.status[CURRENT_PHASE]

    def perform_item_action(self, target, action):
        available_items = self.get_usable_items(action)
        if available_items:
            selected_item = available_items[0]
            if target.is_alive:
                self.use_item(selected_item)
                self.record_action(action, target)
                if action == "Investigate":
                    return self.investigate(target)
                elif action == "Follow":
                    return self.follow(target)
                elif action == "Protect":
                    return self.protect(target)
                elif action == "Heal":
                    return self.heal(target)
                elif action == "Trap":
                    return self.trap(target)
                elif action == "Poison":
                    return self.poison(target)
                elif action == "Bomb":
                    return self.bomb(target)
            else:
                print("Target {} is already dead".format(target.name))
                return "Failed - Target Dead"



    def investigate(self, target):
        if target.is_alive:
            if target != self:
                print("{} successfully investigates {} and learns they are {}, and their stats are {}".format(self.name, target.name, "Career" if target.is_career else "Tribute" , target.stats))
                return "Success: {}".format("Career" if target.is_career else "Tribute")
            else:
                print("{} tried to investigate {} but failed as they cannot protect themself".format(self.name, target.name))
                return "Failed: Self Target"
        else:
            print("{} tried to investigates {} but failed as the target is already dead".format(self.name, target.name))
            return "Failed: Target already dead"

    def follow(self, target):
        if target.is_alive or "Night {}".format(CURRENT_PHASE) in target.death_text:
            print("{} successfully follows {} and learns they performed {}".format(self.name, target.name, target.actions[CURRENT_PHASE]))
            return "Success: {}".format(target.actions[CURRENT_PHASE])
        else:
            print("{} tried to investigates {} but failed as the target is already dead".format(self.name, target.name))
            return "Failed: Target already dead"


    def protect(self, target):
        if target.is_alive:
            if target != self:
                target.apply_status("Protected")
                target.heal_poison()
                print("{} successfully protected {}".format(self.name, target.name))
                return "Success"
            else:
                print("{} tried to protect {} but failed as they cannot protect themself".format(self.name, target.name))
                return "Failed: Self Target"
        else:
            print("{} tried to protect {} but failed as the target is already dead".format(self.name, target.name))
            return "Failed: Target already dead"

    def heal(self, target):
        if target.is_alive:
            target.apply_status("Protected")
            target.heal_poison()
            print("{} successfully healed {}".format(self.name, target.name))
            return "Success"
        else:
            print("{} tried to protect {} but failed as the target is already dead".format(self.name, target.name))
            return "Failed: Target already dead"

    def trap(self, target):
        if target.is_alive:
            if target != self:
                target.apply_status("Trapped")
                print("{} successfully trapped {}".format(self.name, target.name))
                return "Success"
            else:
                print("{} tried to trap {} but failed as they cannot protect themself".format(self.name, target.name))
                return "Failed: Self Target"
        else:
            print("{} tried to trap {} but failed as the target is already dead".format(self.name, target.name))
            return "Failed: Target already dead"

    def poison(self, target):
        if target.is_alive:
            if target != self:
                target.apply_status("Poisoned")
                print("{} successfully poisoned {}".format(self.name, target.name))
                return "Success"
            else:
                print("{} tried to poison {} but failed as they cannot protect themself".format(self.name, target.name))
                return "Failed: Self Target"
        else:
            print("{} tried to poison {} but failed as the target is already dead".format(self.name, target.name))
            return "Failed: Target already dead"

    def bomb(self, target, threshold = 0.5):
        if self._apply_luck():
            threshold -= 0.2
        roll = random.random()
        result = roll >= threshold
        print("{} tries to bomb {}. Threshold: {}, roll: {}".format(self.name, target.name, threshold, roll))
        if result:
            target.set_dead(killer = self)
            print("{} has been killed in an explosion".format(target.name))
            target.death_text = "Killed by a bomb from {} on Night {}".format(self.name, CURRENT_PHASE)
            if target.inventory:
                print("The following items were destroyed {}".format(target.inventory))
                target.inventory = []
            return "Success"
        else:
            print("{} has dodged an explosion".format(target.name))
            return "Failed: Dodged"


        # if target.is_alive:
        #     if target != self:
        #         target.apply_status("Bombed")
        #         print("{} successfully attached a bomb to {}".format(self.name, target.name))
        #         return "Success"
        #     else:
        #         print("{} tried to attach a bomb to {} but failed as they cannot protect themself".format(self.name, target.name))
        #         return "Failed: Self Target"
        # else:
        #     print("{} tried to attach a bomb to {} but failed as the target is already dead".format(self.name, target.name))
        #     return "Failed: Target already dead"



    def attack(self, other, career_kill = False):
        if career_kill:
            self.record_action("Kill", other)
            self.action_bonus[CURRENT_PHASE]['Strength'] += 4
            print("{} attempts a Career kill on {}".format(self.name, other.name))
        else:
            self.record_action("Attack", other)
            print("{} attempts an attack on {}".format(self.name, other.name))

        search_result = self.search_check(other)
        if not search_result:
            print( "Attack Failed, {} could not locate {}".format(self.name, other.name))
            if career_kill:
                self.action_bonus[CURRENT_PHASE]['Strength'] -= 4 #remove the bonus
            return CombatOutcome.hidden
        else:
            combat_result = self.combat(other)
            if career_kill:
                self.action_bonus[CURRENT_PHASE]['Strength'] -= 4 #remove the bonus
            return combat_result


    def combat(self, other):
        attack_result = self.attack_check(other)
        if attack_result == CombatOutcome.success:
            if other.is_protected():
                print( "Attack Prevented, {} tried to kill {}, but failed as target is protected".format(self.name, other.name))
                return CombatOutcome.success_protected
            else:
                other.set_dead(killer = self)
                # other.is_alive = False
                other.death_text = "Killed by {} on Night {}".format(self.name, CURRENT_PHASE)
                print( "Attack Succeeded, {} killed {}".format(self.name, other.name))
        elif attack_result == CombatOutcome.failed:
            print( "Attack Failed, {} defended against {}".format(other.name, self.name))
        elif attack_result == CombatOutcome.countered:
            if self.is_protected():
                print( "Counter Prevented, {} was countered by {}, but survived as they are protected".format(self.name, other.name))
                return CombatOutcome.countered_protected
            else:
                self.set_dead(killer = other)
                # self.is_alive = False
                other.death_text = "Counter killed by {} on Night {}".format(other.name, CURRENT_PHASE)
                print( "Attack Failed, {} was counter killed by {}".format(self.name, other.name))
        return attack_result


    def search_check(self, other):
        a1 = self.get_stat('Agility', TRACE)
        a2 = other.get_stat('Agility', TRACE)
        # a1 = self.stats['Agility'] + self.apply_luck()
        # a2 = other.stats['Agility']+ other.apply_luck() + (5 if other.agility_bonus else 0)
        agility_delta = a1 - a2
        if CURRENT_PHASE > 7:
            ###Fatigue Mode
            target = invnormalcdf(agility_delta,-4,4)
        else:
            target = invnormalcdf(agility_delta,-1,4)
        roll = random.random()
        print_results("Search", target, roll)
        return roll >= target

    def attack_check(self, other):
        s1 = self.get_stat('Strength', TRACE)
        # s1 = self.stats['Strength'] + self.apply_luck()
        d2 = other.get_stat('Defence', TRACE)
        # d2 = other.stats['Defence']+ other.apply_luck() + (3 if other.defence_bonus else 0)
        combat_delta = s1 - d2
        if CURRENT_PHASE > 7:
            ###Fatigue Mode
            target = invnormalcdf(combat_delta,-1,4)
        else:
            target = invnormalcdf(combat_delta,0,4)
        roll = random.random()
        print_results("Attack", target, roll)
        result =  roll >= target
        if result:
            return CombatOutcome.success
        else:
            return CombatOutcome.countered if self.counter_check(other, 1-roll) else CombatOutcome.failed

    def counter_check(self, other, roll):
        d1 = self.get_stat('Defence', TRACE)
        # d1 = self.stats['Defence'] + self.apply_luck()
        s2 = other.get_stat('Strength', TRACE)
        # s2 = other.stats['Strength'] + other.apply_luck()
        combat_delta = s2 - d1
        if CURRENT_PHASE > 7:
            target = invnormalcdf(combat_delta,2,4)
        else:
            target = invnormalcdf(combat_delta,3,4)
        print_results("Counter", target, roll)
        result = roll >= target
        return result

    def raid(self, other):
        if other.inventory:
            raided_item = random.choice(other.inventory)
            self.add_item(raided_item)
            other.inventory.remove(raided_item)
            print("Player: {} raided a {} from {}".format(self.name, raided_item.name, other.name))
        else:
            print("Player: {} attempted to raid from {}, but was unsuccessful as they were not carrying anything".format(self.name, other.name))

#An "Enum of CombatOutcome results"
class CombatOutcome:
    hidden = [] #hacky way so CombatOutcome.hidden != CombatOutcome.failed
    failed = 0  #but at least they're both false, that's good right?
    success = 1
    success_protected = 2
    countered = -1
    countered_protected = -2

class Game:

    def __init__(self, name = "game"):
        self.current_phase = 0
        self.game_name = name
        self.players = {}
        self.kingpin = None
        self.careers = []
        self.night_actions = {}
        self.action_priotities = {"Serum" : -10, "Trap" : -5, "Heal" : -1, "Protect" : -1, "Investigate" : -1, "Bomb" : - 1, "Poison" : -1, "Hide" : 1, "Guard" : 2, "Attack" : 3, "Kill": 3, "Follow" : 5}
        self.cooldown_actions = {"Attack", "Guard", "Hide"}
        self.dropped_items = []

    def set_phase(self, phase):
        self.current_phase = phase
        random.seed(SEEDS[self.current_phase])

    def get_action_priority(self, action):
        return self.action_priotities[action] if action in self.action_priotities else 0

    def get_players_from_csv(self, path):
        with open(path) as f:
            rdr = csv.DictReader(f)
            retrieved_players = [self.get_player_by_name(line["Name"]) for line in rdr]
            return retrieved_players

    def get_players(self):
        return sorted(list(self.players.values()), key = lambda x: x.id)

    def get_living_players(self):
        return [p for p in self.get_players() if p.is_alive]

    def get_player_by_name(self, name):
        return self.players[name]

    def set_careers(self, *names):
        for name in names:
            cur_player = self.get_player_by_name(name)
            cur_player.is_career = True
            self.careers.append(cur_player)

    def create_players_from_responses(self, path):
        with open(path) as f:
            rdr = csv.DictReader(f)
            for i, line in enumerate(rdr):
                current_info = line
                current_preferences = {}
                for stat in line:
                    n = line[stat]
                    if n in '012':
                        current_preferences[int(n)] = stat
                p = Player(current_info['Name'], current_preferences, True if line['Bonus'] == 'T' else False)
                p.id = i
                p.district = (i // 2) + 1
                self.players[p.name] = p


    def create_days_items(self, day):
        with open("ItemDrops.csv") as f:
            lines = list(csv.DictReader(f))
        line = [line for line in lines if line["Day"] == str(day)]
        if len(line) > 1:
            raise ValueError("More than one entry for Day {}".format(day))
        elif len(line) == 1:
            line = line[0]
            new_items = [items.create_item(s) for s in line["Items"].split()]

            return new_items
        else:
            return []

    def assign_items_to_players(self, recipients, items, day):
        ###This only records a day at a time, should really have made this
        with open("Item_Assignments.csv", 'w', newline='') as f:
            wrt = csv.DictWriter(f, ["Player", "Item"])
            wrt.writeheader()
            for index, item in enumerate(items):
                recipients[index].add_item(item)
                print("{} retrieved {}". format(recipients[index].name, item.name))
                wrt.writerow({"Player": recipients[index].name, "Item": item.name})

    def distribute_sponsor_items(self, day):
        sponsor_items = self.create_days_items(day)
        random.shuffle(sponsor_items)
        recipients = self.stat_based_selection(selection_players = self.get_living_players(), selection_stats = ['Luck'], positive = True, n = len(sponsor_items))
        self.assign_items_to_players(recipients, sponsor_items, day)


    def run_feast(self, feast_players):

        random.seed(SEEDS[-1]) #Feast uses different seed to night
        new_items = self.create_days_items(-1)
        players_retrieved_item = self.stat_based_selection(selection_players = feast_players, selection_stats = ['Luck', 'Agility'], positive = True, n = len(new_items))

        with open("Feast_results.csv", 'w', newline='') as f:
            wrt = csv.DictWriter(f, ["Player", "Action", "Target", "Result"])
            wrt.writeheader()


            for index, item in enumerate(new_items):
                players_retrieved_item[index].add_item(item)

                print("{} retrieved new item {}". format(players_retrieved_item[index].name, item.name))
                wrt.writerow({"Player": players_retrieved_item[index].name, "Action": "receives", "Target": item.name })


            ranked_players = self.stat_based_selection(selection_players = feast_players, selection_stats = ['Luck', 'Agility'], positive = True, n = len(feast_players))
            while self.dropped_items:
                if not ranked_players:
                    ranked_players = self.stat_based_selection(selection_players = feast_players, selection_stats = ['Luck', 'Agility'], positive = True, n = len(feast_players))
                cur_player = ranked_players.pop(0)
                cur_item = self.dropped_items.pop()
                cur_player.add_item(cur_item)

                print("{} retrieved {}". format(cur_player.name, cur_item.name))
                wrt.writerow({"Player": cur_player.name, "Action": "receives", "Target": cur_item.name })

            ###FEAST COMBAT
            n_combats = 2
            has_fought = set()
            for c in range(n_combats):
                p1, p2 = self.stat_based_selection(selection_players = feast_players, selection_stats = ['Luck', 'Agility'], positive = False, n = 2)
                while p1.is_career and p2.is_career or p1 in has_fought or p2 in has_fought:  #Careers shouldnd't fight each other, and one fight per person
                    p1, p2 = self.stat_based_selection(selection_players = feast_players, selection_stats = ['Luck', 'Agility'], positive = False, n = 2)
                has_fought.add(p1)
                has_fought.add(p2)
                p1a, p2a = p1.get_stat('Agility'), p2.get_stat("Agility")

                #Faster player goes on the attack (generally better even if you have low strength)
                if p1a > p2a:
                    attacking = p1
                    defending = p2
                #break ties based on when you submitted
                elif p1a == p2a:
                    if feast_players.index(p1) > feast_players.index(p2):
                        attacking = p1
                        defencing = p2
                    else:
                        attacking = p2
                        defending = p1
                else:
                    attacking = p2
                    defending = p1

                print("Cornucopia Combat {} vs {}".format(attacking.name, defending.name))


                combat_res = attacking.combat(defending)

                if combat_res == CombatOutcome.success:
                    attacking.raid(defending)
                    self.player_item_drop(defending)
                    outcome = "Success"
                elif combat_res == CombatOutcome.countered:
                    defending.raid(attacking)
                    self.player_item_drop(attacking)
                    outcome = "Countered"
                elif combat_res == CombatOutcome.failed:
                    outcome = "Failed"

                wrt.writerow({"Player": attacking.name, "Action": "attacks", "Target": defending.name, "Result": outcome })

        random.seed(SEEDS[self.current_phase]) #Restore the seed to normal

    def run_cornucopia(self, cornucopia_players):
        print("Running Cornucopia:", cornucopia_players)
        with open("Cornucopia_results.csv", 'w', newline='') as f:
            wrt = csv.DictWriter(f, ["Player", "Action", "Target", "Result"])
            wrt.writeheader()

            available = self.create_days_items(0)
            random.shuffle(available)

            ranked_players = sorted(cornucopia_players, reverse = True, key = lambda x : x.stats['Luck'] + x.stats['Agility'])
            for index, item in enumerate(available):
                ranked_players[index].add_item(item)

                print("{} retrieved {}". format(ranked_players[index].name, item.name))
                wrt.writerow({"Player": ranked_players[index].name, "Action": "receives", "Target": item.name })

            ### Run cornucopia combat
            n_combats = len(cornucopia_players) // 7

            for c in range(n_combats):
                p1, p2 = self.stat_based_selection(selection_players = cornucopia_players, selection_stats = ['Luck', 'Agility'], positive = False, n = 2)
                while p1.is_career and p2.is_career:  #Careers shouldnd't fight each other
                    p1, p2 = self.stat_based_selection(selection_players = cornucopia_players, selection_stats = ['Luck', 'Agility'], positive = False, n = 2)
                p1a, p2a = p1.get_stat('Agility'), p2.get_stat("Agility")

                #Faster player goes on the attack (generally better even if you have low strength)
                if p1a > p2a:
                    attacking = p1
                    defending = p2
                #break ties based on when you submitted
                elif p1a == p2a:
                    if cornucopia_players.index(p1) > cornucopia_players.index(p2):
                        attacking = p1
                        defencing = p2
                    else:
                        attacking = p2
                        defending = p1
                else:
                    attacking = p2
                    defending = p1

                print("Cornucopia Combat {} vs {}".format(attacking.name, defending.name))


                combat_res = attacking.combat(defending)

                if combat_res == CombatOutcome.success:
                    attacking.raid(defending)
                    self.player_item_drop(defending)
                    outcome = "Success"
                elif combat_res == CombatOutcome.countered:
                    defending.raid(attacking)
                    self.player_item_drop(attacking)
                    outcome = "Countered"
                elif combat_res == CombatOutcome.failed:
                    outcome = "Failed"

                wrt.writerow({"Player": attacking.name, "Action": "attacks", "Target": defending.name, "Result": outcome })

    def final_battle(self, player1, player2, lives = 3):
        player1.battle_lives = player2.battle_lives = lives
        p1a = player1.get_stat("Agility")
        p2a = player2.get_stat("Agility")
        if p1a > p2a:
            first, second = player1, player2
        elif p2a > p1a:
            first, second = player2, player1
        elif p1a == p2a:
            players = [player1, player2]
            random.shuffle(players)
            first, second = players
        round = 1
        while player1.battle_lives > 0 and player2.battle_lives > 0:
            if round % 2 == 1:
                attack_result = first.attack_check(second)
                if attack_result == CombatOutcome.success:
                    second.battle_lives -= 1
                elif attack_result == CombatOutcome.countered:
                    first.battle_lives -= 1
            else:
                attack_result = second.attack_check(first)
                if attack_result == CombatOutcome.success:
                    first.battle_lives -= 1
                elif attack_result == CombatOutcome.countered:
                    second.battle_lives -= 1
            print("Round {}, {} lives: {}, {} lives: {}".format(round, player1.name, player1.battle_lives, player2.name, player2.battle_lives))
            round += 1
        if player1.battle_lives > 0:
            print("{} Wins the Hunger Games!!!".format(player1.name))
            player2.set_dead();
        elif player2.battle_lives > 0:
            print("{} Wins the Hunger Games!!!".format(player2.name))
            player1.set_dead();

    def stat_based_selection(self, selection_players, selection_stats, positive = True, n = 1, unique = True):
        if n > len(selection_players) and unique:
            raise ValueError("Unable to select {} unique players from {}".format(n, len(selection_players)))
        distribution = []
        living_selected = [p for p in selection_players if p.is_alive]
        #This is the easiest but memory inefficient way of doing a weighted distribution
        #But the numbers will be small enough that it won't be a problem
        player_scores = {player:0 for player in living_selected}
        for player in player_scores:
            for stat in selection_stats:
                player_scores[player] += player.get_stat(stat)

        if positive:
            distribution = [player for player in living_selected for i in range(player_scores[player])]
        else:
            invert = max(player_scores[i] for i in player_scores) + min(player_scores[i] for i in player_scores)
            distribution = [player for player in living_selected for i in range(invert - player_scores[player])]

        # print(distribution)
        selected = set()
        ranked_players = []
        if unique:
            while len(selected) < n:
                chosen = random.choice(distribution)
                if chosen not in selected:
                    selected.add(chosen)
                    ranked_players.append(chosen)
                distribution.remove(chosen)
        else:
            ranked_players = random.sample(distribution, n)

        return ranked_players

    def save_players(self):
        self.print_players()
        write_player_file("Players.csv", [p.get_dict() for p in self.get_players()])
        pickle_obj('pik.dat', self.players)


    def load_players(self):
        self.players = unpickle_obj('pik.dat')

    def save_game(self):
        self.print_players()
        t = datetime.now()
        cwd = os.path.dirname(os.path.realpath(__file__))
        sdir = "backup"
        if self.game_name != "game":
            write_player_file("Players.csv", [p.get_dict() for p in self.get_players()])
            write_player_file(os.path.join(cwd,sdir,"players_{}-{}-{}-{}.csv".format(t.month, t.day, t.hour, t.minute)), [p.get_dict() for p in self.get_players()])
        pickle_obj(os.path.join(cwd,sdir,'{}.dat'.format(self.game_name)), self)
        pickle_obj(os.path.join(cwd,sdir,'{}_{}-{}-{}-{}.dat'.format(self.game_name, t.month, t.day, t.hour, t.minute)), self)



    def print_players(self):
        for p in self.get_players():
            print(p)

    def set_ids_and_districts(self, path):
        with open(path) as f:
            rdr = csv.DictReader(f)
            for i, line in enumerate(rdr):
                cur_player = self.get_player_by_name(line["Name"])
                cur_player.id = i
                cur_player.district = (i // 2) + 1



    def initial_setup(self):
        print("~~~Initial Setup~~~")
        self.create_players_from_responses("Responses.csv")
        self.set_ids_and_districts("saved_players.csv")
        self.kingpin = random.choice(self.get_players())
        # print(kingpin)
        self.kingpin.is_kingpin = True
        self.kingpin.is_career = True
        print("Kingpin is:", self.kingpin.name)

        self.save_game()


    def run_pregame(self):
        print("~~~Pregame~~~")
        # self.load_players()
        self.run_cornucopia(self.get_players_from_csv("Cornucopia.csv"))
        # self.save_players()

    def refresh_players(self):
        self.load_players()
        self.save_players()

    def run_game_phase(self, phase = None):
        if phase is None:
            phase = self.current_phase
        print("~~~Day {}~~~".format(phase))
        self.lynch_player_from_file()
        if phase == 9:
            print("~~~Feast ~~~")
            self.run_feast(self.get_players_from_csv("Feast.csv"))
        print("~~~Night {}~~~".format(phase))
        cur_living = self.get_living_players()
        if len(cur_living) == 2:
            print("THE FINAL SHOWDOWN!")
            self.final_battle(*cur_living)
        elif len(cur_living) == 1:
            print("{} Wins the Hunger Games!".format(cur_living[0].name))
        else:
            # self.load_players()
            self.current_phase = phase
            self.night_actions[self.current_phase] = []
            current_actions = self.night_actions[self.current_phase]
            with open("night{}.csv".format(self.current_phase)) as f:
                    rdr = csv.DictReader(f)
                    for i, line in enumerate(rdr):
                            current_actions.append(dict({"Line" : i}, **line))
            current_actions.sort(key = lambda x: x["Line"])
            current_actions.sort(key = lambda x: self.get_player_by_name(x["Player"]).get_stat("Agility"), reverse = True)
            current_actions.sort(key = lambda x: self.get_action_priority(x["Action"]))
            for a in current_actions:
                    a['Result'] = self.perform_action(a)

            for player in [p for p in self.get_players() if p.is_alive]:
                    if player.poison_death_check():
                            player.set_dead()
                            player.death_text = "Killed by poison on Night {}".format(CURRENT_PHASE)
                            print("{} has died of Posioning!".format(player.name))

            with open("night{}_results.csv".format(self.current_phase), 'w', newline='') as f:
                    wrt = csv.DictWriter(f, ["Line", "Player", "Action", "Target", "Result"])
                    wrt.writeheader()
                    wrt.writerows(current_actions)

            self.distribute_sponsor_items(self.current_phase)

    def lynch_player_from_file(self, day = None):
        if day is None:
            day = self.current_phase
        with open("lynches.csv") as f:
            rdr = csv.DictReader(f)
            lynched_name = [line["Name"] for line in rdr if line["Day"] == str(day)]
            if len(lynched_name) > 1:
                raise ValueError("Invalid number of Lynched players for Day {}: {}".format(day, len(lynched_name)))
            elif len(lynched_name) == 0:
                print("No Lynch Target for Day {}".format(day))
            else:
                self.lynch_player(lynched_name[0])

    def lynch_player(self, player_name):
        player = self.get_player_by_name(player_name)
        if player.is_alive:
            player.set_dead()
            self.player_item_drop(player)
            player.death_text = "Lynched Day {}".format(CURRENT_PHASE)
            print("{} Has been Lynched on Day {}".format(player_name, CURRENT_PHASE))
        else:
            print("{} cannot be lynched as they are already dead".format(player_name))

    def player_item_drop(self, player):
        self.dropped_items += player.inventory
        print("{} dropped {}".format(player.name, player.inventory))
        print("Total dropped items: {}".format(self.dropped_items))
        player.inventory = []

    def assign_dropped_item(self, player, item = None):
        if item not in self.dropped_items:
            raise ValueError("Item has not been dropped")

        if item is None:
            selected_item = random.choice(self.dropped_items)
        else:
            selected_item = item
        player.add_item(selected_item)
        self.dropped_items.remove(item)

    def perform_action(self, current_action):
        player, action = self.get_player_by_name(current_action["Player"]), current_action["Action"]
        if not player.can_perform_any_action():
            print("{} tried to {} but cannot as they are {}".format(player.name, action, "Dead" if not player.is_alive else "Trapped"))
            return "Failed: {}".format("Player Dead" if not player.is_alive else "Player Trapped")
        elif action in self.cooldown_actions and player.action_on_cooldown(action):
                print("{} tried to {} but cannot it is on Cooldown {}".format(player.name, action, player.actions))
                return "Failed: Cooldown"
        else:
            if action == "Hide":
                player.hide()
                return "Success"
            elif action == "Guard":
                player.guard()
                return "Success"
            elif action == "Attack" or action == "Kill":
                target = self.get_player_by_name(current_action["Target"])
                if not target.is_alive:
                    print("{} tried to attack {}, but failed as the target is already dead".format(player.name, target.name))
                else:
                    if action == "Attack":
                        attack_action_res = player.attack(target)
                    elif action == "Kill":
                        if player.is_career:
                            attack_action_res = player.attack(target, career_kill = True)
                        else:
                            print("{} tried to perform a Career Kill, but cannot as they are not a Career".format(player.name))
                            return "Failed: Not Career"

                    if attack_action_res == CombatOutcome.success:
                        player.raid(target)
                        self.player_item_drop(target)
                        return "Success"
                    elif attack_action_res == CombatOutcome.countered:
                        target.raid(player)
                        self.player_item_drop(player)
                        return "Countered"
                    elif attack_action_res == CombatOutcome.failed:
                        return "Failed"
                    elif attack_action_res == CombatOutcome.hidden:
                        return "Hidden"
                    elif attack_action_res == CombatOutcome.success_protected:
                        return "Protected from Attack"
                    elif attack_action_res == CombatOutcome.countered_protected:
                        return "Countered but Protected"
            else: #using an item
                if action.endswith("Serum"):
                    available_serums = player.get_usable_items(action)
                    if available_serums:
                        return player.drink_serum(available_serums[0])
                    else:
                        print ("{} tried to drink {}, but doesn't own one".format(player.name, action))
                        return "Failed"
                else:
                    target = self.get_player_by_name(current_action["Target"])

                    return player.perform_item_action(target, action)






        #TODO Finish





def load_game(filename = 'game', timestamp = None):
    cwd = os.path.dirname(os.path.realpath(__file__))
    sdir = "backup"
    if timestamp is None:
        return unpickle_obj(os.path.join(cwd,sdir,'{}.dat'.format(filename)))
    else:
        return unpickle_obj(os.path.join(cwd,sdir,'{}_{}-{}-{}-{}.dat'.format(filename, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)))


###NIGHT 0
# game = Game()

# game.initial_setup()
# game.set_careers("Ben Jelavic", "Caitlin Bell", "Evan Kohilas", "Rachel Alger", "Shane Arora", "Terry Watson")
# game.print_players()
# game.run_pregame()
# game.print_players()
# game.save_game()



###DAY 1
# CURRENT_PHASE = 1
# game = load_game()
# game.lynch_player_from_file(CURRENT_PHASE)
# game.print_players()
# game.save_game()

###NIGHT 1
# CURRENT_PHASE = 1
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()

###DAY 2
# CURRENT_PHASE = 2
# game = load_game()
# game.lynch_player_from_file(CURRENT_PHASE)
# game.print_players()
# game.save_game()

###NIGHT 2
# CURRENT_PHASE = 2
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()


##DAY 3
# CURRENT_PHASE = 3
# game = load_game()
# tony = game.get_player_by_name("Antonio Legovich") ###Bye bye Tony
# tony.name = "Maddie Mackey"
# game.lynch_player_from_file(CURRENT_PHASE)
# game.print_players()
# game.save_game()


###NIGHT 3
# CURRENT_PHASE = 3
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()

###DAY 4
# CURRENT_PHASE = 4
# game = load_game()
# game.lynch_player_from_file(CURRENT_PHASE)
# game.print_players()
# game.save_game()

###NIGHT 4
# CURRENT_PHASE = 4
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()

###DAY 5
# CURRENT_PHASE = 5
# game = load_game()
# game.lynch_player_from_file(CURRENT_PHASE)
# game.print_players()
# game.save_game()

###NIGHT 5
# CURRENT_PHASE = 5
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()


###DAY 6
# CURRENT_PHASE = 6
# game = load_game()
# game.lynch_player_from_file(CURRENT_PHASE)
# game.print_players()
# game.save_game()

###NIGHT 6
# CURRENT_PHASE = 6
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()

###DAY 7
# CURRENT_PHASE = 7
# game = load_game()
# game.lynch_player_from_file(CURRENT_PHASE)
# game.print_players()
# game.save_game()

###NIGHT 7
# CURRENT_PHASE = 7
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()

###DAY 8
# CURRENT_PHASE = 8
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()


###DAY 9 - Feast
# CURRENT_PHASE = 9
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()


###DAY 10
# CURRENT_PHASE = 10
# game = load_game()
# game.set_phase(CURRENT_PHASE)
# game.run_game_phase()
# game.print_players()
# game.save_game()


###DAY 11
#CURRENT_PHASE = 11
#game = load_game()
#game.set_phase(CURRENT_PHASE)
#game.run_game_phase()
#game.print_players()
#game.save_game()

###DAY 12
CURRENT_PHASE = 12
game = load_game()
game.set_phase(CURRENT_PHASE)
game.run_game_phase()
game.print_players()
game.save_game()