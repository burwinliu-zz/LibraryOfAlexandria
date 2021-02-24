class Requester:
    def __init__(self, max_input, stochastic, available_input):
        self.max_input = max_input
        self.stochastic = stochastic
        self.available = available_input

    def get_request(self):
        return {}

    def get_reward(self, request, response, steps):
        return -1
