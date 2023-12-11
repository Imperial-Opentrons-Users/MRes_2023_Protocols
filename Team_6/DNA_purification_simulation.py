from opentrons import simulate
protocol = simulate.get_protocol_api('2.15')

metadata = {
    "apiLevel": "2.15",
    "protocolName": "MDA protocol",
    }

#labware

mag_deck = protocol.load_module('magnetic module', 1)
mag_adapter = mag_deck.load_adapter('opentrons_96_flat_bottom_adapter')
mag_plate = mag_deck.load_labware('corning_96_wellplate_360ul_flat')

sample_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)

tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
reservoir = protocol.load_labware('corning_96_wellplate_360ul_flat', 9)
#A2 = MDA Reaction buffer
#A3 = Enzyme mixture
#A4 = Beads
#A5 = 70% Ethanol
#A6 = Elution buffer
#A7 = Liquid waste
tc = protocol.load_module('thermocycler')
tc_plate = tc.load_labware(name='nest_96_wellplate_100ul_pcr_full_skirt')

#pipettes
p300_multi = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_300])
p20_single = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20])


#protocol

#Preparing warmth for elution buffer
tc.set_block_temperature(temperature=55)
tc.open_lid()
p300_multi.transfer(100, reservoir.wells('A6'), tc_plate.wells('A12'),
                    touch_tip=True, blow_out=True)
tc.close_lid()

#Mixing beads and MDA samples on the sample plate
bead_volume = 1.8*22 #bead ratio multipled by sample volume
p300_multi.transfer(bead_volume, reservoir.wells('A4'), sample_plate.wells('A1'),
                    touch_tip=True, blow_out=True, new_tip='always', 
                    mix_before=(5,22), mix_after=(10,22))

p300_multi.transfer(bead_volume+22+5, sample_plate.wells('A1'), mag_plate.wells('A1'), blow_out=True, touch_tip=True)

#Incubating beads, engaging the magnetic deck, then allowing DNA to settle on mag beads
protocol.delay(minutes = 1)
mag_deck.engage(height_from_base = 0)
protocol.delay(minutes = 2)

#Removing supernatant from the magnetic beads
p300_multi.flow_rate.aspirate = 25 #aspirate slowly to avoid aspirating beads
p300_multi.transfer(bead_volume+22+5, mag_plate.wells('A1'), reservoir.wells('A7'), blow_out=True)


#Washing the beads twice with 70% ethanol
air_volume = p300_multi.max_volume * 0.1 #adding air gap to prevent dripping of ethanol

for i in range(2):
    p300_multi.pick_up_tip()
    p300_multi.transfer(200, reservoir.wells('A5'), mag_plate.wells('A1'), 
                        air_gap=air_volume, new_tip='never')
    protocol.delay(minutes=0.5) #adding gap to prevent drip anywhere else
    p300_multi.transfer(200, mag_plate.wells('A1'), reservoir.wells('A7'), 
                        air_gap=air_volume, new_tip='never')   
    p300_multi.drop_tip()

#Allowing beads to try at room temperature
protocol.delay(minutes=5)
mag_deck.disengage()

#Mixing beads with the elution buffer
tc.open_lid()
p300_multi.transfer(100, tc_plate.wells('A12'), mag_plate.wells('A1'),
                    new_tip='always',blow_out=True,  mix_after=(10,50))

#incubating at room temp for 5 minutes
tc.close_lid()
protocol.delay(minutes=5)
mag_deck.engage(height_from_base = 0)
protocol.delay(minutes=2)

#Isolating purified DNA products
p300_multi.transfer(100, mag_plate.wells('A1'), mag_plate.wells('A2'), blow_out=True, touch_tip=True)

for line in protocol.commands(): 
    print(line)
