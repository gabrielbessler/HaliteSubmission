#!/bin/sh
for ((i=1; i <= 50; ++i)) 
do 	
	echo $i / 50 
	./halite --replay-directory replays/ -vvv --width 32 --height 32 "python3 MyBot.py" "python3 OldBot.py" &>> output.txt 
done
echo "Player 0 Wins: "
grep "Player 0" output.txt | grep -o "rank 1" | wc -l 
echo "Player 1 Wins: " 
grep "Player 1" output.txt | grep -o "rank 1" | wc -l 
rm output.txt
