#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction, Position

import random
from random import shuffle
import collections  

# Can't use STDOUT - use logging
import logging
import sys 
import math 

# This game object contains the initial game state.
game = hlt.Game()

# Do computationally expensive start-up pre-processing here
class Utils(object): 
    def __init__(self, DROPOFF_THRESHOLD=constants.MAX_HALITE * 0.82, MIN_HALITE=17, STOP_SPAWNING=180): 
        self.tiles_visited = set() 
        self.targets = dict()
        self.commands = []
        self.me = None 
        self.game_map = None
        self.DROPOFF_THRESHOLD = DROPOFF_THRESHOLD
        self.MIN_HALITE = MIN_HALITE
        self.STOP_SPAWNING = STOP_SPAWNING
        self.MIN_SHIPS = 15
        self.MIN_RESOURCES_FOR_SHIP = 10000

    def tup(self, pos): 
        pos = self.game_map.normalize(pos)
        return pos.x, pos.y

    def detup(self, tup): 
        return Position(*tup) 

    def get_total_resources(self): 
        total = 0
        for cell_index in range(len(self.game_map._cells)):
            for cell_index_two in range(len(self.game_map._cells[0])):
                total += self.game_map._cells[cell_index][cell_index_two].halite_amount
        return total

    def checkShipSpawn(self, game): 
        # If the game is in the first 100 turns and you have enough halite, spawn a ship
        # Prevent ships from colliding on spawn
        if game.turn_number <= self.STOP_SPAWNING and self.me.halite_amount >= constants.SHIP_COST and not self.game_map[me.shipyard].is_occupied:
            if self.tup(self.game_map[self.me.shipyard].position) not in self.tiles_visited:
                self.commands.append(me.shipyard.spawn())

        # If ships are below a certain threshold due to collisions, spawn more ships 
        # if game.turn_number > self.STOP_SPAWNING and len(self.me.get_ships()) < self.MIN_SHIPS:
        #     if self.get_total_resources() > self.MIN_RESOURCES_FOR_SHIP: 
        #         if self.tup(self.game_map[self.me.shipyard].position) not in self.tiles_visited: 
        #             self.commands.append(me.shipyard.spawn())

    def update_game(self, me, game_map): 
        self.me = me 
        self.game_map = game_map 

        self.commands = []
        self.tiles_visited = set()

    def get_valid_position(self, vertex): 
        directions = Direction.get_all_cardinals()
        shuffle(directions) 
        possible_positions = [vertex.directional_offset(direction) for direction in directions]
        for index, position in enumerate(possible_positions):
            if self.tup(position) not in utils.tiles_visited:
                return directions[index]

    def add_move_to_queue(self, ship, direction):
        self.commands.append(ship.move(direction))
        self.tiles_visited.add(self.tup(ship.position.directional_offset(direction)))

    def add_stationary_to_queue(self, ship): 
        self.commands.append(ship.stay_still())
        self.tiles_visited.add(self.tup(ship.position))

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
        ships_fixed = set()
        for ship in self.me.get_ships(): 
            if ship.halite_amount < game_map[ship.position].halite_amount / 10: 
                self.add_stationary_to_queue(ship)
                ships_fixed.add(ship.id)

        return ships_fixed

    def navigate(self, ship, destination, ignoreCollision = False): 
        directions = self.game_map.get_unsafe_moves(ship.position, drop_off_destination)

        if len(directions) != 0: 
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
        else: 
            # TODO - temporary
            utils.add_stationary_to_queue(ship)

    def reconstruct_path(self, cameFrom, current):
        ''' Given a ditionary 'cameFrom', and the node we're currently at, 
        works backwards to find a path to the beginning ''' 
        total_path = [current] 
        while current in cameFrom: 
            current = cameFrom[current] 
            total_path.append(current)
        return total_path 
    
    def heuristic_cost_estimate(self, start, end):
        # Calculate Manhattan distance 
        # TODO: 
        # For now, we just suppose that each tile has on average 300 resources, 
        # So it costs 30 per tile, and we do not take into account the number of turns (only the cost) 
        return 30 * self.game_map.calculate_distance(self.detup(start), self.detup(end))

    def dist_between(self, start, end): 
        ''' 
        Takes two tuples that are next to each other and returns the distance between them. 
        Since the tuples are next to each other, this is just the cost of moving off of the 
        current tile  
        ''' 
        # TODO: this does not take into account the number of turns, only the cost 
        return self.game_map[self.detup(start)].halite_amount / 10 

    def smart_navigate(self, ship, destination): 
        ''' 
        Uses A* pathing algorithm to find the "best" path from the ship 
        to the destination. 

        If progress cannot be made towards the target, the ship will stand 
        still unless it must move to prevent crashing into another ship.

        Takes a 'ship' and a 'position'
        ''' 
        start = utils.tup(ship.position)
        goal = utils.tup(destination)
        # Set of notes already evaluated 
        closedSet = set() 

        # Set of discovered notes (not evaluated) 
        openSet = set()
        openSet.add(start)
        
        # For each node, node it can most efficiently be reached from
        cameFrom = dict() 

        # Cost from start node to that node 
        gScore = dict() 
        gScore[start] = 0

        # Cost from start node to goal by passing through node - partly heuristic 
        fScore = dict()
        fScore[start] = self.heuristic_cost_estimate(start, goal)

        # While we have nodes we have not evaluated
        while len(openSet) != 0:
            # Get lowest fScore
            minValue = math.inf
            current = None
            for node in openSet:
                if fScore[node] < minValue:
                    minValue = fScore[node]
                    current = node
          
            if current == goal: 
                logging.info("arrived at goal")
                return self.reconstruct_path(cameFrom, current)
            
            openSet.remove(current)
            closedSet.add(current)

            directions = Direction.get_all_cardinals()
            possible_positions = [self.detup(current).directional_offset(direction) for direction in directions]

            # Go through neighbors of current 
            for neighbor in possible_positions:
                # Ignore neighbors we already evaluated  
                if self.tup(neighbor) in closedSet: 
                    continue 

                # Distance from start to neighbor 
                tentative_gScore = gScore[current] + self.dist_between(current, self.tup(neighbor)) 

                # Discovered a new node 
                if self.tup(neighbor) not in openSet: 
                    openSet.add(self.tup(neighbor))
                elif tentative_gScore >= gScore[self.tup(neighbor)]:
                    continue # We already had a better path 

                cameFrom[self.tup(neighbor)] = current 
                gScore[self.tup(neighbor)] = tentative_gScore
                fScore[self.tup(neighbor)] = tentative_gScore + self.heuristic_cost_estimate(self.tup(neighbor), goal)


params = list(map(float, sys.argv[1:]))
if len(params) != 0: 
    utils = Utils(*params)
else: 
    utils = Utils() 
MAX_STEPS_AHEAD = 50
MIN_STEPS_AHEAD = 50
game.ready("Steve v.1.0.5")

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

    first = True # temp 
    for ship in me.get_ships(): 
        if ship.id in ships_fixed:
            continue 

        if first: 
            utils.smart_navigate(ship, me.shipyard.position)
            first = False 

        #if ship.id in utils.targets and utils.targets[ship.id] is not None: 
        #    if ship.position == utils.targets[ship.id]: 
        #        utils.targets[ship.id] = None 
        #    else: 
        #        utils.navigate(ship, utils.targets[ship.id], False)
        #        continue 

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
                target = None 

                visited = [] # Stores all of the vertices we have already looked at 
                queue = [[ship.position, [], 0]] # Each element is [position, path, cost]
                max_score = 0
                while (not foundDirection and steps_ahead < MAX_STEPS_AHEAD) or (steps_ahead < MIN_STEPS_AHEAD):        
                    vertex, path, cost = queue.pop(0)

                    # Check if this vertex is a good destinatiom
                    resources = game_map[vertex].halite_amount
                    pos = utils.tup(game_map[vertex].position)
                    
                    # Make sure no other ship is going to that tile 
                    targetted = False 
                    for ship_id, target in utils.targets.items(): 
                        if target == pos: 
                            targetted = True 

                    if not targetted:
                        if cost < resources and len(path) != 0 and utils.tup(ship.position.directional_offset(path[0])) not in utils.tiles_visited:
                            score = (resources - cost)**2.5 / steps_ahead
                            if score > max_score: 
                                max_score = score
                                directionToMove = path[0]
                                target = pos
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
                    if ship.position == me.shipyard.position or utils.tup(ship.position) in utils.tiles_visited:
                        direction = utils.get_valid_position(ship.position)
                        if direction is None: 
                            utils.add_stationary_to_queue(ship)
                        else: 
                            utils.add_move_to_queue(ship, direction)
                    else:
                        utils.add_stationary_to_queue(ship)
                else:
                    # utils.targets[ship.id] = target 
                    utils.add_move_to_queue(ship, directionToMove)
        else:
            utils.add_stationary_to_queue(ship)
            
    utils.checkShipSpawn(game) 

    game.end_turn(utils.commands)
