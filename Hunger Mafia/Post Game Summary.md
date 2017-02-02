# Mafia Hunger Games Post Game Summary
_Liam Callaway_

## General overview
Firstly thanks everyone for your patience, both throughout the game and afterwards with my delays in putting together this summary. Hopefully it'll be at least somewhat worth it.

Secondly, let me thank you again for being guinea pigs in what was a fairly large experiment of mine. I wanted to try out something completely new, with very little idea how it would work out. Thanks to you all, I think it came together rather well. There were definitely things that didn't work so well, but also quite a few things that ending up being a lot of fun and brought some new dimensions to Mafia.

Considering how little I let on as to how the game would work, and how involved the mechanics got at times, I think all in all everyone played very well. As always, there were a few nice logical deductions made, and some amusing moments of deception. As the game progressed I started to see more people considering what they knew of the mechanics and using this to influence their decisions in game, which is always a good thing. Finally, while I think in some specific areas, the game was slightly unbalanced, overall things were fairly even. This was reflected in the ebb and flow of the town:mafia ratio.

Hopefully you all enjoyed it as much as I enjoyed planning and running the game. As always, I'm very open to feedback and ongoing discussion (either publicly in the group, or privately in a PM). I realise seeing as it's so long now since the game actually ended, finer details may have been forgotten. But if this summary jogs your memory of anything, feel free to let me know.

Obviously it'll be a little while before I attempt something like this again. I like to think that these sort of modifications don't necessarily make mafia *better*, just different. For a while at least, I'd like to run a few more straightforward mafia games. Maybe in the future though, some of these elements could be reused in another game. I'd also be more than happy for people to take elements (or source code) from this game, and use it in their own.

## Stats and Character Generation
So to start with, let's talk about stats. There were 4 primary stats, which each player was asked to rank in order of preference during sign-up. This would influence how stats were distributed.

The following process was used:
- The first 20 stat points were allocated completely randomly among the 4 stats, regardless of preference.
- The next 7 points were randomly distributed into 3 buckets. These buckets were then sorted into decreasing order.
- The largest bucket was then allocated 1 additional point. If the player correctly answered the signup question in regards to the new Rubik's cube solve, the two largest buckets were each allocated a further 1 additional point.
- The score from the largest bucket was then added to the player highest preference stat. The next largest to their second preference and the final bucket to their third (with the last preference receiving no bonus).

This meant that each player ended up with a stat total of either 28 or 30 points depending on if they answered the signup question correctly.
An "average" score for each stat was about 7-8. Anything above 10-11 was high and anything below 4-5 was low.

Agility was used to prioritise actions. An attacker's Agility was compared against their target's Agility to calculate the location threshold.

An attacker's Strength was compared against their target's Defence to calculate the combat threshold. The reverse occurred during any counter-attacks.

Luck was used to potentially apply a +1 bonus to any stat when calculating thresholds, and to determine who would retrieve sponsor items.

Agility and Luck were both used to determine success in the Cornucopia and Feast.

## Items
Items could be used for a range of effects and abilities. In regards to stats, there were two classes of items that could influence them. Passive items would provide permanent boosts, whereas serums would provide a temporary boost. A serum could be used on the same night as any other actions.

__Passive Items__
- Dagger: +1 Str
- Broadsword: +2 Str -1 Agl
- Light Armour: +1 Def
- Heavy Armour: +2 Def -1 Agl
- Running Shoes: +1 Agl
- Lucky Charm: +1 Lck
- Lucky Sword: +2 Str +1 Lck
- Lucky Armour: +2 Def +1 Lck

__Serums__
- Strength Serum: +2 Str
- Defence Serum: +2 Def
- Agility Serum: +2 Agl
- Luck Serum: +2 Lck


The remaining active items were all fairly standard active abilities.

__Active Items__
- Telescope
- Scout Drone
- Med Kit
- Medicine
- Trap Kit
- Trap
- Poison Dart
- Grenades



The Telescope could perform repeated "seers", giving alignment and stat distribution.

Scout Drones were single use "follows" that would show a player's night interactions.

Med Kit was a repeated "protection", but couldn't self target. Medicine was the single use version. Both would heal poison.

Traps and the Trap Kit would prevent a player from performing any actions.

Poison Dart would poison a player and they would day a few nights later.

Grenades (referred to as Sticky Bombs in source code as I changed these fairly late in planning), had to uses, with a chance to blow up a player. They would also trigger upon death if you were holding them with a higher success rate.

## Rolls
In regards to rolls and thresholds, a normal cumulative distribution was used. For each type of roll, a specific mean and standard deviation were used. The threshold was then calculated by comparing a certain value to the cumulative sum of the distribution up to that point, and subtracting it from 1. For example, this value might be the delta of two players' agility, or a player's luck. So if the value was equal to the mean, the roll threshold would be 0.5. If the value was higher than the mean, the threshold would start to decrease below 0.5 (more likely to succeed), and vice versa.

The mean and standard deviation for each time of role varied, and was determined based on experimentation and trial and error before the game. Some rolls were more or less likely to succeed, or could favour either the instigator or the target, which was achieved by shifting the distribution mean one direction or the other.


## Source Code
The game itself was run largely programmatically. I'll share the source code. However please go easy on me. It needs some serious tidying up in places. The project spiralled out of my control a little quickly, and I didn't have quite the amount of time to maintain it. So please don't look to it for examples of good practices :P I'm open to posted the code to GitHub and allowing others to make pull requests if we actually want to maintain it. At the moment a lot of the functionality for Hunger Games Mafia is tied up along with the generic mafia stuff, so something high on my todo is list is to try and make it more modular.

The rough structure of the source is a single "Game" object controlling the interactions of a number of "Player" objects. I used the builtin pickle module to save and restore the state of this game object (and thus the collection of players) between each execution of the script.

The various data IO with the script was controlled mostly through the use of CSV files. I would record nightly actions into a new csv file each night, which would be processed, and the results written to another csv file. I also started logging various actions and calculations in a text file (simply by piping the print output), but I only started this from N2 because I didn't realise that would be a #goodidea earlier.

I'm sure there's better ways to achieve these functions rather than pickle and csv, but they were quick and easy and I knew how to use them so ¯\\_(ツ)_/¯

To add some determinism to the script, I used a different random seed for each night. These were precomputed before the game, which is what that stuff in related to asking for prime numbers and providing a hash was all about. Details about how this was done is available in the source comments. My intent was that post game, others would be able to run the script with the recorded actions and see the same results. However, due to the use of unsorted collections (dictionaries), various factors seem to affect some of the randomised results (eg when a Player is randomly selected), so you might not be able to replicate things exactly.

The source code is on GitHub, (as are the rest of the game files). If I ever get time I might work on some tweaks and improvements to the "engine", as I'd really like to make it more reusable. I'm open happy to take PRs if anyone else feels like doing some work on it. The repo can be found here:  https://github.com/liamcal/ncss-mafia/tree/master/Hunger%20Mafia

(Also, I made the file structure a bit more sane by putting things in various folders. However the source code currently requires a lot of the input files to be in the same directory if you want to run it)

## Phase by Phase Summary
I'm going to give a quick overview of the actual actions and then make some brief comments in some cases

### CORNUCOPIA
- The following players received items:
  - Shane: Trap Kit
  - Bryan: Dagger
  - Alex: L. Armour
  - Aretha: Running Shoes
  - Mitchell: B. Sword
  - Lauren H: Medpack
  - Michael: Lucky Charm
  - Joel: Telescope
  - David: H. Armour
  - Shea: Poison Dart
- Evan attacks Quinn, and kills him.
- Andrew attacks Liam, but they both defend and survive.

### DAY 1:
- Ben Jelavic: 6 (Lauren Heading, Liam Cahill, Lauren McNamara, Alex Rowell, Rachel Alger, Michael Cui)
- Rachel Alger: 2 (Robbie Collins, Bryan Mitchell)
- Michael Cui: 1 (Joel Aquilina)
- Joel Aquilina: 1 (David Vo)


### NIGHT 1:
- Joel investigates Deanna and learns she is a Tribute.
- Evan performs the Tribute kill on Liam Cahill.
- Liam would have attacked Deanna, but he was killed beforehand.
- The following players receive sponsors:
  - Joel: Strength Serum
  - Hayley: Dagger
  - Robbie: Medicine

Night 1 was fairly uneventful. Nearly everyone either hid or guarded, playing it safe to begin with.
As previously mentioned, unfortunately logs aren't available from N1.

### Day 2:
- Jacob Frilay: 8 (David Vo, Rachel Alger, Lauren McNamara, Lauren Heading, Andrew Titmuss, Robbie Collins, Maddie Wagner, Alex Rowell)
- Shane Arora: 2 (Mitchell Busby, Jacob Frilay)
- Lauren Heading: 1 (Deanna Arora)


### NIGHT 2
- Joel investigates Rachel and learns she is a Career.
- Evan attempts to attack Mitchell, but cannot locate him.
- Deanna attacks Lauren M, but was counter killed.
- Terry attempts the career kill on Aretha but couldn't locate her.
- The following players receive sponsors:
	- Joel: Luck Serum
	- David: Scout Drone
	- Lauren H: Trap

Another fairly straightforward night considering the number of players alive. Many players once again either hid or guarded. Joel got lucky and found a Career. Evan wasn't far off finding Mitchell, but Mitchell had guarded so it was unlikely he would have died. Terry had an extremely low chance of finding Aretha, as she had hidden and had an Agility boosting item, so the Mafia had their first night (of many) without kills. Joel received a third item, which meant even considering his high luck, RNGeezus was favouring him...

### DAY 3
- Rachel Alger: 8 (Lauren Heading, Bryan Mitchell, Alex Rowell, Ben Myers, Aretha Peethamparam, Evan Kohilas, Shea Bunge, Hayley van Waas)
- Aretha Peethamparam: 4 (Rachel Alger, Michael Cui, Riley Hoolahan, Maddie Wagner)
- Joel Aquilina: 1 (Lauren McNamara)


### NIGHT 3
- Shane uses a trap on Joel.
- Lauren protects Joel.
- Joel attempts to use Strength Serum and hide, but cannot as he is trapped.
- Alex attacks Shane, and kills him, raiding the Trap Kit.
- Evan attempts the career kill on Joel, but he is protected.
- Hayley attempts to attack Lauren H, but cannot locate her.
- Robbie attempts to attack Terry, but cannot locate him.
- The following players receive sponsors;
	- Hayley: Agility Serum
	- Andrew: Scout Drone
	- Maddie: Poison Dart

Things started to get more interesting tonight. After coming forward with information, a lot of events centred around Joel. The mafia trapped him, but it didn't make much difference as he had chosen not to use the Telescope that night anyway. Alex had a shot attacking Shane, and despite his very low strength, he rolled quite highly which was enough to kill him, before raiding the Trap Kit.

This was quite the blow to the Mafia, after losing Rachel earlier that day. Now they had also lost their Trap Kit and would be unable to block other priority actions. Evan succeeded in killing Joel, but because he was protected by Lauren, he survived.

Hayley couldn't locate Lauren, partly due to her naturally high Agility. Robbie had a fair chance at finding Terry, but luckily Terry had hidden that night, and so couldn't be found.

### DAY 4
- Robbie Collins: 7 (Lauren Heading, Ben Myers, Lauren McNamara, Joel Aquilina, Riley Hoolahan, Evan Kohilas, Mitchell Busby)
- Riley Hoolahan: 2 (Robbie Collins, Alex Rowell)
- Ben Myers: 1 (Michael Cui)
- Lauren Heading: 1 (Hayley van Waas)

### NIGHT 4
- Lauren protects Joel
- Joel investigates Riley and discovered she was a Tribute.
- Shea poisons Evan.
- Evan attempts the career kill on Lauren H, but cannot locate her.
- Ben attacks Riley, but she defends.
- Lauren M attacks Ben, but is killed in the counter attack.
- Riley attacks Aretha, and successfully kills her, raiding her Running Shoes.
- Terry attempts to attack Ben, but cannot find him.
- David uses a Scout Drone to follow Lauren H, and learns she protected Joel.
- The following players receive sponsors:
  - Michael: Defence Serum
  - Caitlin: Sticky Bombs
  - Shea: Light Armour

This night was much closer to the sort of gameplay I'd been hoping for. In other words, lots of death :D Shea had been suspicious of Evan (rightfully so), and used his slow-acting poison.

Both Evan and Terry from the careers attempted a kill, but both were unable to find their targets. This is something that would start to come up a lot this game. While the careers had a significant advantage in regards to their combat Strength, they had no buffs when it comes to the Agility needed to find their targets. Of course, the Agility roll was biased towards the searcher, but regardless, if the careers were to succeed in killing high Agility targets, they would need to either get lucky, or pick a killer who also had high agility.
Asides from the careers, there was many town instigated kills tonight. Lauren was killed in a counter attack, and Aretha was killed by Riley. This mitigated some of the damage sustained by the Careers tonight.

Also it's interesting to note that Shea had quite high Agility bit abysmal Luck. So he was successful in receiving his Poison from the Cornucopia, but it was very very unlikely he would receive any sponsor items. Yet, somehow he did, which goes to show that random truly is (pseudo) random xD

### DAY 5
- Ben Myers: 10 (Alex Rowell, Evan Kohilas, Maxwell Hajncl, Michael Cui, Lauren Heading, David Vo, Maddie Wagner, Hayley van Waas, Riley Hoolahan, Bryan Mitchell)
- Hayley van Waas: 1 (Ben Myers)

### NIGHT 5
- Alex traps Caitlin.
- Lauren H protects Evan, and heals him of poison.
- Caitlin attempts to grenade Riley, but can't because of the Trap.
- Evan successfully performs the career kill on Joel, and raids a Luck Serum.
- Andrew uses a Scout Drone on Lauren and observes them protecting Evan.
- The following players receive sponsors:
	- Alex: Medicine
	- Mitchell: Running Shoes
	- Michael: Trap

While there were less total actions than the previous night, a lot of important stuff still happened here. Alex successfully managed to prevent a potential extra mafia kill. However, the mafia were successful in killing Joel and removing the Telescope from the game for the moment. Even though Joel had hid that night, Evan had fairly high Agility, and was able to locate him without too much trouble.

Additionally, Lauren healed Evan of his poison, saving him from his impending doom. Of course, she didn't know that he was Mafia, but it's always worth considering if it's worth healing someone who is poisoned. Often even if there's a fair chance that their innocent, perhaps their death could shed some light on things, or else perhaps the protection would be better used on someone else.

### DAY 6
- Shea Bunge: 2 (Andrew Titmuss, Evan Kohilas)
- Maddie Wagner: 2 (Michael Cui, Alex Rowell)
- Evan Kohilas: 1 (Shea Bunge)

__Revote__
- Shea Bunge​: 6 (Andrew Titmuss, Caitlin Bell, Evan Kohilas, Lauren Heading, Maddie Wagner, Maxwell Hajncl)
- Maddie Wagner​: 5 (Alex Rowell, Michael Cui, Mitchell Busby, Riley Hoolahan, Shea Bunge)

### NIGHT 6
- Alex uses medicine to protect Lauren H.
- Maddie poisons Alex.
- Caitlin attempts to bomb Lauren H, but misses.
- Terry attempts the career kill on Riley, but cannot find her.
- The following players receive sponsors:
	- Bryan: Strength Serum
	- Alex: Lucky Charm
	- Riley: Broad Sword

A quiet night indeed, there were only two kill attempts (both from the Mafia), both of which failed. Riley was a good target for the career kill, as she had low base agility, but a combination of her previously raided Running Shoes and a Luck boost meant she was able to stay hidden. Caitlin's bomb attack had a fairly low threshold, but unfortunately for her, she rolled extremely low.

### DAY 7
- Maddie Wagner: 6 (Lauren Heading, Bryan Mitchell, Alex Rowell, Caitlin Bell, Evan Kohilas, Michael Cui)
- Caitlin Bell: 4 (David Vo, Maddie Mackey, Hayley van Waas, Maddie Wagner)

### NIGHT 7
- Alex traps Michael.
- Lauren protects Alex, healing him of the poison.
- Bryan drinks a Strength Serum.
- Caitlin bombs Riley, killing her in the explosion and destroying her items.
- Bryan attacks Mitchell, but they both survive each other's attacks.
- Evan attempts the career kill on Lauren, but cannot find her.
- David attacks Caitlin, but they both survive each others attacks.
- The following players receive sponsors:
	- Bryan: Heavy Armour
	- Alex: Grenades
	- Mitchell: Agility Serum

There were a few more attack actions attempted tonight. Bryan had very low Strength, but after the Strength serum, he and Mitchell were on a similar playing field with most of their stats, resulting in a tie. On the other hand, David's strength was a lot lower than Caitlin's defence, but his Defence was more than high enough to block the counter-attack.

For the first time in the game, a grenade detonated successfully, killing Riley without revealing her identity. It also destroyed any items she had been holding without giving Caitlin a chance to raid.

### DAY 8
- Maxwell Hajncl: 4 (Bryan Mitchell, Mitchell Busby, Michael Cui, Evan Kohilas)
- Michael Cui: 1 (Alex Rowell)

### NIGHT 8
- Alex bombs Bryan, killing him in the explosion and destroying his items.
- Evan attempts the career kill on Lauren H, but cannot find her.
- Terry attacks David, but cannot find him.
- The following players receive sponsors:
	- Alex: Defence Serum
	- Terry: Poison Dart
	- Caitlin: Trap

Another grenade explosion left Bryan dead without his identity revealed. Otherwise, this night really highlighted a struggle the Mafia were having this game. While the career kill granted a significant strength bonus, there was no modifier applied to their agility. Even though the agility roll was already biased towards the searcher, the Mafia would have a tough time performing any kills if they couldn't locate their targets. The idea isn't for the career kill to be foolproof, the game was designed for it to occasionally fail. But given the amount of failed mafia kills in this game, perhaps I should have applied a minor agility boost to is as well.

### DAY 9
- Evan Kohilas: 3 (Hayley van Waas, David Vo, Michael Cui)
- Michael Cui: 3 (Evan Kohilas, Maddie Mackey, Mitchell Busby)
- Caitlin Bell: 1 (Lauren Heading)

__Revote__
- Michael Cui: 7 (Alex Rowell, Andrew Titmuss, Caitlin Bell, Evan Kohilas, Maddie Mackey, Mitchell Busby)
- Evan Kohilas: 2 (Michael Cui, David Vo)

### FEAST
- The following players receive items:
	- Andrew: Lucky Sword
	- Lauren H: Lucky Armour
	- Andrew: Trap
	- David: Defence Serum
	- Hayley: Lucky Charm
	- Evan: Light Armour
	- Alex: Strength Serum
	- Lauren H: Telescope
	- Maddie: Medicine
- Evan attacks Andrew and kills him, raiding a Trap.
- Alex attacks David, but they both defend and escape unharmed.

### NIGHT 9
- Alex drinks Defence Serum.
- Terry attempts to poisons Andrew, but failed as he was killed at the feast.
- Mitchell attacks Evan, but is killed in a counterattack. Evan raids a broadsword from Mitchell.
- Evan attempts the career kill on Lauren H, successfully killing her and raiding the Telescope.
- Hayley attacks Evan, but is killed in a counterattack. Evan raids a Lucky Charm from Hayley.
- Caitlin attempts to attack Hayley, but fails as she was already dead.

Oh boy. This was the night that really changed things up. We went from the Mafia being fairly far behind and having a run of bad luck with their kills, to being very close to snatching victory. There was a some amount of luck on their behalf, but also a lot of the results come down to choices made by other players.

First up we had the Feast. I think about 3/4 of the players opted to go in. The feast was ran more or less the same as the Cornucopia did earlier. There were 2 new items, the Lucky Sword and Armour, along with every other item that had been dropped by a dead player so far. The Lucky Items were the most powerful passive items granted in the game, giving a +2 boost to either Strength or Defence as well as a +1 Luck boost. However, Andrew lost the sword straight away in his fight with Evan, and as the raided item is random, Evan ended up raiding a trap inside, removing the Lucky Sword from play.

Mitchell had fairly low base Strength, however holding a broadsword he stood a fair chance against Evan, who also had quite a low defence. Unfortunately the roll worked heavily against him, resulting in a counterkill from Evan's fairly high strength.
Hayley also took a risk attacking Evan, as her strength was also quite low. It was pretty unlikely she would have killed him, but even so, she also was unlucky that the roll was low enough to be killed in a counter attack.

Similarly, to Andrew, Lauren H also lost the Lucky Armour later that night. Her Defence was extremely low to begin with, and even with the +2 bonus, it wasn't nearly enough to block the Career kill. Again, the item was lost as Evan raided the Telescope instead. The mafia, in particular Evan, had been trying to kill Lauren for a very long time, so they were pretty happy when this kill finally succeeded.

It's worth noting that because a lot of the attacks tonight were focused on Evan, it also meant that individually he started to snowball somewhat in Strength. Each win resulted in a raid, and these often left him better prepared for the next fight. Similar things can happen like this in even normal Mafia games, when a particular player has been drawing a lot of attention to themselves. Often in these situations, that player will draw a large number of roll actions, which can often cause unexpected or undesired results in the aggregate. Whenever you target somebody with a role, it's always worth considering how likely they are to be targeted by other roles, and if that will affect you. Sometimes having your role work successfully is more important than having it work on a particular person.

### DAY 10
- Evan Kohilas: 3 (Maddie Mackey, Alex Rowell, David Vo)
- Maddie Mackey: 3 (Evan Kohilas, Terry Watson, Caitlin Bell)

__Revote__
- Evan Kohilas: 3 (Maddie Mackey, Alex Rowell, David Vo)
- Maddie Mackey: 3 (Evan Kohilas, Terry Watson, Caitlin Bell)

_(Going to start giving some comments on the days outcomes now as well as vote tallies)_

By now we were tied 3-3 mafia to town. Usually at this point the game would be over and the Mafia win, but that's not how the Hunger Games works. I never explicitly told either side, but my final twist was that this game was going to be more or less a last-man standing. Hopefully this would become apparent to everyone as the game approached it's end. So, play had to continue. Also, owing to the Grenade related deaths, the exact number wasn't known to the town, so it was important to maintain the possibility of their being a different ratio living players.

Predictably, the vote for Day 10 ended in a 3-3 tie between Evan and Maddie. Obviously, the 3 careers voted for Maddie, and the rest of the town were onto Evan. You all know how much I hate tie votes, there really is no nice way to deal with it. Killing neither or killing both often affects balance, and RNG just seems unfair. If it is still tied after a revote though, I will *usually* err on the side of no kill, however this isn't a hard and fast rule (as then it could be abused to force no-lynch).

### NIGHT 10
- Alex drinks Strength Serum.
- Evan drinks Luck Serum.
- Alex attempts to use a grenade on Caitlin, but it misses.
- Evan attempts to attack David, but cannot find him.
- Maddie attempts to attack Evan, but cannot find him.
- Caitlin attempts to attack Maddie, but cannot find her.
- Terry performs the career kill on Alex, killing him and raiding a Lucky Charm.

This was the last night that the Mafia needed to establish a proper majority in their numbers. There were a lot of last ditch attempts by the town to take out a mafia member. Alex was pretty unlucky with his Grenade, his luck stat meant it was pretty likely to be successful, but the roll worked against him. Maddie might have stood a chance in a fight with Evan, but Agility was not quite in her favour, and Evan couldn't be found. On the other hand, I was not expecting Terry to be able to locate Alex, as Alex's Agility was much higher. It seemed that Agility was finally working in the Mafia's favour tonight, as Terry managed to get a very high role and successfully perform the career kill.

### DAY 11
- David Vo: 3 (Evan Kohilas, Terry Watson, Caitlin Bell

So by now the mafia had the 3-2 advantage and they knew it. Of course, there's a reason why games usually end when there's a mafia majority, because they can just take control of the lynch like they did here. In an earlier draft of my game plan, I had that if the mafia achieved a majority, all non-mafia players would be eliminated instantly and the remaining mafia would have to battle it out til the end.
However I thought it would be best to let the game continue for two reasons, the first being that the nightly mafia kill was not guaranteed, and it could be possible (though difficult and unlikely) for the town to win back the balance of power. Secondly, I kind of hoped we might get some cross factional alliances forming during the day phase. If enough players came to the conclusion that the game was last-man-standing, it would also be reasonable to assume that going up against players stronger than you might be a bad idea.
Regardless, the mafia instantly piled their votes onto David, who didn't even put up a struggle. Nothing unexpected happened and the mafia went into the night phase up 3-1.

### NIGHT 11
- Caitlin Traps Maddie
- Terry Poisons Maddie
- Evan kills Terry and raids a Lucky Charm.
- Maddie tried very hard to eat the berries. (But otherwise performed no actions)

_(Also, somehow the full logs are missing from tonight as well, not sure how that happened...)_

While Caitlin and Terry did what they could to incapacitate Maddie, the career's decided that they would not kill her tonight (and risk a counterattack), but instead leave her alive to be lynched tomorrow. However, surprising his teammates, Evan decided to perform the Career kill on Terry instead. I assume by now he had realised that something was afoot, and that Terry was risky to keep around. The kill was successful, and by the last day we were down to just Evan, Caitlin and Maddie.

### DAY 12
- Maddie Mackey: 2 (Caitlin Bell, Evan Kohilas)

Once again, I really hoped someone would try and make an alliance. For example, it would have been a great play for Caitlin and Maddie to vote out Evan, particularly if she had known that Evan was the one that killed Terry (and not Maddie). With the amount of items Evan was holding by now, he would be tough to beat. But the Mafia stuck together until the end and Maddie was lynched, bringing us into the final night.

### NIGHT 12 - The Final Showdown
So tonight, I did not ask for action submissions for either player. Instead, the two remaining Tributes would fight to the death, in a slightly modified combat system. Both players were given 3 lives, and would then take it in turns fighting, alternating between being on the offensive or defensive side (highest Agility is offensive first, no location rolls). Even with all Evan's items, Evan and Caitlin were actually fairly closely matched. Evan had high Strength but low Defence, Caitlin had high Defence but low Strength. Evan did have the higher Agility though, so got to go first.

The showdown went as follows (more details in the logs):
- R1: Evan attacks Caitlin
	- E3 - C2
- R2: Caitlin attacks Evan
	- E2 - C2
- R3: Caitlin counter-attacks Evan
	- E1 - C2
- R4: Caitlin attacks Evan
	- E0 - C2

In the end, it was the counter-attack that spelled the end for Evan. Even though the stats were somewhat in his favour, all of Caitlin's roll's were moderately high, whereas Evan had one low roll.
You could argue that leaving the winner up to chance is poor game design, and I'll agree that there definitely are issues with it. But a large portion of this game h as been about manipulating the odds to work in your favour. If I had of given each player 5 or 10 lives, it's much more likely that Evan would have won. With a smaller number, while he still had the upper-hand, there was the possibility of having luck affect the outcome, and in this case it did.
