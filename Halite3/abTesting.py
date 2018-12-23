from multiprocessing.pool import ThreadPool 
from multiprocessing import Value, Lock, Array 
import subprocess
import time 
import sys 
import random 
import json
import os 

class CompareBots():
    def __init__(self, shipOne, shipTwo, initialParameters, geneticAlgo=True): 
        self.shipOne = shipOne
        self.shipTwo = shipTwo
        self.initialParameters = initialParameters
        self.geneticAlgo = geneticAlgo

    def runGame(self, info):
        if self.geneticAlgo:  
            parameters = info[4] 
            s = " ".join(map(str, parameters))
            botOne = f"\"python3 {self.shipOne} {s}\""
        else: 
            botOne = f"\"python3 {self.shipOne}\""
        
        args = "-vvv --no-logs --results-as-json --width 32 --height 32"
        
        botTwo = f"\"python3 {self.shipTwo}\""

        with subprocess.Popen(f"./halite {args} {botOne} {botTwo}", shell=True, stdout=subprocess.PIPE) as proc: 
            results = json.loads(proc.stdout.read())
            print("Done!")
            # print(results)
            if results["stats"]["0"]["rank"] == 1: 
                with info[1]: 
                    info[0].value += 1
            
            # Array is stored in info[2]
            if self.geneticAlgo:
                if results["stats"]["1"]["score"] == 0:
                    pass # TODO
                else: 
                    info[2][info[3]] = results["stats"]["0"]["score"] / results["stats"]["1"]["score"] 
            
    def perturb_parameters(self, parameters): 
        return  [random.uniform(.9, 1.1) * x for x in parameters] 

    def median(self, L): 
        L = sorted(L)
        return L[len(L) // 2]

    def run(self):          
        bots_per_generation = 4
        num_generations = 1
        games_per_bot = 5
        print("Starting...")

        count = 0 
        pool = ThreadPool()
        lock = Lock()

        array = Array("f", [0]*bots_per_generation)
        val = Value("i", 0)

        if self.geneticAlgo: 
            best_parameters = self.initialParameters

        for i in range(num_generations):
            print(f"Generation {i}.")
            scores = [[] for _ in range(bots_per_generation)]
            for j in range(games_per_bot): 
                if self.geneticAlgo: 
                    parameters = [self.perturb_parameters(best_parameters) for i in range(bots_per_generation)]
                    pool.map(self.runGame, [(val, lock, array, i, parameters[i]) for i in range(bots_per_generation)])
                    
                    for index, score in enumerate(array[:]): 
                        scores[index].append(score)
                    print(scores)
                else: 
                    pool.map(self.runGame, [(val, lock) for i in range(bots_per_generation)])

            # Take median of 5 games as the actual score  
            scores = list(map(self.median, scores))
            print(scores) 

            best_parameters = parameters[scores.index(max(scores))]
            print(best_parameters)

        print(f"Player Zero Wins: {val.value}")
        print(f"Player One Wins: {num_generations * bots_per_generation * games_per_bot - val.value}")
        
def startsWith(string, beginning): 
    if len(beginning) > len(string):
        return False 

    for i in range(len(beginning)): 
        if string[i] is not beginning[i]:
            return False 
    
    return True 

if __name__ == "__main__":
    parameters = {
            "--bot-one": "MyBot.py", # bot to optimize
            "--bot-two": "MyBot.py", # bot to compare the first bot to 
            "--parameters": [800, 20, 165] # initial parameters for bot 
            }
    
    foundError = False 
    for index, arg in enumerate(sys.argv[1:]):
        foundParameter = False 
        for parameterName in parameters.keys(): 
	    # Check for parameter name match 
            if startsWith(arg, parameterName) and len(arg) >= len(parameterName) + 2:
                foundParameter = True  
                if arg[len(parameterName)] is "=":
                    result = arg[len(parameterName) + 1:]
                    if parameterName is "--parameters":
                        parameters[parameterName] = list(map(int, result.split(",")))
                    else: 
                        parameters[parameterName] = result 
                else: 
                    print("Paremeters are incorrectly formatted")
                    foundError = True
                    break 
        if not foundParameter: 
            print("Parameter " + arg + " not found")
            break 

    # Check that the bots exist 
    if not os.path.isfile(parameters["--bot-one"]):  
        print("Could not find " + parameters["--bot-one"])
    elif not os.path.isfile(parameters["--bot-two"]):
        print("Could not find " + parameters["--bot-two"])
    elif not foundError: 
        compare = CompareBots(parameters["--bot-one"], parameters["--bot-two"], parameters["--parameters"], True) 
        compare.run()

