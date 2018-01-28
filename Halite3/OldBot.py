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

# Can't use STDOUT - use logging
import logging

# This game object contains the initial game state.
game = hlt.Game()

# Do computationally expensive start-up pre-processing here
class Utils(object): 
    def __init__(self): 
        self.tiles_visited = [] 
        self.commands = []
        self.me = None 
        self.game_map = None

    def checkShipSpawn(self, game): 
        # If the game is in the first 100 turns and you have enough halite, spawn a ship
        # Prevent ships from colliding on spawn
        if game.turn_number <= 150 and self.me.halite_amount >= constants.SHIP_COST and not self.game_map[me.shipyard].is_occupied:
            if self.game_map[self.me.shipyard].position not in self.tiles_visited:
                self.commands.append(me.shipyard.spawn())

    def update_game(self, me, game_map): 
        self.me = me 
        self.game_map = game_map 

        self.commands = []
        self.tiles_visited = []

    def get_valid_position(self, vertex): 
        directions = Direction.get_all_cardinals()
        shuffle(directions) 
        possible_positions = [vertex.directional_offset(direction) for direction in directions]
        for index, position in enumerate(possible_positions):
            if position not in utils.tiles_visited:
                return directions[index]

    def add_move_to_queue(self, ship, direction):
        self.commands.append(ship.move(direction))
        self.tiles_visited += [ship.position.directional_offset(direction)]

    def add_stationary_to_queue(self, ship): 
        self.commands.append(ship.stay_still())
        self.tiles_visited += [ship.position]

    def get_closest_dropoff(self, ship): 
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
        # Check for ships that cannot move 
        ships_fixed = []
        for ship in self.me.get_ships(): 
            if ship.halite_amount < game_map[ship.position].halite_amount / 10: 
                self.add_stationary_to_queue(ship)
                ships_fixed.append(ship)

        return ships_fixed

    def navigate(self, ship, destination): 
        direction = self.game_map.naive_navigate(ship, drop_off_destination)
        next_position = ship.position.directional_offset(direction) 
        # Make sure we don't crash into another ship 
        if next_position not in utils.tiles_visited:
            utils.add_move_to_queue(ship, direction)
        elif ship.position not in utils.tiles_visited:
            utils.add_stationary_to_queue(ship)
        else: 
            utils.add_move_to_queue(ship, utils.get_valid_position(ship.position))

utils = Utils()
DROPOFF_THRESHOLD = constants.MAX_HALITE * 0.8
MAX_STEPS_AHEAD = 27
MIN_STEPS_AHEAD = 17
game.ready("Steve v.8")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))
            
""" <<<Game Loop>>> """

while True: 
    game.update_frame() 
    me = game.me 
    game_map = game.game_map 
    utils.update_game(game.me, game_map)
    dropOffs = me.get_dropoffs()
    utils.tiles_visited = [] 

    ships_fixed = utils.check_stuck_ships() 
    for ship in me.get_ships(): 
        if ship in ships_fixed:
            continue 
    
        # If the ship is full, return to the drop-off zone 
        # If the game is almost over, drop off the rest of our resources 
        #   - When to drop off resources depends on how far ship is 
        drop_off_destination, drop_off_distance = utils.get_closest_dropoff(ship)
        if ship.halite_amount > DROPOFF_THRESHOLD or (constants.MAX_TURNS - game.turn_number < drop_off_distance + 10 and ship.halite_amount > 0): 
            utils.navigate(ship, drop_off_destination)

        # If there is not a lot of Halite at the current position go in random (valid) direction
        # Or if another ship is moving to this position 
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 100 or game_map[ship.position].position in utils.tiles_visited:
            
            # Check if we can move 
            if ship.halite_amount < (game_map[ship.position].halite_amount / 10):
                add_stationary_to_queue(ship)
                utils.add_stationary_to_queue(ship)
            else: 
                foundDirection = False 
                steps_ahead = 0

                visited = [] # Stores all of the vertices we have already looked at 
                queue = [[ship.position, [], 0]] # Each element is [position, path, cost]
                max_score = 0
                while (not foundDirection and steps_ahead < MAX_STEPS_AHEAD) or (steps_ahead < MIN_STEPS_AHEAD):        
                    vertex, path, cost = queue.pop(0)

                    # Check if this vertex is a good destinatiom
                    resources = game_map[vertex].halite_amount
                    if cost < resources and len(path) != 0 and ship.position.directional_offset(path[0]) not in utils.tiles_visited:
                            score = (resources - cost) / steps_ahead
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
                        if position not in visited: 
                            visited.append(position)
                            L = [position, path + [directions[index]], cost + (.1 * resources)] 
                            queue.append(L)

                    steps_ahead += 1
                    
                if foundDirection is False: 
                    if ship.position == me.shipyard.position or ship.position in utils.tiles_visited:
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
