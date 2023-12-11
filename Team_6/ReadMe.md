# Single Cell Whole Genome Multiple Displacement Amplification

### Authors: Ryan Sze, Warren Ho, Raymond Cole Hautamaki, Elephes Sung 宋範新, Natasha Kisseroudis

The project aims to achieve Opentron automation of whole genome Multiple Displacement Amplification (MDA) in single cells, 
a method of non-specific DNA amplification using random hexamer primers and the phi29 DNA polymerase. These Scripts are 
designed to streamline the MDA protocol by introducing automation.

### Source:

Automated protocol adapted from Spits et al. (2006).

### Protocol Description:

The MDA protocol consists of 3 stages— a sample preparation stage, a DNA amplification stage, and a purification stage.
Our team has automated the protocol with 4 scripts total due to the limited space in the Opentron deck. The temperature modules, 
magnetic modules, and thermocycler are unable to be plugged in at the same time.

We have 2 Executable Scripts and 2 Simulation Scripts: 
1) The Sample_prep script runs first and automates the protocol's sample prep/MDA part. This involves the preparation and mixing 
of the reagents (enzymes and buffers) with the DNA sample, followed by the amplification reaction done inside the thermocycler.
2) The DNA_purification script runs afterwards and automates the purification part to isolate high-quality DNA from the amplification. Quantification of DNA concentration is meant to be done via Nanodrop. 

The protocol is designed to amplify at most 8 samples (but aim to use at least 1 positive/negative control) due to equipment 
constraints; the p20-single can be swapped out for a p20-multi to handle more samples. The results of the purification will
be located in column 2 of the well plate on the magnetic deck. 

### Labware Setup:

![0D45A1DCF5FC4FEB88225B149194CEFC](https://github.com/Imperial-Opentrons-Users/MRes_2023_Protocols/assets/152276516/2dfdde93-1dfa-4efa-87b8-e488bcb00ce2)

### Notes and Preparation:

1) Make sure to calibrate the Opentron, particularly the Z-axis, on both scripts separately.
2) When conducting the wet runs, the correct temperatures and incubation times were not used as they took too long, and no 
reagents/enzymes were actually being used.
3) We deleted the step for single-cell picking. Single-cell samples are assumed to be isolated by previous manual procedures—
for example, FACS or MACS. Ensure they are located in column 1 of the PCR plate inside the thermocycler. 

-------------------
