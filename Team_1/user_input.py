init = input("Do you want to do larvae sample prep + PCR [1] or PCR only [2]? (Type 1 or 2 to choose)")

while (init.isnumeric() == False) or ((int(init) != 1) and (int(init) != 2)):
    init = input("ERROR: Please input larvae sample prep [1] + PCR or PCR only [2]")

if int(init) == 1:
    scriptname = 'OT2-1_mosquito_pcr_script.py'
elif int(init) == 2:
    scriptname = 'OT2-1_mosquito_pcr_only_script.py'

# Prompt user input to enter anneal temperature
anneal_temp = input("Please input desired annealing temperature (between 4ºC - 99ºC): ")

while (anneal_temp.isnumeric() == False) or ((4 > int(anneal_temp)) or (99 < int(anneal_temp))): # Check if user input is a number
    anneal_temp = input("ERROR: Please input annealing temperature (between 4ºC - 99ºC): ")

# Prompt user input to enter product length (kb) to calculate extension time
extension_time = input("Please input PCR extension time (seconds): ")

while (extension_time.isnumeric() == False) or (int(extension_time) <= 0):
    extension_time = input("ERROR: Please input an extension time (> 0 seconds): ")

# Extract lines of main script
with open(scriptname, 'r') as file:
    script = file.readlines()

# Modify new anneal temp
if int(init) == 1:
    script[140] = '    anneal_temp = ' + anneal_temp + '\n'

    # Modify new extension time
    script[141] = '    extension_time = ' + str(extension_time) + '\n'

elif int(init) == 2:
    script[84] = '    anneal_temp = ' + anneal_temp + '\n'

    # Modify new extension time
    script[85] = '    extension_time = ' + str(extension_time) + '\n'

name = input('Input file name without extension: ')

# Overwrite new input into file
with open(name+'.py', 'w') as file:
    file.writelines(script)