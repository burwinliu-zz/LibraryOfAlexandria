import random
import time
from pathlib import Path

import json

class Requester:
    # Reward is how agent learns, + good, - bad
    # Class agent
    #   Param: maxRequest
    #   getRequest()
    #   getReward(steps, actualResponse, actualRequest)
    # { randoM) < .4  stone, < .8, diamond, < 1, fence }
    # get
    # complexity level 0 == single request, constant distribution
    def __init__(self, max_req, available_input, complexity_level, file_path=None):
        if file_path is not None:
            # Load dictionaries of self.max_req, self.available, self._items, self.probDist, self.passedReward,
            #   self.failedReward and self.stepWeights instead of custom init.
            with open(file_path) as json_file:
                data = json.load(json_file)
                self.max_req = data["max_req"]
                self.available = data["available"]
                self._items = data["_items"]
                self.probDist = data["probDist"]
            self.passedReward = {i: lambda x: 0 for i in self._items}
            self.failedReward = {i: lambda x: x * -100 for i in self._items}
            self.stepWeights = lambda x: x * -1
            return

        # Max num requests to provide
        self.max_req = max_req
        # Items possible, dict of items to number of stacks
        self.available = {i: j//64 for i, j in available_input.items()}
        self._items = [i for i in available_input.keys()]
        # Sorted array of items, tuples, 2 items (item_id, probability)
        self.probDist = []
        if complexity_level == 0:
            self.probDist = [(self._items[random.randint(0, len(available_input)-1)], 1)]

        self.passedReward = {i: lambda x: 0 for i in self._items}
        self.failedReward = {i: lambda x: x * -100 for i in self._items}
        self.stepWeights = lambda x: x * -1
        # Random numbers, probability get_request, get_reward
        if complexity_level == 1:
            # Random distribution of multiple objects, restricted to max_req number of objects
            validNums = [i for i in range(len(available_input))]
            while len(validNums) > max_req:
                validNums.pop(random.randint(0, len(available_input)-1))
            randomNums = sorted([random.random() for _ in range(len(validNums))])
            randomNums[-1] = 1
            print(available_input, validNums, randomNums)
            self.probDist = [(self._items[i], randomNums[i]) for i in range(len(validNums))]

        if complexity_level == 2:
            # Random distribution for all objects
            randomNums = sorted([random.random() for _ in range(len(available_input))])
            randomNums[-1] = 1

            self.probDist = [(self._items[i], randomNums[i]) for i in range(len(available_input))]
        return

    def get_request(self):
        # .4 diamond, .6 stone
        # law large numbers [ average ]
        # Get stone only
        # Get only diamonds
        #   .4 -> .8 [ requests -> average ]  RESETS at every episode -> main issue would be that the agents
        # reward is not well defined here? so this would be increasingly hard to do.
        request = {}
        for i in range(self.max_req):
            randomized = random.random()
            for j in self.probDist:
                if randomized < j[1]:
                    if j[0] not in request:
                        request[j[0]] = 0
                    if request[j[0]] < self.available[j[0]]:
                        request[j[0]] += 1
                    break
        return request

    def get_reward(self, request, response, steps):
        # TODO add stochastic here for rewards
        reward = 0
        print(f"REWARD REQUESTED FROM {request} {response} {steps}")
        for i, j in response.items():
            reward += self.passedReward[i](j)
            request[i] -= j
        for i, j in request.items():
            reward += self.failedReward[i](j)
        return reward + self.stepWeights(steps)

    def save_requester(self, path=None):
        # Given a path, save requester at that location (saving self.max_req, self.available, self._items).
        #   Optional parameter of location,
        #   else default to current time at the savedRequester directory
        if path is None:
            t = time.localtime()
            current_time = time.strftime("%Y_%j_%H_%M_%S_requester", t)
            path = Path(__file__).parent.absolute().joinpath("savedRequester").joinpath(current_time)

            toSave = {
                "max_req": self.max_req,
                "available": self.available,
                "_items": self._items,
                "probDist": self.probDist
            }
            with open(path, 'w') as f:
                json.dump(toSave, f)
        return path
