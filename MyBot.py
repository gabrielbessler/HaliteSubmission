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
game = hlt.Game("Gabeb v.5")
# Then we print our start message to the logs
logging.info("Starting my bot!")

unowned_planets = []

while True:
    planets_queued = []
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

        nearest_allied_planet = []
        nearest_allied_dockable = []
        target_found = False

        # For each non-destroyed planet
        for planet in d:
            # If the planet is owned
            if planet.is_owned():

                if nearest_allied_planet == []:
                    nearest_allied_planet = planet
                if nearest_allied_dockable == [] and not planet.is_full():
                    nearest_allied_dockable = planet

                # Skip this planet IF there are other planets to go to
                if len(unowned_planets) != 0:
                    continue
                else:
                    # all planets have been taken, then go to the nearest
                    #  dockable planet
                    logging.info(f"Endgame Stage - nearest dockable is {nearest_allied_dockable}")
                    if nearest_allied_dockable != []:
                        if ship.can_dock(nearest_allied_dockable):
                            command_queue.append(ship.dock(nearest_allied_dockable))
                            break
                        else:
                            navigate_command = ship.navigate(
                                    ship.closest_point_to(nearest_allied_dockable),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=False)
                            if navigate_command:
                                planets_queued.append(nearest_allied_dockable)
                                command_queue.append(navigate_command)
                            break

            # If we can dock, let's try to dock. If two ships try to dock at
            #  once, neither will be able to.
            if ship.can_dock(planet):
                # We add the command by appending it to the command_queue
                command_queue.append(ship.dock(planet))
                target_found = True
                break
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
                        target_found = True
                        planets_queued.append(planet)
                        command_queue.append(navigate_command)
                        break

        # there are planets left but all are already targetted
        if len(unowned_planets) != 0 and not target_found:
            #  just help our nearest allied planet
            if nearest_allied_planet != []:
                if ship.can_dock(nearest_allied_planet):
                    command_queue.append(ship.dock(nearest_allied_planet))
                else:
                    navigate_command = ship.navigate(
                                ship.closest_point_to(nearest_allied_planet),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)
                    if navigate_command:
                        planets_queued.append(nearest_allied_planet)
                        command_queue.append(navigate_command)

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
