import json
import time

import numpy
import gym, ray
from gym.spaces import Discrete, Box
import matplotlib.pyplot as plt
from ray.rllib.agents import ppo

try:
    from malmo import MalmoPython
except ImportError:
    import MalmoPython

import matplotlib
from Requester import Requester

matplotlib.use('TKAgg')


class Librarian(gym.Env):
    def __init__(self, env_config):
        self.agent = MalmoPython.AgentHost()
        # env_config contains info, including items, etc.

        # These are the dict of items that are to be distributed, key = item; value = number of item
        self._env_items = env_config['items']
        # number of chests
        self.obs_size = env_config['chestNum']
        # map to enable one-hot mapping
        self.map = env_config['mapping']
        # reverse mapping
        self.rMap = env_config['rmapping']
        # maximum items per chest to enqable
        self.max_items_per_chest = env_config['max_per_chest']

        # Contents of chests key = item; value = set of items positions
        self._itemPos = {}
        self._placingInventory = []
        self._chestContents = []
        # Ideas: record next open slot per chest
        self._chestPosition = []
        # Percentage for failure to open in a chest
        self._stochasticFailure = numpy.random.random(self.obs_size)
        self._inventory = {}
        self._nextOpen = 0

        # model params
        self._episode_score = 0
        self.agent_position = 0
        self.episode_number = 0
        self.returns = []
        self.inv_number = 0
        self.item = 0
        self.obs = numpy.zeros(shape=(self.obs_size + 1, self.max_items_per_chest, len(self._env_items)))
        self.world_obs = None
        # self._input_dist = sorted(numpy.random.random((len(self._env_items),)))

        # required for RLLib
        self.action_space = Discrete(self.obs_size)
        self.observation_space = Box(0, 1,
                                     shape=((self.obs_size + 1) * self.max_items_per_chest * len(self._env_items),),
                                     dtype=numpy.float32)
        # For quick training
        self._display = False
        self._printLogs = True

        #  todo code class for requester
        # nondeterm situation occuring when get reward at times
        self._requester = env_config['requester']

    def _optimal_retrieve(self, input: dict):
        """
            input: dict of objects to retrieve in format of {key: object_id, value: number to retrieve}
            Assumed that the self._itemPos is properly updated and kept done well
        """
        action_plan = []
        result = {}
        for item_id, num_retrieve in input.items():
            if len(self._itemPos[item_id]) > 0:
                # Therefore can retrieve, else you dun messed up
                pq_items = sorted([i for i in self._itemPos[item_id]])
                if self._printLogs:
                    print(self._itemPos)
                    print(self._chestContents)
                    print(pq_items)
                    print(num_retrieve)
                    print(item_id)
                # Now we pop until we find
                while num_retrieve > 0 and len(pq_items) > 0:
                    toConsider = pq_items.pop()
                    # TODO Failure may occur on a chest, simulate here
                    chest = self._chestContents[toConsider]
                    if num_retrieve <= len(chest[item_id]):
                        toRetrieve = num_retrieve
                    else:
                        toRetrieve = len(chest[item_id])
                    action_plan.append((toConsider, item_id, toRetrieve))
                    if item_id not in result:
                        result[item_id] = 0
                    result[item_id] += 1
                    num_retrieve -= toRetrieve

        action_plan = sorted(action_plan, key=lambda x: x[0])  # Sort by the first elemetn in the tuple
        score = 0
        for position, item, num_retrieve in action_plan:
            # Should be in order from closest to furthest and retreiving the items so we should be able to execute
            #   from here
            score += self.moveToChest(position + 1, True)
            score += self.openChest(True)
            self.getItems({item: num_retrieve})
            score += self.closeChest(True)
        score += self.moveToChest(0, True)
        if self._display:
            score += self.openChest()
            # Max position item should be at
            for i in range(self._nextOpen):
                self.invAction("swap", i, i)
            score += self.closeChest()
        return result, score

    def step(self, action):
        """
        Take an action in the environment and return the results.

        Args
            action: <int> index of the action to take

        Returns
            observation: <np.array> flattened array of obseravtion
            reward: <int> reward from taking action
            done: <bool> indicates terminal state
            info: <dict> dictionary of extra information
        """
        # item to be placed
        if self._printLogs:
            print(f" ACTION {action}, {self.action_space}, {self.observation_space}")
            print(self.inv_number)
            print(self.item)
        if action == 0:
            action = self.obs_size
        reward = 0
        if self._display:
            time.sleep(0.2)
            self.moveToChest(action)
            self.openChest()
        else:
            self.moveToChest(action, True)
            self.openChest(True)
        
        # new observation
        # TODO ask him about this one Do not want to be doing entire episode in one function -- each time step is
        #  called, place once.
        #   IF PLACED ALL ITEMS, then retrieve and calculate rewards based on ONLY if the retrieval is done
        #   ADD MORE STOCHASITICITY IN CHESTS _> bad movement to "wrong" place -- agent has to be more robust with
        #       placement
        for i, x in enumerate(self.obs[self.agent_position]):
            if not any(self.obs[self.agent_position][i]):
                if self._printLogs:
                    print(self.obs[self.agent_position][i])
                if self._display:
                    self.invAction("swap", self.inv_number, i)
                self.obs[self.agent_position][i][self.item] = 1
                self._itemPos[self.rMap[self.item]].add(self.agent_position - 1)
                self._chestContents[self.agent_position - 1][self.rMap[self.item]].append(i)
                # clear since item has been placed
                self.obs[0][0] = numpy.zeros(shape=len(self._env_items))
                break
        
        if self._display:
            time.sleep(1)
            self.closeChest()
        else:
            self.closeChest(True)
        done = False
        if self._display:
            if self.world_obs:
                for x in self.world_obs:
                    if "Inventory" in x and "item" in x:
                        if self.world_obs[x] != 'air':
                            self.inv_number = int(x.split("_")[1])
                            self.item = self.map[self.world_obs[x]]
                            # set next item to be place
                            self.obs[0][0][self.item] = 1
                            break
                else:
                    # if for loop doesn't break that means only air was found we are done and compute final reward
                    done = True
                    self.moveToChest(0)
                    to_retrieve = self._requester.get_request()
                    retrieved_items, score = self._optimal_retrieve(to_retrieve)
                    reward = self._requester.get_reward(to_retrieve, retrieved_items, score)
        else:
            for i, x in enumerate(self._placingInventory):
                if x != -1:
                    self.item = x
                    self.inv_number = i
                    self._placingInventory[i] = -1
                    self.obs[0][0][self.item] = 1
                    break
            else:
                done = True
                self.moveToChest(0 ,True)
                to_retrieve = self._requester.get_request()
                retrieved_items, score = self._optimal_retrieve(to_retrieve)
                reward = self._requester.get_reward(to_retrieve, retrieved_items, score)


        if self._printLogs:
            print(self.obs)
        if done:
            # end malmo mission
            self.moveToChest(-1)
            time.sleep(0.1)
            self._episode_score += reward
            world_state = self.agent.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
            done = not world_state.is_mission_running
            done = True
        if self._printLogs:
            print(done)

        # 0 reward if no retrieve
        return self.obs.flatten(), reward, done, dict()

    def GetMissionXML(self):
        leftX = self.obs_size * 2 + 2
        front = f"<DrawCuboid x1='{leftX}' y1='0' z1='2' x2='-4' y2='10' z2='2' type='bookshelf' />"
        right = f"<DrawCuboid x1='-4' y1='0' z1='2' x2='-4' y2='10' z2='-10' type='bookshelf' />"
        left = f"<DrawCuboid x1='{leftX}' y1='0' z1='2' x2='{leftX}' y2='10' z2='-10' type='bookshelf' />"
        back = f"<DrawCuboid x1='{leftX}' y1='0' z1='-10' x2='-4' y2='10' z2='-10' type='bookshelf' />"
        floor = f"<DrawCuboid x1='{leftX}' y1='1' z1='-10' x2='-4' y2='1' z2='2' type='bookshelf' />"
        libraryEnv = front + right + left + back + floor
        item = f""
        for items in self._env_items:
            for x in range(self._env_items[items]):
                item += f"<DrawItem x='0' y='0' z='1' type='{items}' />"
        chests = f"<DrawBlock x='0' y='2' z='1' type='air' />" +\
                 f"<DrawBlock x='0' y='2' z='1' type='chest' />"
        for chest_num in range(self.obs_size):
            chests += f"<DrawBlock x='{chest_num * 2 + 2}' y='2' z='1' type='air' />"
            chests += f"<DrawBlock x='{chest_num * 2 + 2}' y='2' z='1' type='chest' />"
            chests += f"<DrawBlock x='{chest_num * 2 + 2}' y='1' z='0' type='diamond_block' />"
        chests += f"<DrawBlock x='0' y='2' z='1' type='chest' />"

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
                                        {item}
                                        {chests}
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
                                    <Inventory>
                                    </Inventory>
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
                                            <min x="-{int(self.obs_size / 2)}" y="-1" z="-{int(self.obs_size / 2)}"/>
                                            <max x="{int(self.obs_size / 2)}" y="0" z="{int(self.obs_size / 2)}"/>
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
        self.world_obs = None
        while self.world_obs is None:
            time.sleep(toSleep)
            toSleep += .2
            try:
                cur_state = self.agent.getWorldState()
                self.world_obs = json.loads(cur_state.observations[-1].text)
            except IndexError:
                print("retrying...")

    # Primative move actions
    def moveLeft(self, steps, retrieval=False):
        if self._display or not retrieval:
            for i in range(steps):
                self.agent.sendCommand("moveeast")
                time.sleep(0.05)
        return steps

    def moveRight(self, steps, retrieval=False):
        if self._display  or not retrieval:
            for i in range(steps):
                self.agent.sendCommand("movewest")
                time.sleep(0.05)
        return steps

    def openChest(self, retrieval=False):
        if self._display or not retrieval:
            self.agent.sendCommand("use 1")
            time.sleep(0.05)
            self.agent.sendCommand("use 0")
            time.sleep(0.05)
        return 1

    def closeChest(self, retrieval=False):
        if self._display or not retrieval:
            for _ in range(10):
                self.agent.sendCommand("movenorth")
            time.sleep(0.1)
            for _ in range(10):
                self.agent.sendCommand("movesouth")
            time.sleep(0.1)
        return 1

    # Complex Move actions
    def moveToChest(self, chest_num, retrieval=False):

        if self.agent_position == chest_num:
            return 0
        if chest_num != -1 and self._printLogs:
            print(f"Moving to chest #{chest_num} ..")
        if self.agent_position - chest_num < 0:
            result = self.moveLeft(2 * abs(self.agent_position - chest_num), retrieval)
        else:
            result = self.moveRight(2 * abs(self.agent_position - chest_num),retrieval)
        self.agent_position = chest_num
        time.sleep(.05)
        return result

    def invAction(self, action, inv_index, chest_index):
        self._updateObs()
        if "inventoriesAvailable" in self.world_obs:
            chestName = self.world_obs["inventoriesAvailable"][-1]['name']
            self.agent.sendCommand(f"{action}InventoryItems {inv_index} {chestName}:{chest_index}")
            time.sleep(0.05)
            self._updateObs()

    def getItems(self, query):
        """
            query = dict{ key = itemId: value = number to retrieve }
        """
        # TODO Fix this to fit with the Librarian Class
        chest = self._chestContents[self.agent_position - 1]
        for itemId, toRetrieve in query.items():
            for i in range(toRetrieve):
                try:
                    posToGet = chest[itemId].pop()
                except IndexError:
                    print("Bad retrieval, should not have happened, somewhere we did not update properly")
                    break
                # Create a new slot for this new item, and deposit there
                if itemId not in self._inventory:
                    self._inventory[itemId] = set()
                self._inventory[itemId].add(self._nextOpen)
                if self._display:
                    self.invAction("swap", self._nextOpen, posToGet)
                self._nextOpen += 1

                time.sleep(.05)
            # update if we have retrieved all said items within the chest
            if len(chest[itemId]) == 0:
                del self._chestContents[self.agent_position - 1][itemId]
                self._itemPos[itemId].remove(self.agent_position - 1)

    def reset(self):
        """
        Resets the environment for the next episode.

        Returns
            observation: <np.array> flattened initial obseravtion
        """
        # Reset Malmo
        self.episode_number += 1
        world_state = self.init_malmo()
        time.sleep(1)
        self.obs = numpy.zeros(shape=(self.obs_size + 1, self.max_items_per_chest, len(self._env_items)))
        self.returns.append(self._episode_score)
        if self._printLogs:
            print(self.returns)
        if self.episode_number % 10 == 0:
            self.log()
        self._episode_score = 0
        self.agent_position = 0
        self._placingInventory = []
        self._updateObs()
        for x in self.world_obs:
            if "Inventory" in x and "item" in x:
                if self._display:
                    if self.world_obs[x] != 'air':
                        self.inv_number = int(x.split("_")[1])
                        self.item = self.map[self.world_obs[x]]
                        break
                else:
                    if self.world_obs[x] in self.map:
                        self._placingInventory.append(self.map[self.world_obs[x]])
                    else:
                        self._placingInventory.append(-1)
        if self._display:
            for i, x in enumerate(self._placingInventory):
                if x != -1:
                    self.item = x
                    self.inv_number = i
                    self._placingInventory[i] = -1
                    break

        self._itemPos = {}
        for items in self.map:
            self._itemPos[items] = set()
        self._chestContents = []
        for chests in range(self.obs_size):
            self._chestContents.append({})
            for items in self.map:
                self._chestContents[chests][items] = []
        self._inventory = {}
        self._nextOpen = 0
        self.obs[0][0][self.item] = 1

        return self.obs.flatten()

    def log(self):
        plt.clf()
        plt.plot(self.returns[1:])
        plt.title('Librarian')
        plt.ylabel('Reward')
        plt.xlabel('Cycles')
        plt.savefig('rer.png')

    def init_malmo(self):
        """
        Initialize new malmo mission.
        """
        my_mission = MalmoPython.MissionSpec(self.GetMissionXML(), True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.requestVideo(800, 500)
        my_mission.setViewpoint(1)

        max_retries = 3
        my_clients = MalmoPython.ClientPool()
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000))  # add Minecraft machines here as available

        for retry in range(max_retries):
            try:

                time.sleep(3)
                self.agent.startMission(my_mission, my_clients, my_mission_record, 0,
                                        'Librarian' + str(self.episode_number))
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:", e)
                    exit(1)
                else:
                    time.sleep(2)

        world_state = self.agent.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = self.agent.getWorldState()
            for error in world_state.errors:
                print("\nError:", error.text)

        return world_state


if __name__ == '__main__':
    # ray.shutdown()
    # ray.init()
    env = {}
    env['items'] = {'stone': 128, 'diamond': 64, 'glass': 64, 'ladder': 128, 'brick': 64, 'dragon_egg': 128 * 3}
    env['mapping'] = {'stone': 0, 'diamond': 1, 'glass': 2, 'ladder': 3, 'brick': 4, 'dragon_egg': 5}
    env['rmapping'] = {0: 'stone', 1: 'diamond', 2: 'glass', 3: 'ladder', 4: 'brick', 5: 'dragon_egg'}

    env['chestNum'] = 10
    env['max_per_chest'] = 3
    env['requester'] = Requester(5, env['items'], 0)
    trainer = ppo.PPOTrainer(env=Librarian, config={
        'env_config': env,  # No environment parameters to configure
        'framework': 'torch',  # Use pyotrch instead of tensorflow
        'num_gpus': 0,  # We aren't using GPUs
        'num_workers': 0  # We aren't using parallelism
    })

    while True:
        print(trainer.train())
