import os
import json
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Create moving average graphs  
    script_dir = os.path.dirname(__file__)
    # Source file
    # toConstruct = "Store\\Store\\logs1\\stepData.json"
    # toConstruct = "Store\\Store\\logs1\\returnsfinalpart.json"
    toConstruct = "Store\\Store\\logs1\\failureData.json"
    # Dest File
    resultPath = "moving_steps.png"

    pathToConst = os.path.join(script_dir, toConstruct)

    with open(pathToConst) as f:
        data = [j for _, j in sorted(json.load(f).items())]
        print(f"Mean of last 100 is {sum(data[-500:])/500}")
        print(f"Max of last 100 is {max(data[-500:])}")
        print(f"Min of last 100 is {min(data[-500:])}")

    # totalCur = 0
    # toSave = []

    # with open(pathToConst) as f:
    #     data = json.load(f)
    #     for _, j in data.items():
    #         totalCur += j
    #         toSave.append(totalCur/(len(toSave) + 1))
    # plt.title('Moving Average of Steps (Actions Taken)')
    # plt.ylabel('Actions')
    # plt.xlabel('Step')
    # plt.plot(toSave)
    # plt.savefig(f".\\{resultPath}")