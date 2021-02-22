import json
import time

import numpy
import gym

try:
    from malmo import MalmoPython
except ImportError:
    import MalmoPython


# todo, provide interface for retrieve, store of items, so there is less issue of potential bad updates
class Librarian(gym.Env):
    def __init__(self, env_config):
        self.agent = MalmoPython.AgentHost()
        self.obs = None
        # env_config contains info, including items, etc.

        # These are the dict of items that are to be distributed, key = item; value = number of item
        self._env_items = env_config['items']
        self._input_dist = sorted(numpy.random.random((len(self._env_items),)))

        # Location of items {key = item; value = list of positions}
        self._itemPos = {}
        # Contents of chests -- list of dicts [{key = item, value = [list of positions where they may be found]}]
        self._chestContents = []
        # Inventory positions
        self._inventory = {}
        self._nextOpen = 0

        self._episode_score = 0
        self.agent_position = 0

    def _optimal_retrieve(self, input: dict):
        """
            input: dict of objects to retrieve in format of {key: object_id, value: number to retrieve}

            Assumed that the self._itemPos is porperly updated and kept done well
        """
        action_plan = []
        for item_id, num_retrieve in input.values():
            if item_id in self._itemPos:
                # Therefore can retrieve, else you dun messed up
                pq_items = sorted([i for i in self._itemPos[item_id]], reverse=True)

                # Now we pop until we find
                while num_retrieve > 0:
                    toConsider = pq_items.pop()
                    chest = self._chestContents[toConsider]
                    if num_retrieve <= len(chest[item_id]):
                        toRetrieve = num_retrieve
                    else:
                        toRetrieve = len(chest[item_id])
                    action_plan.append((toConsider, item_id, toRetrieve))
                    num_retrieve -= toRetrieve

        # TODO merge actions at one chest if they arise
        action_plan = sorted(action_plan, key=lambda x: x[0])  # Sort by the first elemetn in the tuple

        for position, item, num_retrieve in action_plan:
            # Should be in order from closest to furthest and retreiving the items so we should be able to execute from here

            self.moveToChest(position)
            self.openChest()
            self.getItems({item: num_retrieve})
            self.closeChest()

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

    def _invAction(self, action, inv_index, chest_index):
        self._updateObs()
        chestName = self.obs["inventoriesAvailable"][-1]['name']
        self.agent.sendCommand(f"{action}InventoryItems {inv_index} {chestName}:{chest_index}")

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

    def getItems(self, query):
        """
            query = dict{ key = itemId: value = number to retrieve }
        """
        # TODO Fix this to fit with the Librarian Class
        chest = self._chestContents[self.agent_position]
        for itemId, toRetrieve in query:
            for i in range(toRetrieve):
                try:
                    posToGet = chest[itemId].pop()
                except IndexError:
                    print("Bad retrieval, should not have happened, somewhere we did not update properly")
                    break
                if itemId in self._inventory:
                    self._invAction("combine", self._inventory[itemId], posToGet)
                else:
                    # Create a new slot for this new item, and deposit there
                    self._inventory[itemId] = self._nextOpen
                    self._nextOpen += 1
                    self._invAction("swap", self._inventory[itemId], posToGet)
                time.sleep(.2)
            # update if we have retrieved all said items within the chest
            if len(chest[itemId]) == 0:
                del self._chestContents[self.agent_position][itemId]
                self._itemPos[itemId].remove(self.agent_position)

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
