init = input("Do you want to do larvae sample prep + PCR [1] or PCR only [2]? (Type 1 or 2 to choose)")

if int(init) == 1:
    scriptname = 'OT2-1_mosquito_pcr_script.py'
if int(init) == 2:
    scriptname = 'OT2-1_mosquito_pcr_only_script.py'

while (int(init) != 1) and (int(init) != 2):
    init = input("ERROR: Please input larvae sample prep [1] + PCR or PCR only [2]")

# Prompt user input to enter anneal temperature
anneal_temp = input("Please input desired annealing temperature (Celsius): ")

while anneal_temp.isnumeric() == False: # Check if user input is a number
    anneal_temp = input("ERROR: Please input annealing temperature (Celsius): ")

# Prompt user input to enter product length (kb) to calculate extension time
extension_time = input("Please input PCR extension time (seconds): ")

while extension_time.isnumeric() == False: # Check if user input is a number
    extension_temp = input("ERROR: Please input a number extension time (seconds): ")

# Extract lines of main script
with open(scriptname, 'r') as file:
    script = file.readlines()

# Modify new anneal temp
if int(init) == 1:
    script[79] = '    anneal_temp = ' + anneal_temp + '\n'

    # Modify new extension time
    script[81] = '    extension_time = ' + str(extension_time) + '\n'

if int(init) == 2:
    script[57] = '    anneal_temp = ' + anneal_temp + '\n'

    # Modify new extension time
    script[59] = '    extension_time = ' + str(extension_time) + '\n'

name = input('Input file name without extension: ')

# Overwrite new input into file
with open(name+'.py', 'w') as file:
    file.writelines(script)
