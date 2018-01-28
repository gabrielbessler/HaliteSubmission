from multiprocessing.pool import ThreadPool 
from multiprocessing import Value, Lock 
import subprocess
import time 
import sys 

class CompareBots():
    def __init__(self, shipOne, shipTwo, botNameLength): 
        self.shipOne = shipOne
        self.shipTwo = shipTwo
        self.bot_name_length = botNameLength

    def runGame(self, info): 
        with subprocess.Popen(f"./halite -vvv --width 32 --height 32 \"python3 {self.shipOne}\" \"python3 {self.shipTwo}\"", shell=True, stderr=subprocess.PIPE) as proc: 
            result = str(proc.stderr.read())
            index = result.index("rank 1")
            if "Player 1" in result[index-18-self.bot_name_length:index+6]: 
                with info[1]: 
                    info[0].value += 1

    def run(self):         
        threads = 3
        num_games = 9
        print("Starting...")

        with open("comparisons/output.txt", "a") as outfile:
            count = 0 
            pool = ThreadPool()
            lock = Lock()
            val = Value("i", 0)
            for i in range(int(num_games / threads)):
                print(f"Generation {count}.")
                count += 1
                pool.map(self.runGame, [(val, lock) for i in range(threads)])
            
        print(f"Player One Wins: {val.value}")
        print(f"Player Two Wins: {num_games - val.value}")

if __name__ == "__main__":
    botOne = "MyBot.py"
    botTwo = "OldBot.py"
    length = 9
    for index, arg in enumerate(sys.argv[1:]):
        if index == 0:
            botOne = arg
        if index == 1: 
            botTwo = arg
        if index == 2: 
            length = arg
    compare = CompareBots(botOne, botTwo, length) 
    compare.run()
    