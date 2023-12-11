"""Transferring cell culture from a 96 well plate to be centrifuged. 
   In Noah's protocol a customised 48 well rack was used for cell culturing,
   in the absence of this we used two 96 well plates to simulate the step"""

import random
from opentrons import protocol_api
metadata = {'apiLevel': '2.8'}
def run(protocol:protocol_api.ProtocolContext):

    # protocol setup
    source_plate = protocol.load_labware('costar_96_wellplate_360ul', '1')
    tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    target_plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', '2')
    stock_holder = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '9')
    slit_reservoir_1 = protocol.load_labware('4ti0131_12_reservoir_21000ul', '5')
    slit_reservoir_2 = protocol.load_labware('4ti0131_12_reservoir_21000ul', '3')

    # instrument setup
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack])

  #Silica beads 96 well plate
    p300.pick_up_tip()
    p300.transfer(200, slit_reservoir_2.columns(0), source_plate.columns(), new_tip = "never")
    p300.drop_tip()
