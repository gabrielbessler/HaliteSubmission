# HaliteSubmission

Halite is a challange hosted by Two-Sigma at halite.io. The goal is develop an AI that will face off
against other players in the game. Your ranking is determined by how well you do against other players. 

## Halite 2

Highest Rank: 16.7% (970 / 5832)

## Halite 3:

Highest Rating: 67.83 
Team Placement: 6.86% (238 / 3467)

### Strategy

Halite3-Old contains my original implementation that essentially uses BFS to find tiles of interest for each bot.
Note that the implementation of Halite3-Team essentially directly off of this implementation and uses many of the same ideas.
This implementation achieves a rating of ~63. 

Halite3-Team contains the new implementation.

### Hyperparameter Optimization

Many of the AI models developed contained a series of hyperparameters. For example, an A-star algorithm might 
have a heuristic function that contains a hyperparameter. While choosing parameters manually an yield 
decent results, I created a script to search for optimal parameters using a genetic algorithm. 

To run the algorithm, create one python file for the bot you would like to optimize (--bot-one), and one for the for 
the baseline bot that the new bot will be optimize against (--bot-two). Hyperparameters will be passed into the python 
file through sys.argv (the bot must then use these parameters for the optimization to work). 

```
python3 abTesting.py [--parameters=[a, b, c, ...]] 
		     [--bot-one="botName.py"]
		     [--bot-two="botName.py"]
```



