"""
How to run this protocol:
1. Make sure all labware and instrument definitions are available in your Opentrons Robot (check the template file)
2. Adapt the conditions_config variable to your needs
"""

import os
import csv
import json
import datetime
import string
import random

now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

WELLS = [
    f"{row}{col}" for col in range(1, 7) for row in string.ascii_uppercase[:8]
]  # 48 wells


# USER input: final concentration of C and S desired in wells for each condition
# each dictionary in CONDITIONS_CONFIG represents one condition
# add more lines as needed (conditions must be even number)
CONDITIONS_CONFIG = [
    {"c1": 100, "c2": 0, "s1": 10, "s2": 0},
    {"c1": 100, "c2": 0, "s1": 0, "s2": 10},
    {"c1": 100, "c2": 0, "s1": 0, "s2": 0},
    {"c1": 0, "c2": 100, "s1": 10, "s2": 0},
    {"c1": 0, "c2": 100, "s1": 0, "s2": 10},
    {"c1": 0, "c2": 100, "s1": 0, "s2": 0},
]

# USER input: Concentartion of stocks availablee for C/S
STOCK = {"c1": 1000, "c2": 1000, "s1": 1000, "s2": 1000}  # mM  # mM  # mg/ml  # mg/ml


def read_conditions_from_csv(file_path):
    with open(file_path, mode="r") as file:
        csv_reader = csv.DictReader(file)
        conditions_from_csv = []

        for row in csv_reader:
            condition = {"ingredients": row}  # Assuming each row represents a condition
            conditions_from_csv.append(condition)

        return conditions_from_csv


def assign_wells_to_conditions(num_conditions):
    shuffled = sorted(WELLS, key=lambda k: random.random())
    conditions = [[] for _ in range(num_conditions)]
    for idx, well in enumerate(shuffled):
        conditions[idx % num_conditions].append(well)

    return conditions


def generate_file_content(layout_json: str, conditions_config_json: str):
    with open("protocol_template.py", "r") as template:
        file_content = template.read()

    insert = f"""layout_json = \"\"\"{layout_json}\"\"\"\nlayout = json.loads(layout_json)\nconditions_config_json = \"\"\"{conditions_config_json}\"\"\"\nconditions_config = json.loads(conditions_config_json)\nstock_json = \"\"\"{json.dumps(STOCK)}\"\"\"\nstock = json.loads(stock_json)"""

    file_content = file_content.replace("# GENERATED CODE INSERT HERE #", insert)

    return file_content


conditions = {"conditionToWell": assign_wells_to_conditions(len(CONDITIONS_CONFIG))}

layout_json = json.dumps(conditions, indent=4)
conditions_config_json = json.dumps(CONDITIONS_CONFIG, indent=4)

# create a folder for the current generated protocol
folder_name = f"protocol_{now_str}"
os.mkdir(f"generated/{folder_name}")

# write layout to file
with open(f"generated/{folder_name}/layout.json", "w") as layout_file:
    layout_file.write(layout_json)

# filename with current data and time in it (to know what was loaded on the opentrons)
file_name = f"protocol_{now_str}.py"

# write file content to file (/generated folder)
with open(f"generated/{folder_name}/{file_name}", "w") as file:
    file.write(generate_file_content(layout_json, conditions_config_json))
