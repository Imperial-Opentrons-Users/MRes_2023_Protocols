# Random Media Mix Allocation into 96 Well Plate and Supernatant removal
### Team 3: Celine Caraffa, Alfie Brown, Will McKenny, Carolina Pestana, Timon Schneider

### Context

Initially, Noah Sprent approached us with a protocol for growing and monitoring the efficiency of carbon-sequestering bacterial cells which we heavily adapted to fit the constraints of this project. In this repository, you will find two protocols. 
1. [Media Mix Allocator](/Team_3/generate_protocol.py) which can be run to generate protocols that make 6 master mixes which are then distributed into 8 random wells each.
2. [Supernatant Removal](/Team_3/remove_supernatant_96_well.py) which removes liquid supernatant from a 96 well plate.

## Setup
### General Requirements (Start here)
- Installed Python Version >3.10

### Random Media Mix Allocator
#### When to use
You have 6 media mixes with specified target concentrations from 4 different media components, that you first want to make using the Opentrons and then have it automatically pipetted into 8, randomly selected wells in the plate.
#### How to use
1. Download the repository
2. Open this folder in your terminal
3. Install all necessary requirements: `pip install -r requirements.txt`
4. Specify all necessary user inputs at the beginning of [Media Mix Allocator](/Team_3/generate_protocol.py)
5. Run the protocol generator: `python generate_protocol.py`. You will find the generated protocol in the `generated` folder alongside the well-media-mix assignment.
6. Load the protocol onto an Opentrons and run it.

### Supernatant Removal
#### When to use
You have a 96 well plate with centrifuged down cells that you want to remove the supernatant from.
#### How to use
1. Download this repository
2. Adjust the Z_OFFSET parameter in the script [Supernatant Removal](/Team_3/remove_supernatant_96_well.py) which accounts for the depth of the pipette in the well.
3. Load the protocol onto an Opentrons and run it.

### File Overview

In this submission file, you will find 4 python files. These scripts help you generate a randomised plate with growth medium and nutrients to measure cell growth and then a final step to remove supernatant to measure in a plate reader.

The steps and subsequent files are:

1. generate_protocol.py - The user inputs desired conditions, concentrations, volumes and number of wells needed for the assay, the code will calculate the master needed for each condition and assign random wells to each condition
2. protocol_template.py - prepares master mixes and pipettes respective conditions into randomised wells predefined from generate_protocol.py
3. silicabeads.py - plates 200ul of cell culture into 96 well plate for centrifugation
4. remove_supernatant_96_well.py - aspirates supernatant after centrifuging silica beads into a 96-well plate.

#### [Protocol Generator](/Team_3/generate_protocol.py)

User inputs of concentrations of components and supplements, final volume desired in each well and number of wells. The script randomly allocates wells to these conditions.

The protocol has been optimised for varying/combining 2 components and 2 supplements i.e. 6 conditions, components (C) ex: c1=glucose and c2=gluconate, supplements (S) ex: S1=vitamin A and S2=vitamin B, components are in mM and supplements mg/ml. The control is the component without the supplement.

#### [Template for protocol generation](/Team_3/protocol_template.py)

1. The first step is making master mixes for each condition with available stock in the lab. - script uses user-defined conditions, volumes and concentrations from generate_protocol.py - user action requires placing of relevant media and labware in relevant positions specified in script - script prepares the volumes needed for each condition mastermix and stores in reservoir.
2. The conditions are then pipetted randomly across the wells to ensure there is no possibility of position bias in the assay. - The generate_protocol.py script generates a well-map for the random conditions to ensure random well locations are known to the user. - The wells are then incubated with cells manually. The inoculated wells can then be transferred into 2ml glass vials if using methanogenic bacteria (as used by Noah Sprent)

#### [Simulation Cell Culture Transfer](/Team_3/silicabeads.py)

This will transfer 200ul of grown cell cultures from a 96-well plate into another 96-well plate, this plate will then be centrifuged. For this step, we simulated cells using silica beads.

#### [Supernatant Removal](/Team_3/remove_supernatant_96_well.py)

This file allows for the supernatant removal of the centrifuged plate. We ensured to add a slow aspiration speed and low Z value to ensure that the pellet of cells is not disturbed when aspirating the supernatant. This supernatant can then be analysed in a plate reader to measure fluorescence such as GFP.

### Conclusion

The aim of this project and the attached files is to automate the generation of a randomised 96-well plate layout for OpenTron 2. When implementing our code the above can be completed. Given time constraints the supernatant removal step in 4. was optimised to the best of our abilities. Given more time we would test shifting the angle of the multi-tip pipettes to aspirate the supernatant away from the pellet. This would allow for better aspiration and less disruption of the pellet.
