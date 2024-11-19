from opentrons import protocol_api, simulate

metadata = {
'apiLevel': '2.13',
'protocolName': 'mosquitoesPCR_8channel',
'description': 'MRes 2023 Team 1'
}

protocol = simulate.get_protocol_api('2.13')

requirements = {'robotType': 'OT-2'}

def run(protocol: protocol_api.ProtocolContext):


    ################### SET UP ###################

    thermocycler = protocol.load_module(module_name='thermocyclerModuleV2')

    thermocycler.open_lid()

    # labware
    tips1 = protocol.load_labware('opentrons_96_tiprack_20ul', 5)
    tips2 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
    tips3 = protocol.load_labware('opentrons_96_tiprack_300ul', 3)
    reservoir = protocol.load_labware('4ti0136_96_wellplate_2200ul', 2)
        # A1 = MM with less H2O (accounts 1/4 gDNA dilution of gDNA for later in protocol)
        # A2 = H2O
        # A3 = lysis buffer
        # A4 = lysis buffer + control H2O in last well
    P1 = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', 1)        # larvae plate
    P2 = thermocycler.load_labware(name='opentrons_96_wellplate_200ul_pcr_full_skirt')  # thermocycler PCR plate

    # pipettes
    p20 = protocol.load_instrument('p20_multi_gen2', 'left',
                                    tip_racks=[tips1, tips2])
    p300 = protocol.load_instrument('p300_multi_gen2', 'right',
                                    tip_racks=[tips3])



    ########## SAMPLE PREP (LYSIS STEP) ##########


    p20.pick_up_tip()                       # 20.5 µl lysis buffer to each well, split in 2
    for i in range(11):
        p20.transfer(
          10.25,
          reservoir['A3'],
          P2.rows()[0][i].top(z=-16),       # note: z-offset to minimise cross-
          blow_out=True,                    # contamination & conserve tips
          blowout_location='destination well',
          new_tip='never')
        p20.touch_tip(v_offset=-16)
        p20.transfer(
          10.25,
          reservoir['A3'],
          P2.rows()[0][i].top(z=-16),
          blow_out=True,
          blowout_location='destination well',
          new_tip='never')
        p20.touch_tip(v_offset=-16)
    p20.drop_tip()
    p20.pick_up_tip()
    p20.transfer(                          # ensures only H2O in H12
        10.25,
        reservoir['A4'],
        P2.rows()[0][11].top(z=-16),
        blow_out=True,
        blowout_location='destination well',
        new_tip='never')
    p20.touch_tip(v_offset=-16)
    p20.transfer(
        10.25,
        reservoir['A4'],
        P2.rows()[0][11].top(z=-16),
        blow_out=True,
        blowout_location='destination well',
        new_tip='never')
    p20.touch_tip(v_offset=-16)
    p20.drop_tip()

    # incubate 5 min room temp, 2 min 98º
    thermocycler.close_lid()

    thermocycler.set_block_temperature(
        temperature=25,
        hold_time_minutes=5)

    thermocycler.set_lid_temperature(temperature=98)
    thermocycler.set_block_temperature(
        temperature=98,
        hold_time_minutes=2)

    thermocycler.open_lid()

    # 'hold' step to allow time for plate swap in thermocycler
    protocol.pause('Move larvae plate from thermocycler to block 1 and put new PCR plate in thermocycler')

    # combined transfer step
    p20.pick_up_tip()
    for i in range(12):
        p20.transfer(                   # transfer 9 µL of MM PCR to PCR plate
          9,
          reservoir['A1'],
          P2.rows()[0][i].bottom(z=-10.5),
          blow_out=True,
          blowout_location='destination well',
          new_tip='never')
        p20.touch_tip(v_offset=-16)
    p20.drop_tip()
    p300.transfer(                      # dilute prepped gDNA 1/4 with water to allow
      61.5,                             # for larger volume transfer (as 0.5 µl specified
      reservoir['A2'],                  # in the original protocol is too small for p20)
      P1.rows()[0],
      mix_after=(3,50),
      new_tip='always',
      touch_tip=True,
      blow_out=True,
      blowout_location='destination well')
    for i in range(12):
        p20.pick_up_tip()
        p20.transfer(
          1,
          P1.rows()[0][i],
          P2.rows()[0][i].bottom(z=-10.5),
          mix_after=(3,3),
          blow_out=True,
          blowout_location='destination well',
          new_tip='never')
        p20.touch_tip(v_offset=-16)
        p20.drop_tip()

    thermocycler.close_lid()



    ################### PCR STEP ###################


    anneal_temp = 60           # modified with
    extension_time = 20        # user inputs

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

    thermocycler.set_block_temperature(temperature=10)     # PCR products held at 10ºC
    thermocycler.deactivate_lid()
    protocol.pause('Resume to open thermocycler lid.')
    thermocycler.open_lid()

    for line in protocol.commands():
        print(line)