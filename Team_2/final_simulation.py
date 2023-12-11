#will output a python file that can be run using simulation mode
import pandas as pd
import os
from tkinter import Tk, Label, StringVar, OptionMenu, Entry, Button, messagebox, Frame

def get_valid_directory():
    while True:
        directory_path = input("Enter the full path to the directory: ")
        if os.path.isdir(directory_path):
            return directory_path
        else:
            print("Invalid directory. Please enter a valid path.")

# Function to cherry-pick top samples based on user input
def cherry_pick_top_samples(df, num_samples_to_pick, sort_column, ascending):
    # Sort the DataFrame based on the specified column and order
    df_sorted = df.sort_values(by=sort_column, ascending=ascending)

    # Cherry-pick the top samples
    top_samples = df_sorted.head(num_samples_to_pick)

    return top_samples

# Callback function for running the protocol
def run_protocol(directory_path, combined_df, sort_column, source_column, 
                 blank_wells_input, blank_wells_specs, blanking_request, 
                 sort_choice, num_samples_to_pick, min_value, max_value, 
                 num_duplicates, destination_blanks_input, new_script_name):
    global df  # Access the global DataFrame

    if blank_wells_input == 'yes':

        # Convert the user input into a list of tuples containing plate number and well name
        blank_wells_list = [(int(entry.split(':')[0]), entry.split(':')[1].strip().upper()) for entry in blank_wells_specs.split(',')]

        if blanking_request == 'yes':
            # Blank correct the samples on each plate
            def blank_correct_samples(combined_df, blank_wells_list, source_column, sort_column):
                # Create a key column for comparison with blank_wells_list
                combined_df_key = combined_df[['plate_num', source_column, sort_column]]
                combined_df_key['key'] = combined_df_key.apply(lambda row: (row['plate_num'], row[source_column]), axis=1)

                # Separate blanks for each plate number and calculate the average
                for plate_num, well_name in blank_wells_list:
                    plate_blanks = combined_df[(combined_df['plate_num'] == plate_num) & (combined_df[source_column] == well_name)]
                    
                    # Check if there are blanks for averaging
                    if not plate_blanks.empty:
                        avg_blank_value = plate_blanks[sort_column].mean()

                        # Subtract the average blank value from the rest of the values
                        combined_df.loc[(combined_df['plate_num'] == plate_num) & (combined_df[source_column] != well_name), sort_column] -= avg_blank_value

                # Ensure result values are non-negative
                combined_df[sort_column] = combined_df[sort_column].apply(lambda x: max(0, x))

                # Remove rows corresponding to blank wells
                combined_df = combined_df[~combined_df_key['key'].isin(blank_wells_list)]

                return combined_df

            # Apply blank correction function
            if blank_wells_list:
                combined_df = blank_correct_samples(combined_df, blank_wells_list, source_column, sort_column)
        

        elif blanking_request == 'no':
            # Remove blanks function
            def remove_blanks(combined_df, blank_wells_list, source_column, sort_column):
                # Create a key column for comparison with blank_wells_list
                combined_df_key = combined_df[['plate_num', source_column, sort_column]]
                combined_df_key['key'] = combined_df_key.apply(lambda row: (row['plate_num'], row[source_column]), axis=1)

                # Remove rows corresponding to blank wells
                combined_df = combined_df[~combined_df_key['key'].isin(blank_wells_list)]

                return combined_df

            if blank_wells_list:
                combined_df = remove_blanks(combined_df, blank_wells_list, source_column, sort_column)

    elif blank_wells_input == 'no':
        pass

    #sort_column = sort_column_var.get()
    #source_column = source_column_var.get()
    #sort_choice = sort_choice_entry.get()

    if sort_choice == 'minimum':
        # Ask the user for the number of top samples to pick
        #num_samples_to_pick = int(input("Enter the number of top samples to pick: "))
        ascending = True
        # Cherry-pick the top samples with user-defined sorting
        top_samples = combined_df.nsmallest(num_samples_to_pick, sort_column, 'all')

    elif sort_choice == 'maximum':
        # Ask the user for the number of top samples to pick
        #num_samples_to_pick = int(input("Enter the number of top samples to pick: "))
        ascending = False
        # Cherry-pick the top samples with user-defined sorting
        top_samples = combined_df.nlargest(num_samples_to_pick, sort_column, 'all')

    elif sort_choice == 'range':
        # Ask the user for the range values
        min_value = float(min_value_entry.get())
        max_value = float(max_value_entry.get())
        top_samples = combined_df[(combined_df[sort_column] >= min_value) & (combined_df[sort_column] <= max_value)]
        num_samples_to_pick = len(top_samples)
        ascending = True  # Adjust the sorting order as needed

    # Cherry-pick the top samples with user-defined sorting
    top_samples = top_samples.sort_values(by=sort_column, ascending=ascending).head(num_samples_to_pick)

    # Duplicate each row based on the user input
    duplicated_samples = top_samples.loc[top_samples.index.repeat(num_duplicates)]

    # Check if the number of duplicated samples is greater than 96
    if len(duplicated_samples) > 96:
        print("Error: The number of duplicated samples exceeds the capacity of a 96-well plate.")

    destination_blanks_list = [well.strip().upper() for well in destination_blanks_input.split(',')]

    # Create a new column with the specified pattern (A1-A12, B1-B12, C1-C12, ...)
    pattern = [f'{chr(65 + i)}{j}' for i in range(26) for j in range(1, 13)]

    if destination_blanks_list:
        pattern = [well for well in pattern if well not in destination_blanks_list]

    # Check if the number of duplicated samples is greater than the available pattern
    if len(duplicated_samples) > len(pattern):
        raise ValueError("Error: The number of duplicated samples exceeds the available well pattern.")

    duplicated_samples['Dest_Well'] = pattern[:len(duplicated_samples)]

   # Ask the user for the new file name
    new_file_name = new_script_name + "_layout.csv"
    duplicated_samples.to_csv(new_file_name, index=False)
    print(f"Plate Layout saved to {new_file_name} and Python script saved to {new_script_name}")


    # Generate the new Python script (Code B)
    new_script_name = new_script_name + ".py"
    
    
    with open(new_script_name, 'w') as script_file:
        script_file.write("# This script was generated based on Code A\n")
        script_file.write("from opentrons import simulate\n")
        script_file.write("\n")
        script_file.write("# set up opentrons\n")
        script_file.write("metadata = {'apiLevel': '2.15'}\n")
        script_file.write("\n")
        script_file.write("protocol = simulate.get_protocol_api('2.15')")
        script_file.write("\n")
        script_file.write("# Load CSV file with source and destination well information\n")
        script_file.write(f"repeats = {num_duplicates}\n")
        script_file.write(f"data = {duplicated_samples.to_dict(orient='list')}\n")
        script_file.write("\n")
        script_file.write("# Stripping leading zeros after the letter")
        script_file.write("\n")               
        script_file.write("data['Well'] = [well[0] + well[1:].lstrip('0') if well[1] == '0' else well for well in data['Well']]")
        script_file.write("\n") 
        script_file.write("# Define pipette and tiprack\n")
        script_file.write("tiprack_1 = protocol.load_labware(\"opentrons_96_tiprack_300ul\", \"1\")  # Adjust the tip rack type as needed\n")
        script_file.write("tiprack_2 = protocol.load_labware(\"opentrons_96_tiprack_300ul\", \"2\")\n")
        script_file.write("pipette = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_1, tiprack_2])\n")
        script_file.write("\n")
        script_file.write("# (Add your specific labware and instrument definitions here)\n")
        script_file.write("# Deep well 96-well plate for growth\n")
        script_file.write("cherrypicked_96 = protocol.load_labware('thermoscientificnunc_96_wellplate_1300ul', '3')\n")
        script_file.write("\n")
        script_file.write("# Find the maximum plate number\n")
        script_file.write("max_plate_number = max(data['plate_num'])\n")
        script_file.write("\n")
        script_file.write("# Define the source plates\n")
        script_file.write("source_plates = {}\n")
        script_file.write("\n")
        script_file.write("for plate_number in range(1, max_plate_number + 1):\n")
        script_file.write("  source_plate = protocol.load_labware('thermoscientificnunc_96_wellplate_1300ul', "
                           "str(plate_number + 3))  # Adjust the labware type and location\n")
        script_file.write("  source_plates[plate_number] = source_plate\n")
        script_file.write("\n")
        script_file.write("# Counter to keep track of retained tips\n")
        script_file.write("tip_counter = 0\n")
        script_file.write("pipette.pick_up_tip()\n")
        script_file.write("\n")
        script_file.write("for index, row in enumerate(data['Well']):\n")
        script_file.write("  source_well = row\n")
        script_file.write("  dest_well = data['Dest_Well'][index]\n")
        script_file.write("  plate_number = data['plate_num'][index]\n")
        script_file.write("\n")
        script_file.write("# Check if the tip should be changed\n")
        script_file.write("  if tip_counter == repeats:\n")
        script_file.write("    if pipette.has_tip:\n")
        script_file.write("        pipette.drop_tip()\n")
        script_file.write("    pipette.pick_up_tip()\n")
        script_file.write("    tip_counter = 0  # Reset the counter\n")
        script_file.write("\n")
        script_file.write("# Perform liquid transfer\n")
        script_file.write("  if plate_number in source_plates:\n")
        script_file.write("     pipette.transfer(50, source_plates[plate_number].wells(source_well), cherrypicked_96.wells(dest_well), "
                           "blow_out=True, blowout_location='destination well', touch_tip=True, new_tip='never')\n")
        script_file.write("     tip_counter += 1  # Increment the counter\n")
        script_file.write("  else:\n")
        script_file.write("     print(f\"Error: Source plate for Plate_Number {plate_number} is not defined.\")\n")
        script_file.write("\n")
        script_file.write("# Drop the final tip after the last transfer\n")
        script_file.write("pipette.drop_tip()\n")
        script_file.write("\n")
        script_file.write("for line in protocol.commands():\n")
        script_file.write(" print(line)")
    

    pass

def on_button_click():
    global df  
    
    directory_path = get_valid_directory()
    os.chdir(directory_path)
    
    while True:
        try:
            num_files = int(input("Enter the number of CSV files to add: "))
            break  # Exit the loop if the input is a valid integer
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
    
    # Initialize an empty list to store DataFrames
    dfs = []

    for i in range(1, num_files + 1):
        while True:
            file_name = input(f"Enter the name of CSV file {i} (including the extension): ")

            # Check if the file exists in the specified directory
            if os.path.isfile(file_name):
                break  # Exit the loop if the file exists
            else:
                print(f"File '{file_name}' not found in the directory. Please enter a valid file name.")

        file_df = pd.read_csv(file_name)
        file_df['plate_num'] = i
        dfs.append(file_df)

    # Combine the DataFrames into one
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Get unique column names from the concatenated DataFrame
    column_names = combined_df.columns.tolist()
    
    root = Tk()
    root.title("Cherry Picker")

    # Labels, entry widgets, and buttons for user inputs
    Label(root, text="Select the column to use for sorting:").grid(row=0, column=0)
    sort_column_var = StringVar(root)
    sort_column_var.set("")  # Set default value to an empty string
    sort_column_menu = OptionMenu(root, sort_column_var, "")
    sort_column_menu.grid(row=0, column=1)
    OptionMenu(root, sort_column_var, *column_names).grid(row=0, column=1)

    Label(root, text="Select the column to use for source wells:").grid(row=1, column=0)
    source_column_var = StringVar(root)
    source_column_var.set("")  # Set default value to an empty string
    source_column_menu = OptionMenu(root, source_column_var, "")
    source_column_menu.grid(row=1, column=1)
    OptionMenu(root, source_column_var, *column_names).grid(row=1, column=1)

    Label(root, text="Do you have blanks? (yes/no):").grid(row=2, column=0)
    blank_wells_input_entry = Entry(root)
    blank_wells_input_entry.grid(row=2, column=1)

    Label(root, text="List the blank wells (e.g., 1:A1, 2:A10):").grid(row=3, column=0)
    blank_wells_specs_entry = Entry(root)
    blank_wells_specs_entry.grid(row=3, column=1)

    Label(root, text="Do you want to blank correct the data? (yes/no):").grid(row=4, column=0)
    blanking_request_entry = Entry(root)
    blanking_request_entry.grid(row=4, column=1)

    Label(root, text="Do you want to sort data based on minimum, maximum, or a range?").grid(row=5, column=0)
    sort_choice_var = StringVar(root)
    sort_choice_var.set("")  # Set default value to an empty string
    OptionMenu(root, sort_choice_var, "minimum", "maximum", "range").grid(row=5, column=1)

    # Entry for range values (hidden initially)
    range_frame = Frame(root)
    range_frame.grid(row=6, column=0, columnspan=2, sticky='w')

    range_frame_label = Label(range_frame, text="Enter the range values:")
    range_frame_label.grid(row=0, column=0)

    min_value_entry = Entry(range_frame)
    min_value_entry.grid(row=0, column=1)

    max_value_entry = Entry(range_frame)
    max_value_entry.grid(row=0, column=2)

    def show_hide_range_entries():
        if sort_choice_var.get() == "range":
            range_frame.grid()
        else:
            range_frame.grid_remove()

    # Button to trigger the show/hide functionality
    Button(root, text="Update Range Entries", command=show_hide_range_entries).grid(row=7, column=0, columnspan=2)

    Label(root, text="Enter the number of samples to pick:").grid(row=8, column=0)
    num_samples_to_pick_entry = Entry(root)
    num_samples_to_pick_entry.grid(row=8, column=1)

    Label(root, text="Enter the number of times to duplicate each sample:").grid(row=9, column=0)
    num_duplicates_entry = Entry(root)
    num_duplicates_entry.grid(row=9, column=1)

    Label(root, text="Do you want to include blanks in your destination plate? If yes, list the wells:").grid(row=10, column=0)
    destination_blanks_input_entry = Entry(root)
    destination_blanks_input_entry.grid(row=10, column=1)

    Label(root, text="Enter the new Python script/csv file name:").grid(row=11, column=0)
    new_script_name_entry = Entry(root)
    new_script_name_entry.grid(row=11, column=1)

    # Button to trigger the protocol setup
    Button(root, text="Create Opentron Script and Layout File", command=lambda: run_protocol(
        directory_path,
        combined_df,
        sort_column_var.get(),
        source_column_var.get(),
        blank_wells_input_entry.get(),
        blank_wells_specs_entry.get(),
        blanking_request_entry.get(),
        sort_choice_var.get(),
        int(num_samples_to_pick_entry.get()),
        float(min_value_entry.get()) if sort_choice_var.get() == 'range' else None,
        float(max_value_entry.get()) if sort_choice_var.get() == 'range' else None,
        int(num_duplicates_entry.get()),
        destination_blanks_input_entry.get(),
        new_script_name_entry.get()
    )).grid(row=12, column=0, columnspan=2)

    root.mainloop()

# Entry point for the script
on_button_click()
