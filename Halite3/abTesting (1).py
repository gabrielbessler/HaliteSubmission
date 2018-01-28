from multiprocessing.pool import ThreadPool 
from multiprocessing import Value, Lock 
import subprocess
import time 

shipOne = "MyBot.py"
shipTwo = "MyBot.py"
threads = 3
num_games = 9
bot_name_length = 9
print("Starting...")

def runGame(info): 
    with subprocess.Popen(f"./halite -vvv --width 32 --height 32 \"python3 {shipOne}\" \"python3 {shipTwo}\"", shell=True, stderr=subprocess.PIPE) as proc: 
        result = str(proc.stderr.read())
        index = result.index("rank 1")
        if "Player 1" in result[index-18-bot_name_length:index+6]: 
            with info[1]: 
                info[0].value += 1

with open("comparisons/output.txt", "a") as outfile:
    count = 0 
    pool = ThreadPool()
    lock = Lock()
    val = Value("i", 0)
    for i in range(int(num_games / threads)):
        print(f"Generation {count}.")
        count += 1
        pool.map(runGame, [(val, lock) for i in range(threads)])
    
print(f"Player One Wins: {val.value}")
print(f"Player Two Wins: {num_games - val.value}")