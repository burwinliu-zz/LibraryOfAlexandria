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
from priority_dict import priorityDictionary as PQ

agent_position = 7


def GetMissionXML():
    obs_size = 5

    chests_str = "<DrawBlock x='0' y='2' z='1' type='chest'/>\n"
    front = "<DrawCuboid x1='15' y1='0' z1='2' x2='-2' y2='10' z2='2' type='bookshelf' />"
    right = "<DrawCuboid x1='-2' y1='0' z1='2' x2='-2' y2='10' z2='-10' type='bookshelf' />"
    left = "<DrawCuboid x1='15' y1='0' z1='2' x2='15' y2='10' z2='-10' type='bookshelf' />"
    back = "<DrawCuboid x1='15' y1='0' z1='-10' x2='-2' y2='10' z2='-10' type='bookshelf' />"
    roof = "<DrawCuboid x1='15' y1='10' z1='-10' x2='-2' y2='10' z2='2' type='bookshelf' />"
    floor = "<DrawCuboid x1='15' y1='1' z1='-10' x2='-2' y2='1' z2='2' type='bookshelf' />"
    torches = ""
    for i in range(-1, 15, 2):
        torches += f"<DrawBlock x='{i}' y='5' z='1' type='torch' face='NORTH' />"
        torches += f"<DrawBlock x='{i}' y='7' z='1' type='torch' face='NORTH' />"
        torches += f"<DrawBlock x='{i}' y='9' z='1' type='torch' face='NORTH' />"
        torches += f"<DrawBlock x='{i}' y='5' z='-9' type='torch' face='SOUTH' />"
        torches += f"<DrawBlock x='{i}' y='7' z='-9' type='torch' face='SOUTH' />"
        torches += f"<DrawBlock x='{i}' y='9' z='-9' type='torch' face='SOUTH' />"
    for i in range(-9, 2, 2):
        torches += f"<DrawBlock x='14' y='5' z='{i}' type='torch' face='WEST' />"
        torches += f"<DrawBlock x='14' y='7' z='{i}' type='torch' face='WEST' />"
        torches += f"<DrawBlock x='14' y='9' z='{i}' type='torch' face='WEST' />"
        torches += f"<DrawBlock x='-1' y='5' z='{i}' type='torch' face='EAST' />"
        torches += f"<DrawBlock x='-1' y='7' z='{i}' type='torch' face='EAST' />"
        torches += f"<DrawBlock x='-1' y='9' z='{i}' type='torch' face='EAST' />"
    libraryEnv = front + right + left + back + roof + floor + torches

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
                                    <DrawBlock x='0' y='2' z='1' type='ender_chest' />
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
                                <AgentQuitFromReachingPosition>
                                    <Marker x="15" y="2" z="0.5" tolerance="0.5" description="Goal_found"/>
                                </AgentQuitFromReachingPosition>
                            </AgentHandlers>
                        </AgentSection>
                    </Mission>'''


def end(arg_agent_host, arg_world_state):
    print("Ending Mission", end=' ')
    while arg_world_state.is_mission_running:
        print(".", end="")
        arg_agent_host.sendCommand("moveeast")
        time.sleep(0.1)
        arg_world_state = arg_agent_host.getWorldState()
        for end_error in world_state.errors:
            print("Error:", end_error.text)


def moveLeft(arg_agent_host, steps):
    for i in range(steps):
        arg_agent_host.sendCommand("moveeast")
        time.sleep(0.1)


def moveRight(arg_agent_host, steps):
    for i in range(steps):
        arg_agent_host.sendCommand("movewest")
        time.sleep(0.1)


def moveToChest(arg_agent_host, chest_num):
    global agent_position
    if agent_position == chest_num:
        return
    print(f"Moving to chest #{chest_num} ..", end=' ')
    if chest_num == 7:  # if moving to ender chest
        while agent_position < 6:  # move to chest 6
            moveRight(arg_agent_host, 2)
            agent_position += 1
        moveRight(arg_agent_host, 3)  # move to ender chest
        agent_position = 7
        print("done")
        return
    if agent_position == 7:  # if starting at ender chest
        moveLeft(arg_agent_host, 3)  # move to chest 6
        agent_position = 6
        while chest_num < agent_position:  # move to chest
            moveLeft(arg_agent_host, 2)
            agent_position -= 1
        print("done")
        return
    # moving chest -> chest
    if agent_position > chest_num:  # if chest is on the left
        while agent_position > chest_num:
            moveLeft(arg_agent_host, 2)
            agent_position -= 1
    elif agent_position < chest_num:  # if chest is on the right
        while agent_position < chest_num:
            moveRight(arg_agent_host, 2)
            agent_position += 1
    print("done")


def openChest(arg_agent):
    arg_agent.sendCommand("use 1")
    time.sleep(0.1)
    arg_agent.sendCommand("use 0")


def closeChest(arg_agent):
    for _ in range(10):
        arg_agent.sendCommand("movenorth")
    time.sleep(0.1)
    for _ in range(10):
        arg_agent.sendCommand("movesouth")


def _swap_item_to_inventory(arg_agent, pos_chest, pos_inventory):
    #     swapInventoryItems 3 Chest:0
    arg_agent.sendCommand(f"swapInventoryItems {pos_inventory} Chest:{pos_chest} ")
    print(f"swapInventoryItems {pos_inventory} Chest:{pos_chest} ")


def printItemsInChest(agent_host):
    items = {}
    world_state = agent_host.getWorldState()
    obs = json.loads(world_state.observations[-1].text)
    chestName = obs["inventoriesAvailable"][-1]['name']
    chestSize = obs["inventoriesAvailable"][-1]['size']
    for i in range(chestSize):
        item = obs[f"container.{chestName}Slot_{i}_item"]
        if item == 'air':
            continue
        if item not in items:
            items[item] = 0
        items[item] += obs[f"container.{chestName}Slot_{i}_size"]

    print("Items in this chest:")
    print("________________________")
    for key, value in items.items():
        print(f"{key} :: {value}")
    print("________________________\n\n")


def invAction(agent_host, action, inv_index, chest_index):
    world_state = agent_host.getWorldState()
    obs = json.loads(world_state.observations[-1].text)
    chestName = obs["inventoriesAvailable"][-1]['name']
    chestSize = obs["inventoriesAvailable"][-1]['size']
    print(chestName)
    agent_host.sendCommand(f"{action}InventoryItems {inv_index} {chestName}:{chest_index}")


def setupEnv(env_agent, env_size, env_items):
    print("Setting up chests..", end=' ')

    chests = [{} for _ in range(env_size)]
    for i, j in env_items.items():
        for _ in range(j):
            nChest = int(random() * env_size)
            if i not in chests[nChest]:
                chests[nChest][i] = 0
            chests[nChest][i] += 1
    for chest_num in range(env_size):
        num = 0
        itemString = ""
        for item in chests[chest_num].keys():
            while chests[chest_num][item] > 64 and num < 28:
                itemString += f"{{Slot:{num}, id:{item},Count:{64}b}},"
                num += 1
                chests[chest_num][item] -= 64
            if chests[chest_num][item] < 64 and num < 28:
                itemString += f"{{Slot:{num}, id:{item},Count:{chests[chest_num][item]}b}},"
                num += 1
            elif chest_num < env_size - 1:
                chests[chest_num + 1][item] += chests[chest_num][item]
        env_agent.sendCommand(f"chat /setblock {chest_num * 2 + 3} 1 0 minecraft:diamond_block 2 replace")
        env_agent.sendCommand(f"chat /setblock {chest_num * 2 + 3} 2 1 "
                              f"minecraft:chest 2 replace {{Items:[{itemString[:-1]}]}}")
        print(f"chat /setblock {chest_num * 2 + 3} 2 1 "
              f"minecraft:chest 2 replace {{Items:[{itemString[:-1]}]}}")
    print("done")


def testRun2(agent_host):
    size = 6
    items = {'stone': 64, 'diamond': 64}

    setupEnv(agent_host, size, items)
    time.sleep(1)
    moveToChest(agent_host, 6)
    time.sleep(0.5)
    openChest(agent_host)
    time.sleep(0.5)
    printItemsInChest(agent_host)
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
        printItemsInChest(agent_host)
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
    printItemsInChest(agent_host)
    time.sleep(0.5)
    invAction(agent_host, "swap", 0, 0)
    time.sleep(0.25)
    invAction(agent_host, "swap", 1, 1)
    time.sleep(0.25)
    printItemsInChest(agent_host)
    time.sleep(0.5)
    closeChest(agent_host)
    time.sleep(0.5)


def testRun(agent_host):
    size = 6
    items = {'stone': 64, 'diamond': 64}

    setupEnv(agent_host, size, items)
    time.sleep(1)
    moveToChest(agent_host, 3)
    time.sleep(1)
    openChest(agent_host)
    time.sleep(1)
    _swap_item_to_inventory(agent_host, 0, 0)
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


if __name__ == '__main__':
    # Create default Malmo objects:
    agent_host = MalmoPython.AgentHost()

    my_mission = MalmoPython.MissionSpec(GetMissionXML(), True)
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

    print()
    print("Mission running..")
    # Setup env here, and being running test run

    testRun2(agent_host)
    end(agent_host, world_state)

    print()
    print("Mission ended")

    toRetrieve = ""

    while toRetrieve != "q":
        toRetrieve = input("Enter values to retrieve in format of ([itemToRetrieve]:[numItems];...): ")
        toGet = {}
        for item in toRetrieve.split(";"):
            try:
                key, value = item.split(":")
                toGet[key.strip()] = int(value)
            except Exception as e:
                print(f"Invalid input of '{item}', disregarding as {e}")
        print(f" ---- Retrieving {toGet} into Ender Chest ---- ")


