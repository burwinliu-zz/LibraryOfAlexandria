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


def GetMissionXML(size, items: dict):
    obs_size = 5

    chests_str = ""
    chests = [{} for _ in range(size)]
    for i, j in items.items():
        for _ in range(j):
            nChest = int(random()*size)
            if i not in chests[nChest]:
                chests[nChest][i] = 0
            chests[nChest][i] += 1

    for i, j in enumerate(chests):
        # <Inventory>
        #                                     <InventoryItem slot="0" type="diamond_pickaxe"/>
        #                                 </Inventory>
        chests_str += f"<DrawBlock x='{i//2 * 2}' y='2' z='{1 if i%2 == 0 else -1}' type='chest'/>\n"

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
                                    <DrawCuboid x1='{-size}' x2='{size}' y1='2' y2='2' z1='{-size}' z2='{size}' type='air'/>
                                    <DrawCuboid x1='{-size}' x2='{size}' y1='1' y2='1' z1='{-size}' z2='{size}' type='stone'/>
                                    {chests_str}
                                </DrawingDecorator>
                                <ServerQuitWhenAnyAgentFinishes/>
                            </ServerHandlers>
                        </ServerSection>

                        <AgentSection mode="Survival">
                            <Name></Name>
                            <AgentStart>
                                <Placement x="0.5" y="2" z="0.5" pitch="40" yaw="0"/>
                                
                            </AgentStart>
                            <AgentHandlers>
                                <DiscreteMovementCommands/>
                                <ObservationFromFullStats/>
                                <ObservationFromRay/>
                                <ObservationFromGrid>
                                    <Grid name="floorAll">
                                        <min x="-{int(obs_size / 2)}" y="-1" z="-{int(obs_size / 2)}"/>
                                        <max x="{int(obs_size / 2)}" y="0" z="{int(obs_size / 2)}"/>
                                    </Grid>
                                </ObservationFromGrid>
                            </AgentHandlers>
                        </AgentSection>
                    </Mission>'''


if __name__ == '__main__':
    # Create default Malmo objects:
    agent_host = MalmoPython.AgentHost()

    my_mission = MalmoPython.MissionSpec(GetMissionXML(6, {'stone': 50, 'diamond': 30}), True)
    my_mission_record = MalmoPython.MissionRecordSpec()
    my_mission.requestVideo(800, 500)
    my_mission.setViewpoint(1)
    # Attempt to start a mission:
    max_retries = 3
    my_clients = MalmoPython.ClientPool()
    my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000))
    agent_host.startMission(my_mission, my_clients, my_mission_record, 0, "%s-%d" % ('Moshe', 0))