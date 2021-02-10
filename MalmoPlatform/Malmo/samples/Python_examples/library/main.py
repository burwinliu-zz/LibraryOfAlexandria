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
    for i in range(-1,15,2):
        torches += f"<DrawBlock x='{i}' y='5' z='1' type='torch' face='NORTH' />"
        torches += f"<DrawBlock x='{i}' y='7' z='1' type='torch' face='NORTH' />"
        torches += f"<DrawBlock x='{i}' y='9' z='1' type='torch' face='NORTH' />"
        torches += f"<DrawBlock x='{i}' y='5' z='-9' type='torch' face='SOUTH' />"
        torches += f"<DrawBlock x='{i}' y='7' z='-9' type='torch' face='SOUTH' />"
        torches += f"<DrawBlock x='{i}' y='9' z='-9' type='torch' face='SOUTH' />"
    for i in range(-9,2,2):
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
                                    <DrawBlock x='0' y='2' z='1' type='ender_chest' />{libraryEnv}
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

def end(agent_host, world_state):
    print("Ending Mission", end = ' ')
    while world_state.is_mission_running:
        print(".", end="")
        agent_host.sendCommand("moveeast")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:",error.text)

def moveLeft(agent_host, steps):
    for i in range(steps):
        agent_host.sendCommand("moveeast")
        time.sleep(0.1)

def moveRight(agent_host, steps):
    for i in range(steps):
        agent_host.sendCommand("movewest")
        time.sleep(0.1)

def moveToChest(agent_host, chestNum):
    global agent_position
    if agent_position == chestNum:
        return
    print(f"Moving to chest #{chestNum} ..", end=' ')
    if chestNum == 7: # if moving to ender chest
        while agent_position < 6: # move to chest 6
            moveRight(agent_host, 2)
            agent_position += 1
        moveRight(agent_host, 3) # move to ender chest
        agent_position = 7
        print("done")
        return
    if agent_position == 7: # if starting at ender chest
        moveLeft(agent_host, 3) # move to chest 6
        agent_position = 6
        while chestNum < agent_position: # move to chest
            moveLeft(agent_host, 2)
            agent_position -= 1
        print("done")
        return
    # moving chest -> chest
    if agent_position > chestNum: # if chest is on the left
        while agent_position > chestNum:
            moveLeft(agent_host, 2)
            agent_position -= 1
    elif agent_position < chestNum: # if chest is on the right
        while agent_position < chestNum:
            moveRight(agent_host, 2)
            agent_position += 1
    print("done")

def openChest(agent_host):
    agent_host.sendCommand("use 1")
    time.sleep(0.1)
    agent_host.sendCommand("use 0")

def closeChest(agent_host):
    for i in range(10):
        agent_host.sendCommand("movenorth")
    time.sleep(0.1)
    for i in range(10):
        agent_host.sendCommand("movesouth")

def testRun(agent_host):
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
            print("Error:",error.text)

    print()
    print("Mission running..")

    print("Setting up chests..", end=' ')
    size = 6
    items = {'stone': 50, 'diamond': 30}

    chests = [{} for _ in range(size)]
    for i, j in items.items():
        for _ in range(j):
            nChest = int(random() * size)
            if i not in chests[nChest]:
                chests[nChest][i] = 0
            chests[nChest][i] += 1
    for i in range(size):
        # /setblock ~3 ~2 ~1 minecraft:chest 2 replace {Items:[{Slot:0,id:stone,Count:1b}]}

        itemString = ",".join([f"{{Slot:{num}, id:{value[0]},Count:{value[1]}b}}"
                               for num, value in enumerate(chests[i].items())])
        agent_host.sendCommand(f"chat /setblock {i * 2 + 3} 2 1 minecraft:chest 2 replace {{Items:[{itemString}]}}")
    print("done")

    testRun(agent_host)
    end(agent_host, world_state)

    print()
    print("Mission ended")