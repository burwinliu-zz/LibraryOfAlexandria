import os
import json
import matplotlib.pyplot as plt

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    # Source file
    toConstruct = "Store\\Store\\case3\\returnsfinalpart.json"
    # Dest File
    resultPath = "result.png"

    pathToConst = os.path.join(script_dir, toConstruct)
    totalCur = 0
    toSave = []

    with open(pathToConst) as f:
        data = json.load(f)
        for _, j in data.items():
            totalCur += j
            toSave.append(totalCur/(len(toSave) + 1))
    plt.title('Moving Average')
    plt.ylabel('Reward')
    plt.xlabel('Step')
    plt.plot(toSave)
    plt.savefig(f".\\{resultPath}")