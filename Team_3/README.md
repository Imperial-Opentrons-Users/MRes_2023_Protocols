# Team 3

## Generating 96-well plate randomised layout from predefined media conditions for growing and monitoring the efficiency of carbon sequestering bacterial cells, through a plate reader assay.

### Introduction

We took Noah Sprent's protocol for growing and monitoring the efficiency of carbon-sequestering bacterial cells. The original protocol is fully automated using a Hamilton Robot, our objective was to extract key steps and demonstrate the OpenTrons 2's capabilities as a cheaper, more accessible substitute.

### File Overview

In this submission file, you will find 4 python files. These scripts help you generate a randomised plate with growth medium and nutrients to measure cell growth and then a final step to remove supernatant to measure in a plate reader.

The steps and subsequent files are:

1. generate_protocol.py - The user inputs desired conditions, concentrations, volumes and number of wells needed for the assay, the code will calculate the master needed for each condition and assign random wells to each condition
2. protocol_template.py - prepares master mixes and pipettes respective conditions into randomised wells predefined from generate_protocol.py
3. silicabeads.py - plates 200ul of cell culture into 96 well plate for centrifugation
4. supernatant_aspirate_speed.py - aspirates supernatant after centrifuging silica beads into a 96-well plate.

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
