#This code was written to set up plates for our wet run. Two source plates were filled with buffer and a pause step included so we could add dye randomly to different wells. Touch tip was only used for the microtitre plates as the amount of volume in each well was less important for setting up the random concentrations, but much more important for accurately analysing the fluorescence from each well.
#This code also sets up a microtitre plate with buffer to be used as a validation plate for the wet run of the cherrypicking protocol.
#Volumes of 500 uL per well were selected to represent typical media volumes in a 96-well deep well plate.
#Total volume of 200 uL was selected for analysis in the 200 uL plate. 50 uL of solution to be analysed was diluted with water. This ensured we could take several repeats from each well in the source plate without being limited by volume.

# Define labware
from opentrons import protocol_api
requirements = {"robotType": "OT-2", "apiLevel": "2.15"}

def run(protocol: protocol_api.ProtocolContext):
  # Flat bottom 96-well plate for fluorescence analysis of plate 1
  flat_96_val = protocol.load_labware('corning_96_wellplate_360ul_flat', '6')
  #flat bottom 96 well plate for fluorescence analysis of plate 2
  flat_96_val2 = protocol.load_labware('corning_96_wellplate_360ul_flat', '7')
  #flat bottom 96 well plate for fluoresnce analysis of cherrypicked plate
  flat_96_cherrypicked = protocol.load_labware('corning_96_wellplate_360ul_flat', '8')
  # Source 96-well plate 1
  source_96 = protocol.load_labware('thermoscientificnunc_96_wellplate_1300ul', '5')
  #Source 96-well plate 2
  source_96_2 = protocol.load_labware('thermoscientificnunc_96_wellplate_1300ul', '9')

  # Trough
  trough = protocol.load_labware('nest_12_reservoir_15ml', '2')

  # Tips
  tiprack1_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '4')
  tiprack2_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '1')
  tiprack3_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')


  # Reagent setup
  growth_media = trough.wells('A1')

  # Pipette
  m300 = protocol.load_instrument('p300_multi_gen2','left', tip_racks=[tiprack1_300, tiprack2_300, tiprack3_300])
  
  #columns
  cols = [j + str(i) for j in ['A'] for i in range(1, 13)]
  #transfer of buffer into 2 deep-well 96 plates to set up different dye concentrations. For the wet run we are cherrypicking from 2 source plates. 500 uL added to each well to represent growth media.
  m300.pick_up_tip()
  for i in cols:
   m300.transfer(250, growth_media, source_96[i], new_tip='never', blow_out=True, blowout_location='destination well')
   m300.transfer(250, growth_media, source_96[i], new_tip='never', blow_out=True, blowout_location='destination well')
   m300.transfer(250, growth_media, source_96_2[i], new_tip='never', blow_out=True, blowout_location='destination well')
   m300.transfer(250, growth_media, source_96_2[i], new_tip='never', blow_out=True, blowout_location='destination well')
    
  #transfer of buffer into 3 microtitre plates (2 for analysis of source plates, 1 for analysis of cherrypicked plate). 150 uL of buffer was chosen so that a smaller volume of solution could be taken from each well for the validation plate. This means we could test the protocol with multiple repeats and have enough volume to do so,
  for i in cols:
   m300.transfer(150, growth_media, flat_96_val[i], new_tip='never', blow_out=True, blowout_location='destination well', touch_tip=True)
   m300.transfer(150, growth_media, flat_96_val2[i], new_tip='never', blow_out=True, blowout_location='destination well', touch_tip=True)
   m300.transfer(150, growth_media, flat_96_cherrypicked[i], new_tip='never', blow_out=True, blowout_location='destination well', touch_tip=True)
  
  m300.drop_tip()

#Pause once buffer is dispensed. Add dye to many random wells in the two source plates. Ensure that source plates and their corresponding microtitre plates are labelled.
  protocol.pause('Add Dye')

  #resuspend dye and take 50ul of each 96 well plate and transfer to flatbottom well plate. 200 uL total in each flat-bottomed plate. This step was only performed for the source plates, as the cherrypicked flat-bottom plate will be filled with the dye samples in the cherrypicking protocol.
  
  for i in range(1, 13):
     m300.transfer(50, source_96.wells('A'+str(i)), flat_96_val.wells('A'+str(i)), mix_before=(2,50), new_tip='always', blow_out=True, blowout_location='destination well', touch_tip=True)
     m300.transfer(50, source_96_2.wells('A'+str(i)), flat_96_val2.wells('A'+str(i)), mix_before=(2,50), new_tip='always', blow_out=True, blowout_location='destination well', touch_tip=True)


 
