"""
    Display a Librian run, given a path to the saved location
"""
from Requester import Requester
from Librarian import Librarian

if __name__ == '__main__':
    # Choose one of two to set up req path to given position
    # req_path = input("Requester Path: ")
    # lib_path = input('Lib Path: ')
    # stochastic_array = input('Chest Changes: ')

    req_path = "test"
    lib_path = "test"
    stochastic_array = [0.35995969, 0.679561, 0.140505, 0.16909558, 0.969226, 0.62966605, 0.18746248, 0.90296069,
                        0.76486581, 0.90063654]

    # ray.shutdown()
    # ray.init()
    env = {
        'items': {'stone': 128, 'diamond': 64, 'glass': 64, 'ladder': 128, 'brick': 64, 'dragon_egg': 128 * 3},
        'mapping': {'stone': 0, 'diamond': 1, 'glass': 2, 'ladder': 3, 'brick': 4, 'dragon_egg': 5},
        'rmapping': {0: 'stone', 1: 'diamond', 2: 'glass', 3: 'ladder', 4: 'brick', 5: 'dragon_egg'},
        'chestNum': 10,
        'max_per_chest': 3,
        'requester': Requester(None, None, None, req_path),

        '_display': True,
        '_print_logs': True,
        '_sleep_interval': .5,
        '_stochasticFailure': stochastic_array
    }
    # todo load librarian from lib_path + maybe chest distribution? Up to Kelson
