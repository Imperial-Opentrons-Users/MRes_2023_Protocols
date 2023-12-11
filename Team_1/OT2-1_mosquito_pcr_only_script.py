# Code block to run PCR for second gene locus using same gDNA extracted in the first protocol (same but without lysis and dilution)

# Check for sufficient tips and reload clean plate into thermocycler.

#Check gDNA plate is in block 1
from opentrons import protocol_api, simulate

metadata = {
'apiLevel': '2.8',
'protocolName': 'mosquitoesPCR_8channel',
'description': 'MRes 2023 Team 1'
}

protocol = simulate.get_protocol_api('2.8')

requirements = {'robotType': 'OT-2'}

def run(protocol: protocol_api.ProtocolContext): #runs the PCR for genotyping only

    # load thermocycler GEN 2 module
    thermocycler = protocol.load_module(module_name='thermocyclerModuleV2')

    # open thermocycler lid
    thermocycler.open_lid()

    # load labware
    tips1 = protocol.load_labware('opentrons_96_tiprack_20ul', 5)
    tips2 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    tips3 = protocol.load_labware('opentrons_96_tiprack_300ul', 3)
    reservoir = protocol.load_labware('4ti0136_96_wellplate_2200ul', 2)
        # A1 = mega MM with less water (to account for the 1 in 4 dilution of gDNA. Dilution occurs later on in this protocol after sample lysis)
        # A2 = water
    P1 = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', 1) # larvae plate
    P2 = thermocycler.load_labware(name='opentrons_96_wellplate_200ul_pcr_full_skirt')  # thermocycler PCR plate

    # pipettes (2 different pipette types are required for this protocol)
    p20 = protocol.load_instrument('p20_multi_gen2', 'left',
                                    tip_racks=[tips1, tips2])
    p300 = protocol.load_instrument('p300_multi_gen2', 'right',
                                    tip_racks=[tips3])


    # combined transfer step
    p20.transfer(9, reservoir['A1'].bottom(z=-2), P2.rows()[0], touch_tip=False, new_tip='once',    # transfer 9 µL of mega MM PCR to PCR plate
                 blow_out=True, blowout_location='destination well')
    p300.transfer(61.5, reservoir['A2'].bottom(z=-2), P1.rows()[0], mix_after=(3,50), touch_tip=True, new_tip='always',
                  blow_out=True, blowout_location='destination well') # dilute prepped gDNA 1/4 with water to allow for larger volume transfer (as 0.5 ul specified in the original protocol is too small)
    p20.transfer(1, P1.rows()[0], P2.rows()[0], mix_after=(3,3), new_tip='always', aspirate_flow_rate=1,
                 blow_out=True, blowout_location='destination well')                      # transfer 1µL of prepped and diluted gDNA to PCR plate

    thermocycler.close_lid()


    # PCR

    anneal_temp = 60

    extension_time = 20
    
    thermocycler.set_lid_temperature(temperature=anneal_temp)

    init_denature = [
    {'temperature':98, 'hold_time_seconds':300}               # denaturation step at 98ºC
    ]

    pcr_loop = [
    {'temperature':98, 'hold_time_seconds':5},                # denaturation
    {'temperature':anneal_temp, 'hold_time_seconds':5},       # annealing
    {'temperature':72, 'hold_time_seconds':extension_time}    # extension
    ]

    final = [
    {'temperature':72, 'hold_time_seconds':60},               # final extension
    ]

    thermocycler.execute_profile(steps=init_denature, repetitions=1)
    thermocycler.execute_profile(steps=pcr_loop, repetitions=40)
    thermocycler.execute_profile(steps=final, repetitions=1)

    thermocycler.set_block_temperature(temperature=10)   # after the end of PCR, PCR products held at 10ºC
    thermocycler.deactivate_lid()
    protocol.pause('Resume to open thermocycler lid.')
    thermocycler.open_lid()

    for line in protocol.commands():
        print(line)