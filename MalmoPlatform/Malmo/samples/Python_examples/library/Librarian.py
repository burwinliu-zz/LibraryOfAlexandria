import json
import time

import numpy
import gym

try:
    from malmo import MalmoPython
except ImportError:
    import MalmoPython


class Librarian(gym.Env):
    def __init__(self, env_config):
        self.agent = MalmoPython.AgentHost()
        self.obs = None
        # env_config contains info, including items, etc.

        # These are the dict of items that are to be distributed, key = item; value = number of item
        self._env_items = env_config['items']
        self._input_dist = sorted(numpy.random.random((len(self._env_items),)))

        # Contents of chests key = item; value = priorityQueue of items, sorted by position
        self._itemPos = {}

        self._episode_score = 0
        self.agent_position = 0

    def _optimal_retrieve(self):
        pass

    def GetMissionXML(self, obs_size):
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

    def _updateObs(self):
        toSleep = .1
        self.obs = None
        while self.obs is None:
            time.sleep(toSleep)
            toSleep += .2
            try:
                cur_state = self.agent.getWorldState()
                self.obs = json.loads(cur_state.observations[-1].text)
            except IndexError:
                print("retrying...")

    # Primative move actions
    def moveLeft(self, steps):
        self._episode_score += steps
        for i in range(steps):
            self.agent.sendCommand("moveeast")
            time.sleep(0.1)

    def moveRight(self, steps):
        self._episode_score += steps
        for i in range(steps):
            self.agent.sendCommand("movewest")
            time.sleep(0.1)

    def openChest(self):
        self._episode_score += 1
        self.agent.sendCommand("use 1")
        time.sleep(0.1)
        self.agent.sendCommand("use 0")

    def closeChest(self):
        self._episode_score += 1
        for _ in range(10):
            self.agent.sendCommand("movenorth")
        time.sleep(0.1)
        for _ in range(10):
            self.agent.sendCommand("movesouth")

    # Complex Move actions
    def moveToChest(self, chest_num):

        if self.agent_position == chest_num:
            return
        if chest_num != -1:
            print(f"Moving to chest #{chest_num} ..")
        if self.agent_position - chest_num < 0:
            self.moveLeft(2 * abs(self.agent_position - chest_num))
        else:
            self.moveRight(2 * abs(self.agent_position - chest_num))
        self.agent_position = chest_num

    def getItemsInChest(self):
        items = {}
        self._updateObs()
        chestName = self.obs["inventoriesAvailable"][-1]['name']
        chestSize = self.obs["inventoriesAvailable"][-1]['size']
        for i in range(chestSize):
            if f"container.{chestName}Slot_{i}_item" in self.obs:
                item = self.obs[f"container.{chestName}Slot_{i}_item"]
                if item == 'air':
                    continue
                if item not in items:
                    items[item] = 0
                items[item] += self.obs[f"container.{chestName}Slot_{i}_size"]

        return items

    def invAction(self, action, inv_index, chest_index):
        self._updateObs()
        chestName = self.obs["inventoriesAvailable"][-1]['name']
        self.agent.sendCommand(f"{action}InventoryItems {inv_index} {chestName}:{chest_index}")

    def getItems(self, searching, inventoryNeeds, ordersMet):
        self._updateObs()
        chestName = self.obs["inventoriesAvailable"][-1]['name']
        chestSize = self.obs["inventoriesAvailable"][-1]['size']
        for i in range(chestSize):

            if f"container.{chestName}Slot_{i}_item" in self.obs:
                item = self.obs[f"container.{chestName}Slot_{i}_item"]
                itemHad = self.obs[f"container.{chestName}Slot_{i}_size"]

                if item == 'air':
                    continue
                if item in searching and len(searching[item]) != 0:
                    inventoryNeeds[searching[item][-1]][1] -= itemHad
                    time.sleep(.2)
                    self.invAction(
                        "combine" if int(self.obs[f"InventorySlot_{searching[item][-1]}_size"]) != 0 else "swap",
                        searching[item][-1], i)
                    if inventoryNeeds[searching[item][-1]][1] == 0:
                        ordersMet += 1
                        if len(searching[item]) == 1:
                            del searching[item][-1]
                        else:
                            searching[item].pop()
            self._updateObs()

        return searching, inventoryNeeds, ordersMet

    def end(self):
        print("Ending Mission", end=' ')
        while self.obs.is_mission_running:
            print(".", end="")
            self.moveToChest(self.agent, -1)
            time.sleep(0.1)
            arg_world_state = self.agent.getWorldState()
            for end_error in self.obs.errors:
                print("Error:", end_error.text)
        print()
