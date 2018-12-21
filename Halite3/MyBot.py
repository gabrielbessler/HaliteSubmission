#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

import random
from random import shuffle
import collections  
from collections import defaultdict 

# Can't use STDOUT - use logging
import logging

# This game object contains the initial game state.
game = hlt.Game()

# Do computationally expensive start-up pre-processing here
class Utils(object): 
    def __init__(self, DROPOFF_THRESHOLD=constants.MAX_HALITE * 0.8, MIN_HALITE=20, STOP_SPAWNING=165): 
        '''
        '''
        self.tiles_visited = set() 
        self.commands = []
        self.targets = defaultdict(list) 
        self.me = None 
        self.game_map = None
        self.DROPOFF_THRESHOLD = DROPOFF_THRESHOLD
        self.MIN_HALITE = MIN_HALITE
        self.STOP_SPAWNING = STOP_SPAWNING

    def tup(self, pos): 
        '''
        '''
        pos = self.game_map.normalize(pos)
        return pos.x, pos.y

    def detup(self, tup): 
        '''
        '''
        return Position(*tup) 

    def checkShipSpawn(self, game): 
        '''
        '''
        # If the game is in the first 100 turns and you have enough halite, spawn a ship
        # Prevent ships from colliding on spawn
        if game.turn_number <= self.STOP_SPAWNING and self.me.halite_amount >= constants.SHIP_COST and not self.game_map[me.shipyard].is_occupied:
            if self.tup(self.game_map[self.me.shipyard].position) not in self.tiles_visited:
                self.commands.append(me.shipyard.spawn())

    def update_game(self, me, game_map): 
        '''
        '''
        self.me = me 
        self.game_map = game_map 

        self.commands = []
        self.tiles_visited = set()

    def get_valid_position(self, vertex): 
        '''
        '''
        directions = Direction.get_all_cardinals()
        shuffle(directions) 
        possible_positions = [vertex.directional_offset(direction) for direction in directions]
        for index, position in enumerate(possible_positions):
            if self.tup(position) not in utils.tiles_visited:
                return directions[index]

    def add_move_to_queue(self, ship, direction):
        '''
        '''
        self.commands.append(ship.move(direction))
        self.tiles_visited.add(self.tup(ship.position.directional_offset(direction)))

    def add_stationary_to_queue(self, ship): 
        '''
        '''
        self.commands.append(ship.stay_still())
        self.tiles_visited.add(self.tup(ship.position))

    def get_closest_dropoff(self, ship): 
        '''
        '''
        dropOffDistance = self.game_map.calculate_distance(self.me.shipyard.position, ship.position)
        dropOffIndex = -1
        for i in range(len(dropOffs)):
            dropOff = dropOffs[i]
            dist = self.game_map.calculate_distance(dropOff.position, ship.position)
            if dist < dropOffDistance: 
                dropOffDistance = dist 
                dropOffIndex = i

        if dropOffIndex > -1: 
            destination = self.me.get_dropoffs()[dropOffIndex]
        else:
            destination = self.me.shipyard.position
        
        return destination, dropOffDistance

    def check_stuck_ships(self): 
        '''
        '''
        # Check for ships that cannot move 
        ships_fixed = []
        for ship in self.me.get_ships(): 
            if ship.halite_amount < game_map[ship.position].halite_amount / 10: 
                self.add_stationary_to_queue(ship)
                ships_fixed.append(ship)

        return ships_fixed

    def navigate(self, ship, destination, ignoreCollision = False): 
        '''
        '''

        directions = self.game_map.get_unsafe_moves(ship.position, drop_off_destination)

        direction = directions[0]
        
        next_position = ship.position.directional_offset(direction) 
        
        # Make sure we don't crash into another ship 
        if self.tup(next_position) not in utils.tiles_visited or ignoreCollision:
            utils.add_move_to_queue(ship, direction)
        elif len(directions) == 2 and self.tup(ship.position.directional_offset(directions[1])) not in utils.tiles_visited: 
            utils.add_move_to_queue(ship, directions[1])
        elif self.tup(ship.position) not in utils.tiles_visited:
            utils.add_stationary_to_queue(ship)
        else: 
            direction = utils.get_valid_position(ship.position) 
            if direction is not None: 
                utils.add_move_to_queue(ship, direction)
            else: 
                utils.add_stationary_to_queue(ship)
    
    def A_star(self, start, goal): 
        '''
        '''

        # Set of notes we have evaluated 
        nodesVisited = set() 

        # Set of currently discovered nodes that are not evaluated yet 
        nodesDiscovered = set()
        nodesDiscovered.add(start) 

        # For each node, the node it can most efficiently be reached from 
        cameFrom = {}

        # Cost of going from start to that node 
        gScore = {} 
        gScore[start] = 0

    def check_target(self, ship): 
        '''
        '''
        if self.targets[ship.id] is None: 
            return False  
        self.navigate(ship, self.targets[ship.id])
        return True 

utils = Utils()
MAX_STEPS_AHEAD = 60
MIN_STEPS_AHEAD = 60
game.ready("Steve v.1.0.4")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can alys fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))
            
""" <<<Game Loop>>> """

while True: 
    game.update_frame() 
    me = game.me 
    game_map = game.game_map 
    utils.update_game(game.me, game_map)
    dropOffs = me.get_dropoffs()
    turns_left = constants.MAX_TURNS - game.turn_number

    ships_fixed = utils.check_stuck_ships() 
    for ship in me.get_ships(): 
        if ship in ships_fixed:
            continue 
        
        if utils.check_target(ship):
            continue
    
        # If the ship is full, return to the drop-off zone 
        # If the game is almost over, drop off the rest of our resources 
        #   - When to drop off resources depends on how far ship is 
        drop_off_destination, drop_off_distance = utils.get_closest_dropoff(ship)
        if ship.halite_amount > utils.DROPOFF_THRESHOLD: 
            if drop_off_distance == 1 and turns_left < 5: 
                utils.navigate(ship, drop_off_destination, True) 
            else: 
                utils.navigate(ship, drop_off_destination, False)  

        elif (turns_left < (drop_off_distance + 5)) and ship.position != drop_off_destination: 
            if drop_off_distance == 1: 
                utils.navigate(ship, drop_off_destination, True) 
            else: 
                utils.navigate(ship, drop_off_destination, False)    

        # If at the end of the game, make all of the ships crash at the drop-off point
        elif ship.position == drop_off_destination and ((constants.MAX_TURNS - game.turn_number) < 10): 
            utils.add_stationary_to_queue(ship)

        # If there is not a lot of Halite at the current position go in random (valid) direction
        # Or if another ship is moving to this position 
        elif game_map[ship.position].halite_amount < utils.MIN_HALITE or utils.tup(game_map[ship.position].position) in utils.tiles_visited:
            
            # Check if we can move 
            if ship.halite_amount < (game_map[ship.position].halite_amount / 10):
                add_stationary_to_queue(ship)
                utils.add_stationary_to_queue(ship)
            else: 
                foundDirection = False 
                steps_ahead = 0

                visited = set() # Stores all of the vertices we have already looked at 
                queue = [[ship.position, [], 0]] # Each element is [position, path, cost]
                max_score = 0
                while (not foundDirection and steps_ahead < MAX_STEPS_AHEAD) or (steps_ahead < MIN_STEPS_AHEAD):        
                    vertex, path, cost = queue.pop(0)

                    # Check if this vertex is a good destinatiom
                    resources = game_map[vertex].halite_amount
                    if cost < resources and len(path) != 0 and utils.tup(ship.position.directional_offset(path[0])) not in utils.tiles_visited:
                        score = (resources - cost)**2.5 / steps_ahead
                        if score > max_score: 
                            max_score = score
                            directionToMove = path[0]
                            foundDirection = True 
                    
                    # Get all tiles you can access from it 
                    directions = Direction.get_all_cardinals()
                    random.shuffle(directions)
                    possible_positions = [vertex.directional_offset(direction) for direction in directions]

                    # For each tile, check if we have already visited it. If not, add to the queue 
                    for index, position in enumerate(possible_positions): 
                        pos = utils.tup(position)
                        if pos not in visited: 
                            visited.add(pos)
                            L = [position, path + [directions[index]], cost + (.1 * resources)] 
                            queue.append(L)

                    steps_ahead += 1
                    
                if foundDirection is False: 
                    if ship.position == me.shipyard.position or utils.tup(ship.position) in utils.tiles_visited:
                        direction = utils.get_valid_position(ship.position)
                        if direction is None: 
                            utils.add_stationary_to_queue(ship)
                        else: 
                            utils.add_move_to_queue(ship, direction)
                    else:
                        utils.add_stationary_to_queue(ship)
                else:
                    utils.add_move_to_queue(ship, directionToMove)
        else:
            utils.add_stationary_to_queue(ship)
            
    utils.checkShipSpawn(game) 

    game.end_turn(utils.commands)