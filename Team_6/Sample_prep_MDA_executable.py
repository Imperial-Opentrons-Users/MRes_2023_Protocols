from opentrons import protocol_api

metadata = {
    "apiLevel": "2.15",
    "protocolName": "MDA protocol",
    }

def run(protocol: protocol_api.ProtocolContext):
  
    # Labware setup
    sample_plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 2)
    
    temp_deck = protocol.load_module('temperature module', 4)
    temp_plate = temp_deck.load_labware('opentrons_24_aluminumblock_nest_1.5ml_snapcap')
    
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    reservoir = protocol.load_labware('4ti0131_12_reservoir_21000ul', 9)
    #A2 = MDA Reaction buffer
    #A3 = Enzyme mixture
    #A4 = Beads
    #A5 = 70% Ethanol
    #A6 = Elution buffer
    #A7 = Liquid waste
    tc = protocol.load_module('thermocycler')
    tc_plate = tc.load_labware(name='4ti0960rig_96_wellplate_200ul')
    
    # Pipettes setup
    p300_multi = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_300])
    p20_single = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20])
    
    # Sample Preparation (Assuming samples are pre-prepared in the wells)
    # ...
    
    #preparing reaction buffer and enzyme mixture
    temp_deck.set_temperature(celsius=4)
    p20_single.pick_up_tip()
    p20_single.transfer(180, reservoir['A2'], temp_plate['A6'],
                        blow_out=True, touch_tip=True, new_tip='never')
    p20_single.drop_tip()
    p20_single.transfer(20, reservoir['A3'], temp_plate['A6'],
                        blow_out=True, touch_tip=True, new_tip='always')
    
    tc.close_lid()

    # Cell Lysis
    tc.set_block_temperature(65, hold_time_minutes=10) 
    tc.open_lid()
    
    # MDA Reaction Setup 
    p20_single.flow_rate.aspirate = 25
    p20_single.flow_rate.dispense = 25
    p20_single.transfer(20, temp_plate['A6'], tc_plate.columns()[0], new_tip='always',
                        mix_before=(3,10), mix_after=(3, 11), blow_out=True, touch_tip=True)

    tc.close_lid()
    
    # Incubation for MDA
    tc.set_block_temperature(30, hold_time_minutes = 2) # in actual execution, should be 2 hours (120 mins)
    tc.set_block_temperature(65, hold_time_minutes = 1) # in actual execution, should be 10 mins
    
    tc.open_lid()

    for i in range(8):
        p20_single.transfer(22, tc_plate.columns()[0][i], sample_plate.columns()[0][i],
                            new_tip='once', blow_out=True, touch_tip=True)
