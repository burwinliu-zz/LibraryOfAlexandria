import random


class Requester:
    # Reward is how agent learns, + good, - bad
    # Class agent
    #   Param: maxRequest
    #   getRequest()
    #   getReward(steps, actualResponse, actualRequest)
    # { randoM) < .4  stone, < .8, diamond, < 1, fence }
    # get
    # complexity level 0 == single request, constant distribution
    def __init__(self, max_req, available_input, complexity_level):
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
            self.stepWeights = lambda x: x*-1

        # Random numbers, probability get_request, get_reward

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
