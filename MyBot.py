"""
1. Initialize game
2. If a ship is not docked and there are unowned planets
    2.a. Try to Dock in the planet if close enough
    2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to
communicate with the Halite engine. If you need
to log anything use the logging module.
"""
import hlt
import logging

# GAME START
# Here we define the bot's name as Settler and initialize the game,
#  including communication with the Halite engine.
game = hlt.Game("Gabeb v.3")
# Then we print our start message to the logs
logging.info("Starting my bot!")

planets_queued = []
unowned_planets = []

while True:
    # Update the map for the new turn
    game_map = game.update_map()

    # Get a list of all the planets that are not owned
    unowned_planets = [planet for planet in game_map.all_planets()
                       if not planet.is_owned()]

    # Here we define the set of commands to be sent
    command_queue = []

    # Loop through all owned ships
    me = game_map.my_id
    my_ships = game_map.get_me().all_ships()

    '''
    s = f"num ships: {len(my_ships)}"
    logging.info(s)
    '''

    for ship in my_ships:

        # If ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        # get dictionary of all entities with distances
        d = game_map.nearby_entities_by_distance(ship)

        # now, we want to turn this into a list of tuples,
        # sorted by the distances
        d = sorted(d.items(), key=lambda x: x[0])

        # now, filter out everything that isn't a planet
        d = [e[1][0] for e in d if isinstance(e[1][0], hlt.entity.Planet)]

        # For each non-destroyed planet
        for planet in d:
            # If the planet is owned
            if planet.is_owned():
                # Skip this planet IF there are other planets to go to
                if len(unowned_planets) != 0:
                    continue
                else:
                    # all planets have been taken
                    if ship.can_dock(planet):
                        # if we can dock at the planet, dock
                        command_queue.append(ship.dock(planet))
                        break
                    else:
                        continue
                        # TODO: ADD THIS IN
                        if planet.owner.id != me:
                            # Attack other planets
                            navigate_command = ship.navigate(planet,
                                                             game_map,
                                                             speed=int(hlt.constants.MAX_SPEED),
                                                             ignore_ships=False)
                            command_queue.append(navigate_command)
                            break

            ''' We do not own the planet '''

            # If we can dock, let's try to dock. If two ships try to dock at
            #  once, neither will be able to.
            if ship.can_dock(planet):
                # We add the command by appending it to the command_queue
                command_queue.append(ship.dock(planet))
            else:
                # If one of our ships is already going to this planet
                if planet in planets_queued:
                    # skip the planet
                    continue
                else:
                    # go to the planet
                    navigate_command = ship.navigate(
                        ship.closest_point_to(planet),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False)
                    if navigate_command:
                        planets_queued.append(planet)
                        command_queue.append(navigate_command)
            break

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
