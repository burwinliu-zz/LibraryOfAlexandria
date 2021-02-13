# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #7: The Maze Decorator
from random import random

try:
    from malmo import MalmoPython
except ImportError:
    import MalmoPython

import os
import sys
import time
import json
import matplotlib.pyplot as plt
from numpy.random import randint

agent_position = 0
num_moves = 0

diamond_distribution = 0.2;


def GetMissionXML(obs_size):
    leftX = obs_size * 2 + 2
    front = f"<DrawCuboid x1='{leftX}' y1='0' z1='2' x2='-4' y2='10' z2='2' type='bookshelf' />"
    right = f"<DrawCuboid x1='-4' y1='0' z1='2' x2='-4' y2='10' z2='-10' type='bookshelf' />"
    left = f"<DrawCuboid x1='{leftX}' y1='0' z1='2' x2='{leftX}' y2='10' z2='-10' type='bookshelf' />"
    back = f"<DrawCuboid x1='{leftX}' y1='0' z1='-10' x2='-4' y2='10' z2='-10' type='bookshelf' />"
    floor = f"<DrawCuboid x1='{leftX}' y1='1' z1='-10' x2='-4' y2='1' z2='2' type='bookshelf' />"
    libraryEnv = front + right + left + back + floor

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
                    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                        <About>
                            <Summary>Librarian</Summary>
                        </About>

                        <ServerSection>
                            <ServerInitialConditions>
                                <Time>
                                    <StartTime>12000</StartTime>
                                    <AllowPassageOfTime>false</AllowPassageOfTime>
                                </Time>
                                <Weather>clear</Weather>
                            </ServerInitialConditions>
                            <ServerHandlers>
                                <FlatWorldGenerator generatorString="3;7,2;1;"/>
                                <DrawingDecorator>
                                    {libraryEnv}
                                    <DrawBlock x='-2' y='1' z='0' type='iron_block' />
                                    <DrawBlock x='0' y='1' z='0' type='emerald_block' />
                                </DrawingDecorator>
                                <ServerQuitWhenAnyAgentFinishes/>
                                    
                            </ServerHandlers>
                        </ServerSection>

                        <AgentSection mode="Survival">
                            <Name>Librarian</Name>
                            <AgentStart>
                                <Placement x="0.5" y="2" z="0.5" pitch="40" yaw="0"/>
                            </AgentStart>
                            <AgentHandlers>
                                <ContinuousMovementCommands/>
                                <DiscreteMovementCommands/>
                                <ChatCommands/>
                                <ObservationFromFullStats/>
                                <InventoryCommands/>
                                <ObservationFromFullInventory/>
                                <ObservationFromRay/>
                                <ObservationFromGrid>
                                    <Grid name="floorAll">
                                        <min x="-{int(obs_size / 2)}" y="-1" z="-{int(obs_size / 2)}"/>
                                        <max x="{int(obs_size / 2)}" y="0" z="{int(obs_size / 2)}"/>
                                    </Grid>
                                </ObservationFromGrid>
                                <AgentQuitFromTouchingBlockType>
                                    <Block type="iron_block"/>
                                </AgentQuitFromReachingPosition>
                                
                            </AgentHandlers>
                        </AgentSection>
                    </Mission>'''


def getObs(arg_agent):
    toSleep = .1
    obs = {}
    while obs == {}:
        time.sleep(toSleep)
        toSleep += .2
        try:
            cur_state = arg_agent.getWorldState()
            obs = json.loads(cur_state.observations[-1].text)
        except IndexError:
            print("retrying...")
    return obs


def end(arg_agent_host, arg_world_state):
    print("Ending Mission", end=' ')
    while arg_world_state.is_mission_running:
        print(".", end="")
        moveToChest(arg_agent_host, -1)
        time.sleep(0.1)
        arg_world_state = arg_agent_host.getWorldState()
        for end_error in world_state.errors:
            print("Error:", end_error.text)
    print()


def moveLeft(arg_agent_host, steps):
    global num_moves

    num_moves += steps
    for i in range(steps):
        arg_agent_host.sendCommand("moveeast")
        time.sleep(0.1)


def moveRight(arg_agent_host, steps):
    global num_moves

    num_moves += steps
    for i in range(steps):
        arg_agent_host.sendCommand("movewest")
        time.sleep(0.1)


def moveToChest(arg_agent_host, chest_num):
    global agent_position

    if agent_position == chest_num:
        return
    if chest_num != -1:
        print(f"Moving to chest #{chest_num} ..")
    if agent_position - chest_num < 0:
        moveLeft(arg_agent_host, 2 * abs(agent_position - chest_num))
    else:
        moveRight(arg_agent_host, 2 * abs(agent_position - chest_num))
    agent_position = chest_num


def openChest(arg_agent):
    global num_moves
    num_moves += 10
    arg_agent.sendCommand("use 1")
    time.sleep(0.1)
    arg_agent.sendCommand("use 0")


def closeChest(arg_agent):
    for _ in range(10):
        arg_agent.sendCommand("movenorth")
    time.sleep(0.1)
    for _ in range(10):
        arg_agent.sendCommand("movesouth")


def getItemsInChest(arg_agent):
    items = {}
    obs = getObs(arg_agent)
    chestName = obs["inventoriesAvailable"][-1]['name']
    chestSize = obs["inventoriesAvailable"][-1]['size']
    for i in range(chestSize):
        if f"container.{chestName}Slot_{i}_item" in obs:
            item = obs[f"container.{chestName}Slot_{i}_item"]
            if item == 'air':
                continue
            if item not in items:
                items[item] = 0
            items[item] += obs[f"container.{chestName}Slot_{i}_size"]

    return items


def printItemsInDict(items):
    print("Items in this chest:")
    print("________________________")
    for key, value in items.items():
        print(f"{key} :: {value}")
    print("________________________\n\n")


def invAction(arg_agent, action, inv_index, chest_index, obs=None):
    if obs is None:
        obs = getObs(arg_agent)
    chestName = obs["inventoriesAvailable"][-1]['name']
    agent_host.sendCommand(f"{action}InventoryItems {inv_index} {chestName}:{chest_index}")


def getItems(arg_agent, searching, inventoryNeeds, ordersMet):
    obs = getObs(arg_agent)
    chestName = obs["inventoriesAvailable"][-1]['name']
    chestSize = obs["inventoriesAvailable"][-1]['size']
    for i in range(chestSize):

        obs = getObs(arg_agent)
        if f"container.{chestName}Slot_{i}_item" in obs:
            item = obs[f"container.{chestName}Slot_{i}_item"]
            itemHad = obs[f"container.{chestName}Slot_{i}_size"]

            if item == 'air':
                continue
            if item in searching and len(searching[item]) != 0:
                inventoryNeeds[searching[item][-1]][1] -= itemHad
                time.sleep(.2)
                print(int(obs[f"InventorySlot_{searching[item][-1]}_size"]))
                invAction(arg_agent,
                          "combine" if int(obs[f"InventorySlot_{searching[item][-1]}_size"]) != 0 else "swap",
                          searching[item][-1], i, obs=obs)
                if inventoryNeeds[searching[item][-1]][1] == 0:
                    ordersMet += 1
                    if len(searching[item]) == 1:
                        del searching[item][-1]
                        break
                    else:
                        searching[item].pop()
    return searching, inventoryNeeds, ordersMet


def bruteForceRetrieve(arg_agent, values: dict, size):
    # Reformatting the values into easily distributable sections (stacks of 64 presumed)
    inventoryNeeds = []
    toFill = {}
    for i in values.keys():
        if i not in toFill:
            toFill[i] = []
        while values[i] > 64:
            inventoryNeeds.append([i, 64])
            values[i] -= 64
            toFill[i].append(len(inventoryNeeds) - 1)
        inventoryNeeds.append([i, values[i]])
        toFill[i].append(len(inventoryNeeds) - 1)
    ordersMet = 0
    for i in range(1, size):
        moveToChest(arg_agent, i)
        time.sleep(.5)
        openChest(arg_agent)
        time.sleep(.5)
        toFill, inventoryNeeds, ordersMet = getItems(arg_agent, toFill, inventoryNeeds, ordersMet)
        # Retrieve all items into the spaces, as needed
        time.sleep(.5)
        closeChest(arg_agent)
        time.sleep(.5)
        if len(inventoryNeeds) == ordersMet:
            break
    moveToChest(arg_agent, 0)
    time.sleep(.5)
    obs = getObs(arg_agent)
    openChest(arg_agent)
    time.sleep(.2)
    for i in range(27):
        invAction(arg_agent, "swap", i, i, obs=obs)
        time.sleep(.2)
    closeChest(arg_agent)
    time.sleep(.2)


# Testing and enviornment
def setupEnv(env_agent, env_size, env_items):
    print("Setting up chests..", end=' ')
    # 7 max slots per
    for chest_num in range(env_size):
        num = 0
        itemString = ""
        for i in range(7):
            val = random()
            itemID = 'air'
            for j in env_items:
                if val < j[1]:
                    itemID = j[0]
                    break
            itemString += f"{{Slot:{i},id:{itemID},Count:1b}},"
        env_agent.sendCommand(f"chat /setblock {chest_num * 2 + 2} 1 0 minecraft:diamond_block 2 replace")
        env_agent.sendCommand(f"chat /setblock {chest_num * 2 + 2} 2 1 "
                              f"minecraft:chest 2 replace {{Items:[{itemString[:-1]}]}}")
    env_agent.sendCommand(f"chat /setblock 0 2 1 minecraft:chest 0 replace")
    print("done")


def testRun2(agent_host):
    size = 6
    items = {'stone': .5, 'diamond': .5}

    setupEnv(agent_host, size, items)
    time.sleep(1)
    moveToChest(agent_host, 6)
    time.sleep(0.5)
    openChest(agent_host)
    time.sleep(0.5)
    printItemsInDict(getItemsInChest(agent_host))
    time.sleep(0.5)
    invAction(agent_host, "swap", 0, 0)
    time.sleep(0.25)
    invAction(agent_host, "swap", 1, 1)
    time.sleep(0.25)
    closeChest(agent_host)
    time.sleep(0.5)
    for i in reversed(range(1, 6)):
        moveToChest(agent_host, i)
        time.sleep(0.5)
        openChest(agent_host)
        time.sleep(0.5)
        printItemsInDict(getItemsInChest(agent_host))
        time.sleep(0.5)
        invAction(agent_host, "combine", 0, 0)
        time.sleep(0.25)
        invAction(agent_host, "combine", 1, 1)
        time.sleep(0.25)
        closeChest(agent_host)
        time.sleep(0.5)
    moveToChest(agent_host, 7)
    time.sleep(0.5)
    openChest(agent_host)
    time.sleep(0.5)
    printItemsInDict(getItemsInChest(agent_host))
    time.sleep(0.5)
    invAction(agent_host, "swap", 0, 0)
    time.sleep(0.25)
    invAction(agent_host, "swap", 1, 1)
    time.sleep(0.25)
    printItemsInDict(getItemsInChest(agent_host))
    time.sleep(0.5)
    closeChest(agent_host)
    time.sleep(0.5)


def testRun(agent_host):
    size = 6
    items = {'stone': .5, 'diamond': .5}

    setupEnv(agent_host, size, items)
    time.sleep(1)
    moveToChest(agent_host, 3)
    time.sleep(1)
    openChest(agent_host)
    time.sleep(1)
    closeChest(agent_host)
    time.sleep(1)
    moveToChest(agent_host, 6)
    time.sleep(1)
    openChest(agent_host)
    time.sleep(1)
    closeChest(agent_host)
    time.sleep(1)
    moveToChest(agent_host, 1)
    time.sleep(1)
    openChest(agent_host)

    time.sleep(1)
    closeChest(agent_host)
    time.sleep(1)
    moveToChest(agent_host, 4)
    time.sleep(1)
    openChest(agent_host)
    time.sleep(1)
    closeChest(agent_host)
    time.sleep(1)
    moveToChest(agent_host, 7)
    time.sleep(1)
    openChest(agent_host)
    time.sleep(1)
    closeChest(agent_host)
    time.sleep(1)


def fillRandomInput(inputs):
    global diamond_distribution

    input_stream = [];
    for x in range(inputs):
        appendValue = ""
        if randint(101) / 100 < diamond_distribution:
            appendValue += "diamond:{}".format(randint(5) + 1)
        else:
            appendValue += "stone:{}".format(randint(20) + 1)
        input_stream.append(appendValue)
    return input_stream


if __name__ == '__main__':
    # Create default Malmo objects:
    agent_host = MalmoPython.AgentHost()

    size = -1
    itemDist = []
    valDist = {}
    probTotal = 0
    EPSILON = 0.0001
    while size == -1 or itemDist == []:
        try:
            if size == -1:
                size = int(input("Pass integer for size of maze: "))
            toRetrieve = input("Enter probability distribution in format of ([itemID]:[probItem];... ** NOTE "
                               "PROB MUST SUM TO 1 ** ): ")
            for item in toRetrieve.split(";"):
                key, value = item.split(":")
                probTotal += float(value)
                itemDist.append((key.strip(), probTotal))
                valDist[key.strip()] = float(value)

            if abs(probTotal - 1) > EPSILON:
                raise Exception("Invalid Probability Distribution")
        except Exception as e:
            probTotal = 0
            itemDist = []
            valDist = {}
            print(f"Improper pass, error of {e}")

    runMode = input("Enter r to generate random values and u to input user values: ")
    if runMode == "r":
        trackSteps = []
        userInput = fillRandomInput(100)
        print(userInput)
        for toRetrieve in userInput:
            size = 50
            my_mission = MalmoPython.MissionSpec(GetMissionXML(size), True)
            my_mission_record = MalmoPython.MissionRecordSpec()
            my_mission.requestVideo(800, 500)
            my_mission.setViewpoint(1)
            # Attempt to start a mission:
            max_retries = 3
            my_clients = MalmoPython.ClientPool()
            my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000))

            for retry in range(max_retries):
                try:
                    agent_host.startMission(my_mission, my_clients, my_mission_record, 0, "%s-%d" % ('Moshe', retry))
                    break
                except RuntimeError as e:
                    if retry == max_retries - 1:
                        print("Error starting mission", (retry), ":", e)
                        exit(1)
                    else:
                        time.sleep(2)
            # Loop until mission starts:
            print("Waiting for the mission to start ", end=' ')
            world_state = agent_host.getWorldState()
            while not world_state.has_mission_begun:
                print(".", end="")
                time.sleep(0.1)
                world_state = agent_host.getWorldState()
                for error in world_state.errors:
                    print("Error:", error.text)

            print()

            setupEnv(agent_host, size, itemDist)

            toGet = {}
            total = 0
            for item in toRetrieve.split(";"):
                try:
                    key, value = item.split(":")
                    toGet[key.strip()] = int(value)
                    total += int(value)

                except Exception as e:
                    print(f"Invalid input of '{item}', disregarding as {e}")
            # TODO reformat to ensure that it is possible to retrieve items
            print(f" ---- Retrieving {toGet} into Ender Chest ---- ")

            # Methods 1, Brute Force

            bruteForceRetrieve(agent_host, toGet, size)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
            print("Ended")
            end(agent_host, world_state)
            if int(toRetrieve.split(':')[1]) != 0:
                trackSteps.append(num_moves / int(toRetrieve.split(':')[1]) * valDist[toRetrieve.split(':')[0]])
            else:
                trackSteps.append(0)

            print(trackSteps)
            num_moves = 0
            agent_position = 0

        plt.clf()
        plt.plot(trackSteps)
        plt.title('Library')
        plt.ylabel('Steps')
        plt.xlabel('Run')
        plt.savefig('returnsfinalpart.png')
    else:
        # todo adapt to inputted sizes
        my_mission = MalmoPython.MissionSpec(GetMissionXML(size), True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.requestVideo(800, 500)
        my_mission.setViewpoint(1)
        # Attempt to start a mission:
        max_retries = 3
        my_clients = MalmoPython.ClientPool()
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000))
        agent_host.startMission(my_mission, my_clients, my_mission_record, 0, "%s-%d" % ('Moshe', 0))
        # Loop until mission starts:
        print("Waiting for the mission to start ", end=' ')
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            print(".", end="")
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)

        toRetrieve = input("Enter values to retrieve in format of ([itemToRetrieve]:[numItems];...): ")

        # MonteCarlo == METHOD Multi Armed Bandit is general problem -- dig through this.
        while toRetrieve != "q":

            setupEnv(agent_host, size, itemDist)

            toGet = {}
            total = 0
            for item in toRetrieve.split(";"):
                try:
                    key, value = item.split(":")
                    toGet[key.strip()] = int(value)
                    total += int(value)

                except Exception as e:
                    print(f"Invalid input of '{item}', disregarding as {e}")
            # TODO reformat to ensure that it is possible to retrieve items
            print(f" ---- Retrieving {toGet} into Ender Chest ---- ")

            # Methods 1, Brute Force
            print(agent_position)
            bruteForceRetrieve(agent_host, toGet, size)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
            print("Ended")
            end(agent_host, world_state)
            toRetrieve = input("Enter values to retrieve in format of ([itemToRetrieve]:[numItems];...): ")