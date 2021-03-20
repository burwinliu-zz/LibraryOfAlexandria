import os
import json
import matplotlib.pyplot as plt

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    # Source file
    toConstruct = "Store\\Store\\logs1\\stepData.json"
    # Dest File
    resultPath = "moving_steps.png"

    pathToConst = os.path.join(script_dir, toConstruct)
    totalCur = 0
    toSave = []

    with open(pathToConst) as f:
        data = json.load(f)
        for _, j in data.items():
            totalCur += j
            toSave.append(totalCur/(len(toSave) + 1))
    plt.title('Moving Average of Steps (Actions Taken)')
    plt.ylabel('Actions')
    plt.xlabel('Step')
    plt.plot(toSave)
    plt.savefig(f".\\{resultPath}")