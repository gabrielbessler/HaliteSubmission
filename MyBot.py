import hlt
import logging
import time

game = hlt.Game("Gabeb v.6")
count = 0
MAX_SPEED = int(hlt.constants.MAX_SPEED)


def is_docked(ship):
    if ship.docking_status != ship.DockingStatus.UNDOCKED:
        return True


def get_closest_entities(game_map, ship):
    # get dictionary of all entities with distances
    d = game_map.nearby_entities_by_distance(ship)
    # now, we want to turn this into a list of tuples,
    # sorted by the distances
    d = sorted(d.items(), key=lambda x: x[0])
    # now, filter out everything that isn't a planet
    planets = [e[1][0] for e in d if isinstance(e[1][0], hlt.entity.Planet)]
    ships = [e[1][0] for e in d if isinstance(e[1][0], hlt.entity.Ship)]
    return planets, ships


def get_closest_enemy(game_map, enemies):
    # get dictionary of all entities with distances
    for e in enemies:
        if game_map.my_id != e.owner.id:
            return e

while True:
    s_time = time.time()
    count += 1
    # logging.info(f"Turn: {count}")
    game_map = game.update_map()

    # List of planets that we will be going to
    planets_queued = []
    # Define the set of commands to be sent
    command_queue = []
    # Get a list of all the planets that are not owned
    unowned_planets = [planet for planet in game_map.all_planets()
                       if not planet.is_owned()]

    planet_targetted = {p: 0 for p in game_map.all_planets()}

    # Loop through owned ships
    for ship in game_map.get_me().all_ships():

        # if len(unowned_planets) == 0:
            # logging.info("New Ship - Phase 2")
        # else:
            # logging.info("New Ship - Phase 1")

        if is_docked(ship):
            continue

        planets, enemies = get_closest_entities(game_map, ship)
        nearest_allied_planet = []
        target_found = False

        # For each non-destroyed planet
        for planet in planets:
            # If the planet is owned
            if planet.is_owned():

                if nearest_allied_planet == []:
                    nearest_allied_planet = planet

                # Skip this planet IF there are other planets to go to
                if len(unowned_planets) != 0:
                    continue
                else:
                    # all planets have been taken, then go to the nearest
                    #  dockable planet
                    planned_docking = len(planet._docked_ship_ids) + planet_targetted[planet]
                    if planned_docking < planet.num_docking_spots:
                        target_found = True
                        if ship.can_dock(planet):
                            command_queue.append(ship.dock(planet))
                            break
                        else:
                            navigate_command = ship.navigate(
                                    ship.closest_point_to(planet),
                                    game_map,
                                    speed=MAX_SPEED,
                                    ignore_ships=False)
                            if navigate_command:
                                planets_queued.append(planet)
                                command_queue.append(navigate_command)
                                # planet_targetted[planet] += 1 TODO
                            break
                    else:
                        if (time.time() - s_time) < .5:
                            nearest_enemy = get_closest_enemy(game_map, enemies)
                            # logging.info(f"nearest_enemy: {nearest_enemy}")
                            navigate_command = ship.navigate(nearest_enemy, game_map, speed=MAX_SPEED)
                            if navigate_command:
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
                        speed=MAX_SPEED,
                        ignore_ships=False)
                    if navigate_command:
                        target_found = True
                        planets_queued.append(planet)
                        command_queue.append(navigate_command)
                        # planet_targetted[planet] += 1 TODO
                        break

        # logging.info(f"target_found: {target_found}")

        # there are planets left but all are already targetted
        if len(unowned_planets) != 0 and not target_found:
            #  just help our nearest allied planet
            if nearest_allied_planet != []:
                if ship.can_dock(nearest_allied_planet):
                    command_queue.append(ship.dock(nearest_allied_planet))
                else:
                    navigate_command = ship.navigate(
                                ship.closest_point_to(nearest_allied_planet),
                                game_map, speed=MAX_SPEED,
                                ignore_ships=False)
                    if navigate_command:
                        planets_queued.append(nearest_allied_planet)
                        command_queue.append(navigate_command)
                        # planet_targetted[planet] += 1 TODO
    logging.info(f"time: {time.time() - s_time}")
    game.send_command_queue(command_queue)
