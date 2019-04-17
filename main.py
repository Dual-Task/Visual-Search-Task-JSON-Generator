"""
Script to generate the visual search grids for Dual-Task studies.
@author: Pramod Kotipalli (pramodk@gatech.edu)
"""

import json
import random
import uuid

VERSION = '1.0'

CONFIG_FILE = 'config.json'

OUTPUT_FILE = 'output.json'

SEED = 42
random.seed(SEED)


def get_grid(width, height):
    """ Creates a 2D array. """
    array = [None] * width
    for i in range(width):
        array[i] = [None] * height
    return array


def get_unique_random_values(number_of_stimuli,
                             min_value, max_value,
                             numbers_to_exclude):
    """
    Generates a list of unique numbers without values in numbers_to_exclude.
    """

    values_set = set()

    while len(values_set) < number_of_stimuli:
        # Get a value to insert
        new_value = random.randint(min_value, max_value)

        # Ensure it is not excluded
        if new_value in numbers_to_exclude:
            continue

        # Add it in (duplicates don't matter to sets)
        values_set.add(new_value)

    # Shuffle the resultant list to avoid unexpected orderings
    values_list = list(values_set)
    random.shuffle(values_list)

    return values_list


def generate_random_grid(width, height,
                         number_of_stimuli,
                         min_value, max_value,
                         target_number,
                         target_number_inclusion_probability):
    """ Randomly generates a grid that conforms to the given values. """

    # Get an empty grid
    grid = get_grid(width, height)

    # Find what values to insert into it
    values_list = get_unique_random_values(
        number_of_stimuli=number_of_stimuli,
        min_value=min_value,
        max_value=max_value,
        numbers_to_exclude=[target_number],
    )

    for value_to_insert in values_list:
        # Find a location to insert the value
        while True:
            x_pos = random.randint(0, width - 1)
            y_pos = random.randint(0, height - 1)

            # Only in an empty space
            if grid[x_pos][y_pos] is None:
                grid[x_pos][y_pos] = value_to_insert
                break

    # Choose whether or not to substitute a value in the grid with the target
    should_insert_target_number = \
        random.random() < target_number_inclusion_probability

    if should_insert_target_number:
        # Find somewhere to insert it
        while True:
            x_pos = random.randint(0, width - 1)
            y_pos = random.randint(0, height - 1)

            # Fill in the target number into a non-empty cell
            if grid[x_pos][y_pos] is not None:
                grid[x_pos][y_pos] = target_number
                break

    return grid


def main():
    # Read in all the config values
    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)

    config['grid'] = config['grid']

    width = config['grid']['width']
    height = config['grid']['height']

    min_value = config['grid']['minValue']
    max_value = config['grid']['maxValue']

    target_number = config['grid']['targetNumber']
    target_number_inclusion_probability = config['grid']['targetNumberInclusionProbability']
    number_of_stimuli = config['grid']['numberOfStimuli']

    conditions = config['study']['conditions']
    number_of_grids_per_condition = config['study']['numberOfGridsPerCondition']
    sessions = config['study']['sessions']

    # Begin generating outputs
    grids = []

    # For each session (training, testing)
    for session in sessions:
        # For each condition (Visual Search, Visual Search + HUD, etc.)
        for condition in conditions:
            # For each grid
            for grid_index_in_condition in range(number_of_grids_per_condition):
                # Get a new grid
                grid = generate_random_grid(
                    width=width,
                    height=height,
                    number_of_stimuli=number_of_stimuli,
                    min_value=min_value, max_value=max_value,
                    target_number=target_number,
                    target_number_inclusion_probability=target_number_inclusion_probability,
                )

                grids.append({
                    'id': str(uuid.uuid4()),
                    'version': VERSION,
                    'session': session,
                    'condition': condition,
                    'targetNumber': target_number,
                    'width': width,
                    'height': height,
                    'minValue': min_value,
                    'maxValue': max_value,
                    'targetNumberInclusionProbability': target_number_inclusion_probability,
                    'numberOfStimuli': number_of_stimuli,
                    'gridIndexInCondition': grid_index_in_condition,
                    'numberOfGridsPerCondition': number_of_grids_per_condition,
                    'values': grid,
                })

    # Write the grid to the output file
    with open(OUTPUT_FILE, 'w+') as output_file:
        json.dump(grids, fp=output_file, indent=4)


if __name__ == '__main__':
    main()
