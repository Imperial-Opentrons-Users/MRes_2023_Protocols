from opentrons import protocol_api
from opentrons import simulate
protocol = simulate.get_protocol_api('2.15')

metadata = {'apiLevel': '2.15',
               'protocolName':'ELISA protocol group 4',
    'description': '''Following protocols provided by the Polizzi group, this script purifies centrifuged P.pastoris 1 mL cultures, then performs an ELISA to determine protein of interest concentration. ''',
    'author': 'Group Four'}


def which_PBS(current_PBS,reservoir,trash):
    if current_PBS<22000:
        return(reservoir["A8"])
    elif current_PBS<44000:
        return(reservoir["A12"])
    elif current_PBS<66000:
        return(reservoir["A8"])
    elif current_PBS<88000:
        return(trash["A10"])
    elif current_PBS<110000:
        return(trash["A11"])
    elif current_PBS<132000:
        return(trash["A12"])
    # elif current_PBS<154000:
    #     return(trash["A12"])

def which_trash(current_trash):
    if current_trash<22000:
        return("A1")
    elif current_trash<44000:
        return("A2")
    elif current_trash<66000:
        return("A3")
    elif current_trash<88000:
        return("A4")
    elif current_trash<110000:
        return("A5")
    elif current_trash<132000:
        return("A6")  
    elif current_trash<154000:
        return("A7")  
    elif current_trash<176000:
        return("A8")  
    elif current_trash<198000:
        return("A9")  
def run(protocol:protocol_api.ProtocolContext):
    current_PBS = 0
    current_trash = 0
    ########################
    # LOAD LABWARE 
    ########################
    
    # LOAD P300 PIPETTE TIPS IN SLOTS 5, 6, 7, 9, 10
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    tiprack_3 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    tiprack_4 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)
    tiprack_5 = protocol.load_labware('opentrons_96_tiprack_300ul', 9)
    tiprack_6 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)
    
    # LOAD P300 MULTI-CHANNEL PIPETTE & DEFINE WHICH TIPS TO USE
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tiprack_1,tiprack_2,tiprack_3,tiprack_4,tiprack_5,tiprack_6])
    # DEFINE PIPETTE FLOW RATE (default is 94, decreased to aid liquid uptake)
    p300.flow_rate.aspirate = 40   
    # DEFINE HOW FAR DOWN PIPETTE GOES (default is 1 mm from bottom of well, increased to 5 to aid uptake & avoid disruption of centrifugation pellet / magnetic beads)
    p300.well_bottom_clearance.aspirate = 5
    p300.well_bottom_clearance.dispense = 5
   
    # LOAD RESERVOIR CONTAINING REAGENTS IN SLOT 1
        #A1 well is 2M NaOH
        #A2 will have 20 mL Ni-NTA equilibration buffer
        #A3 will have pre aliquoted 1 mL of Pierce NiNTA magnetic agarose beads
        #A4 is Ni-NTA wash buffer 
        #A5 is Ni-NTA elution buffer for beads
        #A6 is ELISA coating solution 
        #A7 is ELISA blocking buffer
        #A8 is PBS-T
        #A9 is ELISA primary antibody
        #A10 is ELISA secondary antibody
        #A11 is PnPP
        #A12 is PBS
    # LOAD RESERVOIR #2/TRASH CONTAINING REAGENTS IN SLOT 1
        #A1-A9 is for trash
        #A10-A12 is for PBS
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 1)
    
    # LOAD ELISA 96 WELL PLATE IN SLOT 3
    plate = protocol.load_labware('thermofischer_96_wellplate_400ul', 3)
    
    # LOAD 96 DEEP WELL PLATE IN SLOT 2
        # samples 1-8 are in col 1, samples 9-16 are in col 2
    deep_well = protocol.load_labware('4ti0136_96_wellplate_2200ul', 2)
    
    # LOAD RESERVOIR FOR WASTE LIQUIDS IN SLOT 11
    trash = protocol.load_labware('usascientific_12_reservoir_22ml', 11)

    # LOAD MAGNETIC MODULE WITH ADAPTER AND 96 WELL PLATE IN SLOT 7
    mag_mod = protocol.load_module('magnetic module', 4)
    mag_adapter = mag_mod.load_adapter('opentrons_96_flat_bottom_adapter')
    mag_rack = mag_mod.load_labware('thermofischer_96_wellplate_400ul')

    ########################
    # EXTRACT SUPERNATANTS, CORRECT pH, DUPLICATE SAMPLES
    ########################
    
    # ADD 80 µL NaOH TO SUPERNATANT SAMPLES
    p300.transfer(80, reservoir["A1"], deep_well.rows()[0][2:4],blow_out = True)#, mix_after=(3, 50))
    
    # 1 mL CENTRIFUGED CULTURES IN SLOT 2 DEEP WELL PLATE, COLUMNS 1 & 2
    # EXTRACT 800 µL SUPERNATANT INTO NEW COLUMNS 3 & 4
    p300.transfer(800, deep_well.rows()[0][0], deep_well.rows()[0][2], mix_after=(3, 50))
    p300.transfer(800, deep_well.rows()[0][1], deep_well.rows()[0][3],mix_after=(3, 50))

    # PAUSE FOR 1 HOUR FOR SALTS TO SETTLE
    protocol.delay(minutes = 60)
    
    # TAKE TWO 300 µL ALIQUOTS OF NEUTRALISED SAMPLES
    # magnetic plate wells cannot hold 600 µL so divide them up
    # leaves 280 µL of neutralised samples in slot 2, cols 3 & 4
    # samples 1-8 made into two tech reps in cols 5,6
    p300.transfer(300, deep_well.rows()[0][2], deep_well.rows()[0][4:6])#, mix_after=(3, 50))
    #samples 9-16 made into two tech reps in cols 7,8
    p300.transfer(300, deep_well.rows()[0][3], deep_well.rows()[0][6:8])#, mix_after=(3, 50))
    
    ########################
    # Ni-NTA MAGNETIC BEAD PURIFICATION
    ########################
    
    # EQUILIBRATE MAGNETIC BEADS
    # ADD 9 mL EQUILIBRATION BUFFER TO 1 mL BEAD SLURRY 
    p300.transfer(9000/8, reservoir["A2"], reservoir["A3"], mix_after=(3, 50))
    # MIX THEN TRANSFER TO MAGNETIC PLATE
    p300.transfer(10000/8, reservoir["A3"], mag_rack.rows()[0][0], mix_before=(3, 50))
    # ENGAGE MAGNET
    mag_mod.engage(height_from_base=4.4)
    # PAUSE FOR 2 MINUTES FOR BEADS TO SETTLE
    protocol.delay(minutes = 2)
    # REMOVE EQUILIBRIUM BUFFER
    current_trash += 8000
    p300.transfer(8000/8, mag_rack.rows()[0][0], trash[which_trash(current_trash)])#, mix_after=(3, 50))
    # DISENGAGE MAGNET
    mag_mod.disengage()       
    
    # EQUILIBRATE BEADS AGAIN
    # ADD 1800 µL EQUILIBRATION BUFFER TO BEADS
    p300.transfer(8000/8, reservoir["A2"], mag_rack.rows()[0][0], mix_after=(3, 50))
    #DISTRIBUTE 312 UL OF BEAD-EQUILIBRATION MIX TO THE NEXT FOUR COLUMNS
    p300.transfer(10000/32, mag_rack.rows()[0][0],mag_rack.rows()[0][1:5] , mix_after=(3, 50))
    mag_mod.engage(height_from_base=4.4)
    # PAUSE FOR 2 MINUTES FOR BEADS TO SETTLE
    protocol.delay(minutes = 2)
    # REMOVE EQUILIBRIUM BUFFER 
    current_trash += 270*32
    p300.transfer(270, mag_rack.rows()[0][1:5], trash[which_trash(current_trash)])#, mix_after=(3, 50))
    # DISENGAGE MAGNET
    mag_mod.disengage()
    
    # TRANSFER 300 uL OF SAMPLES ONTO MAG PLATE TO MIX WITH BEADS AND GIVE ENOUGH VOLUME TO REMOVE BEADS
    p300.transfer(300, deep_well.rows()[0][4:6],mag_rack.rows()[0][1:3], mix_after=(3, 50)) 
    p300.transfer(330, mag_rack.rows()[0][1:3],deep_well.rows()[0][4:6],  mix_after=(3, 50))

    p300.transfer(300, deep_well.rows()[0][6:8],mag_rack.rows()[0][1:5], mix_after=(3, 50)) 
    # TRANSFER SAMPLE+BEAD MIX BACK TO DEEP WELL PLATE (magnet very strong so this maximises protein binding)
    p300.transfer(330, mag_rack.rows()[0][3:5],deep_well.rows()[0][6:8],  mix_after=(3, 50))

    # PAUSE FOR 5 MINUTES FOR PROTEIN TO BIND BEADS
    protocol.delay(minutes = 5)
    # TRANSFER BACK INTO MAGNETIC PLATE
    p300.transfer(330, deep_well.rows()[0][4:6],mag_rack.rows()[0][1:3])#, mix_after=(3, 50)) 
    p300.transfer(330, deep_well.rows()[0][6:8],mag_rack.rows()[0][3:5])#, mix_after=(3, 50)) 
    # ENGAGE MAGNET
    mag_mod.engage(height_from_base=4.4)
    # PAUSE FOR 3 MINUTES FOR BEADS TO SETTLE
    protocol.delay(minutes = 3)
    # REMOVE 300 µL SUPERNATANT
    current_trash += 5280
    p300.transfer(330, mag_rack.rows()[0][1:3], trash[which_trash(current_trash)])#, mix_after=(3, 50))
    current_trash += 5280
    p300.transfer(330, mag_rack.rows()[0][3:5], trash[which_trash(current_trash)])#, mix_after=(3, 50))
    # DISENGAGE MAGNET
    mag_mod.disengage()  
    
    # ADD 300 µL WASH BUFFER
    p300.transfer(300, reservoir["A4"], mag_rack.rows()[0][1:5], mix_after=(3, 50))
    # ENGAGE MAGNET
    mag_mod.engage(height_from_base=4.4)
    # PAUSE FOR 2 MINUTES FOR BEADS TO SETTLE
    protocol.delay(minutes = 2)
    # REMOVE WASH BUFFER
    current_trash += 2400*4
    p300.transfer(300, mag_rack.rows()[0][1:5], trash[which_trash(current_trash)])#, mix_after=(3, 50))
    # DISENGAGE MAGNET
    mag_mod.disengage() 
    
    # ADD 300 µL WASH BUFFER AGAIN
    p300.transfer(300, reservoir["A4"], mag_rack.rows()[0][1:5], mix_after=(3, 50))
    # ENGAGE MAGNET
    mag_mod.engage(height_from_base=4.4)
    # PAUSE FOR 2 MINUTES FOR BEADS TO SETTLE
    protocol.delay(minutes = 2)
    # REMOVE WASH BUFFER
    current_trash += 2400*4
    p300.transfer(300, mag_rack.rows()[0][1:5], trash[which_trash(current_trash)])#, mix_after=(3, 50))
    # DISENGAGE MAGNET
    mag_mod.disengage() 
    
    # ADD 100 µL ELUTION BUFFER
    p300.transfer(100, reservoir["A5"], mag_rack.rows()[0][1:5], mix_after=(3, 50))
    # TRANSFER OFF OF MAGNET TO MAXIMISE ELUTION (magnet very strong)
    # samples 1-8 duplicates to deep well plate column 9
    p300.transfer(100, mag_rack.rows()[0][1:3],deep_well.rows()[0][8], mix_after=(3, 50))
    # samples 9-16 duplicates to deep well plate column 10
    p300.transfer(100, mag_rack.rows()[0][3:5],deep_well.rows()[0][9], mix_after=(3, 50))
    # PAUSE FOR 10 MINUTES FOR PROTEIN TO ELUTE
    protocol.delay(minutes = 10)
    # TRANSFER BACK TO MAGNETIC PLATE
    # samples 1-8 to magnetic plate col 6, samples 9-16 to col 77
    p300.transfer(200, deep_well.rows()[0][8:10],mag_rack.rows()[0][5:7], mix_after=(3, 50),new_tip = 'always')
    # ENGAGE MAGNET
    mag_mod.engage(height_from_base=4.4)
    # PAUSE FOR 2 MINUTES FOR BEADS TO SETTLE
    protocol.delay(minutes = 2)
    # TRANSFER 200 µL ELUTED SAMPLE INTO DEEP WELL PLATE COLS 11 & 12
    p300.transfer(200, mag_rack.rows()[0][5:7], deep_well.rows()[0][10:])
    
    
    ########################
    # ELISA
    ########################
    
    # SET UP DILUTION PLATE - starting with 2x to 32x
    # ADD COATING SOLUTION TO WELLS (cols 1-6, 7-12)
    p300.transfer(100, reservoir["A6"], plate.rows()[0][0:12])
    
    # TRANSFER 100 µL PURIFIED SAMPLES 1-8 TO ELISA PLATE COLUMN 1
    # (100 µL purified samples remain in deep well cols 11 & 12 for reserve)
    p300.transfer(100, deep_well.rows()[0][10], plate.rows()[0][0])#, mix_after=(3, 50))
    # TRANSFER 100 µL PURIFIED SAMPLES 9-16 TO ELISA PLATE COLUMN 7
    p300.transfer(100, deep_well.rows()[0][11], plate.rows()[0][6])#, mix_after=(3, 50))
    
    # READJUSTING THE ASPIRATE AND DISPENSE HEIGHTS TO THE DEFAULT NOW THAT DONE WITH DEEP WELL
    p300.well_bottom_clearance.aspirate = 1
    p300.well_bottom_clearance.dispense = 1

    # MAKING DILUTIONS OF SAMPLES 1-8 FROM COLUMN 1 TO 6
    p300.transfer(100, plate.rows()[0][:5], plate.rows()[0][1:6], mix_after=(3, 50))
    # EMPTY THE EXTRA 100 uL FROM COLUMN 6 so 100 µL in all wells
    current_trash += 800
    p300.transfer(100, plate.rows()[0][5], trash[which_trash(current_trash)])#, mix_after=(3, 50))

    # MAKING DILUTIONS OF SAMPLES 9-16 FROM COLUMN 7 TO 12
    p300.transfer(100, plate.rows()[0][6:11], plate.rows()[0][7:12], mix_after=(3, 50))
    # EMPTY THE EXTRA 100 uL FROM COLUMN 12 so 100 µL in all wells
    current_trash += 800
    p300.transfer(100, plate.rows()[0][11], trash[which_trash(current_trash)])#, mix_after=(3, 50))
    
    # PAUSE FOR 2 HOURS FOR COATING SOLUTION TO BIND - add cover slip
    protocol.delay(minutes = 120)
    # REMOVE COATING SOLUTION
    current_trash += 800*12
    p300.transfer(100,plate.rows()[0][11::-1], trash[which_trash(current_trash)])
    
    # ADD 200 µL BLOCKING BUFFER
    p300.transfer(200, reservoir["A7"], plate.rows()[0][11::-1])
    # PAUSE FOR 1 HOUR FOR BLOCKING SOLUTION TO BIND
    protocol.delay(minutes=60)
    # REMOVE BLOCKING BUFFER
    current_trash += 1600*12
    p300.transfer(200,plate.rows()[0][11::-1], trash[which_trash(current_trash)])
    # WASH 3 TIMES WITH 100 µL PBS-T
    for wash in range(3):
        current_PBS+=800*12
        p300.transfer(100,which_PBS(current_PBS,reservoir,trash) , plate.rows()[0][11::-1])# mix_after=(1, 50))
        current_trash += 800*12
        p300.transfer(100,plate.rows()[0][11::-1], trash[which_trash(current_trash)])
    
    # ADD 100 µL PRIMARY ANTIBODY
    p300.transfer(100, reservoir["A9"], plate.rows()[0][11::-1])
    # PAUSE FOR 1 HOUR FOR ANTIBODY TO BIND
    protocol.delay(minutes=60)
    # REMOVE PRIMARY ANTIBODY
    current_trash += 800*12
    p300.transfer(100,plate.rows()[0][11::-1], trash[which_trash(current_trash)])    
    for wash in range(3):
        current_PBS+=800*12
        p300.transfer(100,which_PBS(current_PBS,reservoir,trash) , plate.rows()[0][11::-1])# mix_after=(1, 50))
        current_trash += 800*12
        p300.transfer(100,plate.rows()[0][11::-1], trash[which_trash(current_trash)])
    # ADD 100 µL SECONDARY ANTIBODY
    p300.transfer(100, reservoir["A10"], plate.rows()[0][11::-1])
    # PAUSE FOR 1 HOUR FOR ANTIBODY TO BIND
    protocol.delay(minutes=60)
    # REMOVE SECONDARY ANTIBODY
    current_trash += 800*12
    p300.transfer(100,plate.rows()[0][11::-1], trash[which_trash(current_trash)])
    
    # WASH 3 TIMES WITH 100 µL PBS-T, AGITATING FOR 5 MINUTES
    for wash in range(3):
        if wash == 0:
            current_PBS+=800*6
            p300.transfer(100,which_PBS(current_PBS,reservoir,trash) , plate.rows()[0][5::-1], mix_after=(1, 50))
            current_PBS+=800*6
            p300.transfer(100,which_PBS(current_PBS,reservoir,trash) , plate.rows()[0][11:5:-1], mix_after=(1, 50))
            current_trash += 800*6
            p300.transfer(100,plate.rows()[0][5::-1], trash[which_trash(current_trash)])
            current_trash += 800*6
            p300.transfer(100,plate.rows()[0][11:5:-1], trash[which_trash(current_trash)])
            protocol.delay(minutes = 5)
        else:
            current_PBS+=800*12
            p300.transfer(100,which_PBS(current_PBS,reservoir,trash) , plate.rows()[0][11::-1])# mix_after=(1, 50))
            current_trash += 800*12
            p300.transfer(100,plate.rows()[0][11::-1], trash[which_trash(current_trash)])


    # ADD 100 µL PnPP, MIX
    p300.transfer(100, reservoir["A11"], plate.rows()[0][5::-1], mix_after=(3, 50))
    p300.transfer(100, reservoir["A11"], plate.rows()[0][11:5:-1], mix_after=(3, 50))
    # PAUSE FOR 15 MINUTES FOR COLOUR TO DEVELOP
    protocol.delay(minutes = 15)
    # ADD 50 µL NaOH TO STOP REACTION, MIX
    p300.transfer(50, reservoir["A1"], plate.rows()[0][5::-1], mix_after=(3, 50))
    p300.transfer(50, reservoir["A1"], plate.rows()[0][11:5:-1], mix_after=(3, 50))

    # MEASURE ABSORBANCE AT 405 nm
    # Absorbance is directly proportional to protein of interest concentration
    
    return
