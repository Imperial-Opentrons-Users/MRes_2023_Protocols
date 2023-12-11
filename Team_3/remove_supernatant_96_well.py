"""
This protocol removes the supernatant from a 96-well plate.

How to run this protocol:
1. Make sure all labware and instrument definitions are available in your Opentrons Robot
2. Change the Z_OFFSET to the correct value for the volume of your supernatant (reference: >150ul ~= -0.95mm)
3. Upload and run this protocol
"""

from opentrons import protocol_api

metadata = {"apiLevel": "2.8"}

Z_OFFSET = -0.95  # This depends on the volume of the supernatant


def run(protocol: protocol_api.ProtocolContext):
    # Labware and Instrument Setup
    source_plate = protocol.load_labware("costar_96_wellplate_360ul", "1")
    tiprack = protocol.load_labware("opentrons_96_tiprack_300ul", "10")
    target_plate = protocol.load_labware(
        "costar3370flatbottomtransparent_96_wellplate_200ul", "2"
    )
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[tiprack])
    p300.well_bottom_clearance.aspirate = (
        Z_OFFSET  # This is to aspirate only the supernatant
    )

    # Supernatant pickup
    for col_source, col_target in zip(source_plate.columns(0), target_plate.columns(0)):
        p300.pick_up_tip()
        p300.aspirate(volume=100, location=col_source, rate=0.1)
        p300.dispense(volume=100, location=col_target)
        p300.drop_tip()
