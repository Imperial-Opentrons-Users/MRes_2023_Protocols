import random
from opentrons import protocol_api
import json

layout = None
conditions_config = None

# GENERATED CODE INSERT HERE #

conditions = layout["conditionToWell"]

# INFORMATION FOR USER:
# protocol has been optmized for varying 2 components and 2 supplements i.e. 6 conditions
# where the control is the component without the supplement
# components (C) ex: c1=glucose and c2=gluconate
# supplements (S) ex: S1=vitamin A and S2=vitamin B
# commponents are in mM and supplements mg/ml

# PART 1: making master mixes for each condition suing available stock in lab

# PART 1a : define conditions, volumes and concentrations

# USER input: final concentration of C and S desired in wells for each condition
# each dictionary in CONDITIONS_CONFIG represents one condition
# add more lines as needed (conditions must be even number)


# USER input: Concentartion of stocks availablee for C/S
STOCK = {"c1": 1000, "c2": 1000, "s1": 1000, "s2": 1000}  # mM  # mM  # mg/ml  # mg/ml

# USER define number of wells to use in 96 well plate
NUM_WELLS = 48

# number of conditions stored as number of condtions input by user
num_cond = len(conditions_config)
num_cond_repeats = NUM_WELLS // num_cond  # calculates repeats of each condition

# USER define volume parameters to calculate total needed volume of each condition mastermix
vol_per_well = 90  # µL
tolerance = 2  # extra volume

# PART 1b: calculating liquid handling to generate mastermixes for each condition

total_vol = num_cond_repeats * vol_per_well * (1 + tolerance)  # µL

conditionToMediaVol = (
    []
)  # store volumes needed of C1, c2, S1, S2, minimal media for each condition

for condition in conditions_config:  # calculate volume of each stock for each condition
    c1stock_pip = condition["c1"] * total_vol / STOCK["c1"]
    c2stock_pip = condition["c2"] * total_vol / STOCK["c2"]
    s1stock_pip = condition["s1"] * total_vol / STOCK["s1"]
    s2stock_pip = condition["s2"] * total_vol / STOCK["s2"]
    minmed_pip = total_vol - (c1stock_pip + c2stock_pip + s1stock_pip + s2stock_pip)

    ## Create a dictionary to store the information
    pipette_info = {}

    pipette_info["c1"] = c1stock_pip
    pipette_info["c2"] = c2stock_pip
    pipette_info["s1"] = s1stock_pip
    pipette_info["s2"] = s2stock_pip
    pipette_info["min_media"] = minmed_pip

    conditionToMediaVol.append(pipette_info)  # append to larger list

mediaVolToCondition = {}

for mediaVolumes in conditionToMediaVol:
    for key in mediaVolumes:
        if key not in mediaVolToCondition:
            mediaVolToCondition[key] = []

        mediaVolToCondition[key].append(mediaVolumes[key])

metadata = {"apiLevel": "2.8"}


def run(protocol: protocol_api.ProtocolContext):
    # LABWARE
    # USER action : place relevant labware in right position
    tiprack_1 = protocol.load_labware("opentrons_96_tiprack_300ul", 10)
    p300 = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tiprack_1])

    tiprack_2 = protocol.load_labware("opentrons_96_tiprack_300ul", 11)
    p300m = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[tiprack_2])

    # 96 well plate used for cells in conditions with randomized lay-out
    target_plate = protocol.load_labware("costar_96_wellplate_360ul", 1)

    # tube rack for stocks required to make different conditions
    # USER action: place stocks in tube rack
    # c1 in A2
    # c2 in B2
    # s1 in C1
    # s2 in B1
    stock_holder = protocol.load_labware(
        "opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", 9
    )

    # reservoir will store mastermix for each condtions
    # USER action: pour out minimal media in slit A12
    slit_reservoir = protocol.load_labware("4ti0131_12_reservoir_21000ul", 5)

    # Preparing Master Mix for each condition by pipetting each stock

    # minimal media
    p300m.pick_up_tip()
    for i in range(num_cond):
        p300m.transfer(
            (mediaVolToCondition["min_media"][i] / 8),
            slit_reservoir["A12"],
            slit_reservoir[f"A{i + 1}"],
            new_tip="never",
        )
    p300m.drop_tip()

    # c1
    p300.pick_up_tip()
    for i in range(num_cond):
        if mediaVolToCondition["c1"][i] <= 0:
            continue

        p300.transfer(
            mediaVolToCondition["c1"][i],
            stock_holder["A2"],
            slit_reservoir[f"A{i + 1}"],
            new_tip="never",
        )
    p300.drop_tip()

    # c2
    p300.pick_up_tip()
    for i in range(num_cond):
        if mediaVolToCondition["c2"][i] <= 0:
            continue

        p300.transfer(
            mediaVolToCondition["c2"][i],
            stock_holder["B2"],
            slit_reservoir[f"A{i + 1}"],
            new_tip="never",
        )
    p300.drop_tip()

    # s1
    p300.pick_up_tip()
    for i in range(num_cond):
        if mediaVolToCondition["s1"][i] <= 0:
            continue

        p300.transfer(
            mediaVolToCondition["s1"][i],
            stock_holder["C1"],
            slit_reservoir[f"A{i + 1}"],
            new_tip="never",
        )
    p300.drop_tip()

    # s2
    p300.pick_up_tip()
    for i in range(num_cond):
        if mediaVolToCondition["s2"][i] <= 0:
            continue

        p300.transfer(
            mediaVolToCondition["s2"][i],
            stock_holder["B1"],
            slit_reservoir[f"A{i + 1}"],
            new_tip="never",
        )
    p300.drop_tip()

    # Mix media
    for n in range(num_cond):
        p300m.pick_up_tip()
        p300m.mix(4, 200, slit_reservoir[f"A{n + 1}"])
        p300m.drop_tip()

    # Pipette Master Mix into wells
    for n in range(num_cond):
        p300.pick_up_tip()
        for i in range(len(conditions[n])):
            p300.transfer(
                100,
                slit_reservoir[f"A{n + 1}"],
                target_plate[f"{conditions[n][i]}"],
                new_tip="never",
            )
        p300.drop_tip()
