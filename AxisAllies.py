import random
from enum import Enum

class pieces(Enum):
    infantry = 1
    artillery = 2
    submarine = 3
    destroyer = 4
    fighter = 5
    bomber = 6 
    battleShip = 7
    battleShipHit1 = 8
    battleShipHit2 = 9
    combinedInfantry = 10
    tank = 11
    cruiser = 12
    aircraftCarrier = 13

class battleType(Enum):
    land = 1
    sea = 2
    amphibious = 3


random.seed(1)
landDefenseProfile = [pieces.infantry, pieces.combinedInfantry, pieces.artillery, pieces.tank, pieces.fighter]
seaDefenseProfile = [pieces.battleShipHit1, pieces.submarine, pieces.destroyer, pieces.cruiser, pieces.fighter, pieces.aircraftCarrier, pieces.battleShipHit2]
subHitsProfile = [pieces.battleShipHit1, pieces.submarine, pieces.destroyer, pieces.cruiser, pieces.aircraftCarrier, pieces.battleShipHit2]

def assignHitsByProfile(numHits, defender, hitProfile):
    #loop over defender pieces and assign the hits

    for piece in hitProfile:
        if (numHits == 0):
            break
        numPieces = defender[piece]
        if (piece != pieces.combinedInfantry):
            if (numPieces > 0):
                if (numPieces - numHits >= 0):
                    # All hits assigned
                    defender[piece] -= numHits              
                    if (piece == pieces.battleShipHit2):
                        #remove the battleships
                        defender[pieces.battleShip] -= numHits

                    numHits = 0
                else:
                    numHits -= numPieces
                    if (piece == pieces.battleShipHit2):
                        defender[piece] = 0
                        #remove the battleships
                        defender[pieces.battleShip] = 0
                    else:
                        defender[piece] = 0
        else:
            if (numPieces > 0):
                if (numPieces - numHits >= 0):
                    # All hits assigned
                    defender[piece] -= numHits 
                    # Peel out the artillery 
                    defender[pieces.artillery] = numHits

                    numHits = 0
                else:
                    defender[piece] = 0
                    defender[pieces.artillery] = (numPieces * 2) - numHits;
                    numHits -= numPieces


def assignHits(attackerHits, defender, battle):

    for piece in pieces:
        if (attackerHits[piece] > 0):
            #Submarines are special
            if (piece == pieces.submarine):
                assignHitsByProfile(attackerHits[piece], defender, subHitsProfile)
            else:
                # Subs cannot be hit by airpower if no destroyer is present
                if (battle == battleType.sea):
                    unAssignedhits = assignHitsByProfile(attackerHits[piece], defender, seaDefenseProfile)
                elif (battle == battleType.land):
                    unAssignedhits = assignHitsByProfile(attackerHits[piece], defender, landDefenseProfile)


def determineHits(numPieces, attackVal):
    hits = 0
    for x in range(numPieces):
        randVal = random.randint(1,6)
        print ("RandVal = {0}, attackVal = {1}".format(randVal, attackVal))
        if (randVal <= attackVal):
            hits = hits + 1
    return hits

def doBattle(attacker, defender, attackVals, defenseVals, battle):

    numDefenderHits = 0
    numAttackerHits = 0
    sneakAttackAttacker = False
    sneakAttackDefender = False

    attackerHits = dict.fromkeys(pieces, 0)
    defenderHits = dict.fromkeys(pieces, 0)
    #Submarines are special...still haven't dealt with submerging subs
    if (attacker[pieces.submarine] > 0 and defender[pieces.destroyer] == 0):
        #Attackers get sneak attack
        sneakAttackAttacker = True
        print ("Submarine Sneak Attack")
        attackerHits[pieces.submarine] = determineHits(attacker[pieces.submarine], attackVals[pieces.submarine])
        numAttackerHits += attackerHits[pieces.submarine]
        #Assign submarine hits from attackers, losses do not get counter attack
        if (attackerHits[pieces.submarine] > 0):
            assignHits(attackerHits, defender, battle)
            #All allowable sub hits assigned
            attackerHits[pieces.submarine] = 0;
    elif (attacker[pieces.destroyer] == 0 and defender[pieces.submarine] > 0):
        #Defenders get sneak attack
        sneakAttackDefender = True
        defenderHits[pieces.submarine] = determineHits(defender[pieces.submarine], defenseVals[pieces.submarine])
        numDefenderHits =+ defenderHits[pieces.submarine]
        #Assign submarine hits from defenders, losses do not get attack (except maybe subs that have already attacked)
        if (defenderHits[pieces.submarine] > 0):
            assignHits(defenderHits, attacker, battle)
            #All allowable sub hits assigned
            defenderHits[pieces.submarine] = 0;
    #Subs special attacks taken care of...one more special case...anti-aircraft rolls
    for piece in pieces:
        if (piece != pieces.battleShipHit1 and piece != pieces.battleShipHit2):
            if (attacker[piece] > 0):
                if not (piece == pieces.submarine and sneakAttackAttacker):
                    # Combined Infantry are really double pieces
                    numPieces = attacker[piece]
                    if (piece == pieces.combinedInfantry):
                        numPieces *= 2
                    attackerHits[piece] = determineHits(numPieces, attackVals[piece])
                    numAttackerHits += attackerHits[piece]
            if (defender[piece] > 0):
                if not (piece == pieces.submarine and sneakAttackDefender):
                    defenderHits[piece] = determineHits(defender[piece], defenseVals[piece])
                    numDefenderHits += defenderHits[piece]

    #Assign hits

    print ("Total Attacker hits {0}\n".format(numAttackerHits))
    print ("Total Defender hits {0}\n".format(numDefenderHits))

    assignHits(attackerHits, defender, battle)
    assignHits(defenderHits, attacker, battle)

def main():
    print ("Do Battle")
    random.seed(1)

    attacker = dict.fromkeys(pieces, 0)
    defender = dict.fromkeys(pieces, 0)

    attacker[pieces.destroyer] = 0
    attacker[pieces.submarine] = 6
    attacker[pieces.fighter] = 0
    attacker[pieces.infantry] = 0
    attacker[pieces.artillery] = 0
    # make pseudo piece for infantry/artillery combo
    attacker[pieces.combinedInfantry] = 0
    attacker[pieces.tank] = 0

    defender[pieces.destroyer] = 1
    defender[pieces.submarine] = 0
    defender[pieces.fighter] = 2
    defender[pieces.battleShip] = 1
    defender[pieces.infantry] = 0
    defender[pieces.artillery] = 0
    defender[pieces.cruiser] = 0
    defender[pieces.aircraftCarrier] = 2
    defender[pieces.tank] = 0
    # make pseudo pieces for battleship hit 1 and 2
    defender[pieces.battleShipHit1] = 1
    defender[pieces.battleShipHit2] = 1

    battleGround = battleType.sea

    attackVals = {pieces.infantry: 1, pieces.artillery: 2, pieces.combinedInfantry: 2, pieces.tank: 3, pieces.destroyer: 2, pieces.fighter: 3, pieces.submarine: 2, pieces.cruiser: 3, pieces.aircraftCarrier: 1, pieces.battleShip: 4}
    defenseVals = {pieces.infantry: 2, pieces.artillery: 2, pieces.tank: 3, pieces.destroyer: 2, pieces.fighter: 4, pieces.submarine: 1, pieces.cruiser: 3, pieces.aircraftCarrier: 2, pieces.battleShip: 4}

    origAttacker = {k: v for k, v in attacker.items()}
    origDefender = {k: v for k, v in defender.items()}
    monteCarloResults = list()
    winLossPercentage  = 0.0
    monteCarloRuns = 1000

    for x in range(monteCarloRuns):
        resultsOfRound = [{'attacker':origAttacker,'defender':origDefender}]
        results = list()
        results.append(resultsOfRound)

        # Do a full battle...either defenders or attackers are gone
        remainingAttackers = sum(origAttacker.values())
        remainingDefenders = sum(origDefender.values())

        # Reset attacker and defender
        attacker = origAttacker.copy()
        defender = origDefender.copy()

        print("Attacker: ")
        print(attacker)

        # Could get into endless loop depending on pieces, i.e. subs on aircraft
        round = 0
        while remainingAttackers > 0 and remainingDefenders > 0:
            print("Round: {0}".format(round))
            doBattle(attacker, defender, attackVals, defenseVals, battleGround)
            results.append( [{'attacker:':{k: v for k, v in attacker.items()}, 'defender':{k: v for k, v in defender.items()}} ])
            #Over counts Battleships
            remainingAttackers = sum(attacker.values())
            remainingDefenders = sum(defender.values())
            print("Total Remaining Attackers: {0}\n".format(remainingAttackers))
            print("Total Remaining Defenders: {0}\n".format(remainingDefenders))
            round += 1

        if (remainingAttackers > remainingDefenders):
            print('Attacker Wins')
            winLossPercentage += 1.0
        else:
            print('Defender Wins')
    print("Total Attacker Win %: {0}".format((winLossPercentage/monteCarloRuns)*100))

    #print ("Originals:")
    #print (origAttacker)

    #attackerHits = dict.fromkeys(pieces, 0)
    #attackerHits[pieces.fighter] = 2
    #attackerHits[pieces.submarine] = 4

#    assignHits(attackerHits, defender)

    print (attacker)
    print (defender)

    print (monteCarloResults)


    #results = sea_battle(attacker, defender, attackVals, defenseVals)

main()