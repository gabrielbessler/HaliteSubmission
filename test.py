import hlt
import logging
import time

game = hlt.Game("Gabeb v.7")


def is_docked(ship):
    if ship.docking_status != ship.DockingStatus.UNDOCKED:
        return True


def get_closest_entities(game_map, ship):
    # Get dictionary of all entities with distances
    d = game_map.nearby_planets_by_distance(ship)
    # Now, we want to turn this into a list of tuples,
    # Sorted by the distances
    d = sorted(d.items(), key=lambda x: x[0])
    planets = [e[1][0] for e in d]

    return planets


def initial_setup(game_map):
    # get the closest planets to each ship
    ships = game_map.get_me().all_ships()
    ships_1_closest = get_closest_entities(game_map, ships[0])
    ships_2_closest = get_closest_entities(game_map, ships[1])
    ships_3_closest = get_closest_entities(game_map, ships[2])

    opening_planets[ships[0].id] = ships_1_closest[0]
    opening_planets[ships[1].id] = ships_2_closest[0]
    opening_planets[ships[2].id] = ships_3_closest[0]

    # if all 3 have a single planet as the closest
    if ships_1_closest[0] == ships_2_closest[0] and ships_1_closest[0] == ships_3_closest[0]:
        # send the third one to a different planet if needed
        if ships_3_closest[0].num_docking_spots < 3:
            opening_planets[ships[2].id] = ships_3_closest[1]

count = 0
in_opener = True
opening_planets = {}

while True:
    count += 1
    s_time = time.time()
    game_map = game.update_map()

    if count == 1:
        initial_setup(game_map)

    # Define the set of commands to be sent
    command_queue = []

    ''' Opening Phase (only 3 ships) '''
    if in_opener:
        dock_count = 0
        for ship in game_map.get_me().all_ships():
            target = opening_planets[ship.id]
            if is_docked(ship):
                dock_count += 1
                continue
            elif ship.can_dock(target):
                command_queue.append(ship.dock(target))
                continue
            else:
                navigate_command = ship.navigate(
                                        ship.closest_point_to(target),
                                        game_map)
                command_queue.append(navigate_command)
        if dock_count == len(game_map.get_me().all_ships()):
            in_opener = False

        game.send_command_queue(command_queue)
        continue
    ''' End of opening phase '''

    # Store how many ships are going to each planet
    planet_targetted = {p: 0 for p in game_map.all_planets()}

    ''' Loop through all owned ships '''
    for ship in game_map.get_me().all_ships():

        ''' TIME FAILSAFE '''
        if (time.time() - s_time) >= 1.90:
            game.send_command_queue(command_queue)
            break

        if is_docked(ship):
            continue

        ''' We are not docked '''
        planets = get_closest_entities(game_map, ship)
        closest_enemy_planet = None

        ''' Loop through planets (closest->farthest) '''
        for planet in planets:
            if closest_enemy_planet is None and planet.is_owned():
                if planet.owner.id != game_map.my_id:
                    closest_enemy_planet = planet

            # If we the planet is full, ignore it
            if planet.is_full():
                continue

            ''' We are not docked and planet is not full '''

            ''' We own the planet '''
            if planet.is_owned():
                '''We Own the Planet '''
                if planet.owner.id == game_map.my_id:
                    num_slots = planet.num_docking_spots - \
                                len(planet._docked_ship_ids)

                    # If we can dock, dock
                    if ship.can_dock(planet):
                        command_queue.append(ship.dock(planet))
                        break
                    # if there are open slots, travel to it
                    elif num_slots > planet_targetted[planet]:
                        navigate_command = ship.navigate(
                                    ship.closest_point_to(planet),
                                    game_map)
                        if navigate_command:
                            planet_targetted[planet] += 1
                            command_queue.append(navigate_command)
                            break
                    else:
                        continue
                else:
                    ''' Someone else owns it '''
                    # Attack an enemy
                    enemy = planet.get_docked_ship(planet._docked_ship_ids[0])
                    navigate_command = ship.navigate(
                                enemy, game_map)
                    if navigate_command:
                        planet_targetted[planet] += 1
                        command_queue.append(navigate_command)
                        break
            else:
                ''' Nobody owns the planet '''
                # If we can dock, dock
                if ship.can_dock(planet):
                    command_queue.append(ship.dock(planet))
                    break
                else:
                    navigate_command = ship.navigate(
                                    ship.closest_point_to(planet),
                                    game_map)
                    if navigate_command:
                        planet_targetted[planet] += 1
                        command_queue.append(navigate_command)
                        break
        # if after looping through all planets we haven't found a target
        # that means all planets are full
        # TODO: make this better

        # for now, just attack enemy planets
        enemy = closest_enemy_planet.get_docked_ship(
            closest_enemy_planet._docked_ship_ids[0])
        navigate_command = ship.navigate(enemy, game_map)
        if navigate_command:
            planet_targetted[planet] += 1
            command_queue.append(navigate_command)

    game.send_command_queue(command_queue)
    continue

