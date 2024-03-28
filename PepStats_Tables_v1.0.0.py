#!/usr/bin/env python3
import platform
import os
import sys
import shutil
import argparse
import subprocess
import tempfile
import datetime
import locale
import re
from textwrap import dedent
from packaging import version

# Defining Script Name
script_name = os.path.basename(sys.argv[0])

# Defining Script Current Version
script_version = "1.0.0"

# Defining_Script_Initial_Version_Data (date '+DATE:%Y/%m/%d%tTIME:%R')
version_date_initial = "DATE:2021/07/17   TIME:00:00"

# Defining_Script_Current_Version_Data (date '+DATE:%Y/%m/%d%tTIME:%R')
version_date_current = "DATE:2024/02/21   TIME:15:58"

copyright = dedent("""
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.  """)

authors = dedent("""
Author:                            Rodolfo Aramayo
WORK_EMAIL:                        raramayo@tamu.edu
PERSONAL_EMAIL:                    rodolfo@aramayo.org
""")

usage = dedent(f"""
########################################################################################################################################################################################################
ARAMAYO_LAB
{copyright}

SCRIPT_NAME:                      {script_name}
SCRIPT_VERSION:                   {script_version}

USAGE: {script_name}
       -p Homo_sapiens.GRCh38.pep.all.fa               # REQUIRED (Proteins File - Proteome)
       -r PepStats_Tables                              # OPTIONAL (Run Name)
       -z TMPDIR Location                              # OPTIONAL (default=0='TMP TMPDIR Run')

TYPICAL COMMANDS:
                                   {script_name} -p Homo_sapiens.GRCh38.pep.all.fa -r PepStats_Tables

INPUT01:          -p FLAG          REQUIRED - Protein File
INPUT01_FORMAT:                    Fasta Format
INPUT01_DEFAULT:                   No default

INPUT02:          -r FLAG          OPTIONAL - Run Name
INPUT02_FORMAT:                    Text
INPUT02_DEFAULT:                   PepStats_Tables

INPUT03:          -z FLAG          OPTIONAL input
INPUT03_FORMAT:                    Numeric: 0 == TMP TMPDIR Run | 1 == Local TMP Run
INPUT03_DEFAULT:                   0 == TMP TMPDIR Run
INPUT03_NOTES:                     0 Processes the data in the TMP $TMPDIR directory of the computer used or of the node assigned by the SuperComputer scheduler
INPUT03_NOTES:                     Processing the data in the $TMPDIR directory of the node assigned by the SuperComputer scheduler reduces the possibility of file error generation due to network traffic
INPUT03_NOTES:                     1 Processes the data in the same directory where the script is being run

DEPENDENCIES:                      EMBOSS:        Required (see: http://emboss.open-bio.org/html/adm/ch01s01.html)

{authors}
########################################################################################################################################################################################################
""")
# print (usage)

def error_handling_function():
    print("An error occurred. Invoking the error handling function.")
    print (usage)
    sys.exit(1)

def setup_argparse():
    parser = argparse.ArgumentParser(
      description='Script Description and Usage',
      formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
      '-p', '--proteome',
      required=True,
      help='Proteins File - Proteome'
    )
    parser.add_argument(
      '-r',
      '--run_name',
      default='PepStats_Tables',
      help='Optional Run Name'
    )
    parser.add_argument(
      '-z',
      '--tmp_dir',
      type=int,
      choices=[0, 1],
      default=0,
      help='TMPDIR Location (0 for TMP TMPDIR Run, 1 for Local TMPDIR Run)'
    )
    parser.add_argument(
      '-v',
      '--version',
      action='version',
      version=f'%(prog)s {script_version}',
      help='Show program\'s version number and exit'
    )
    return parser

# Check if no arguments were provided
if len(sys.argv) == 1:
    print("\nPlease enter required arguments")
    print (usage)
    sys.exit(1)

def main():
    parser = setup_argparse()

    args = parser.parse_args()  # This line parses the command-line arguments

    # Test print argument names and their values
    # print("Entered command-line arguments and values:")
    # for arg in vars(args):
    #     print(f"{arg}: {getattr(args, arg)}")

    # Extract and print the name of the protein file
    proteome_file_name = os.path.basename(args.proteome)
    # print(f"Proteome File Name: {proteome_file_name}") # test_print_var

    proteome, _ = os.path.splitext(proteome_file_name)
    # print(f"Proteome Name: {proteome}") # test_print_var

    run_name = os.path.basename(args.run_name)
    # print(f"Run name: {run_name}") # test_print_var

    tmp_dir = (args.tmp_dir)
    # print(f"TMP dir: {tmp_dir}") # test_print_var

    # Construct the directory path
    current_working_directory = os.getcwd()
    # print(f"Current Working Directory:", current_working_directory) # test_print_var

    current_working_directory_path = os.path.dirname(current_working_directory)
    # print(f"Directory Path: {current_working_directory_path}") # test_print_var

    working_directory_name = f"{proteome_file_name}_{run_name}.dir"
    # print(f"Working Directory Name: {working_directory_name}") # test_print_var

    # Check if the working directory exists
    if not os.path.isdir(working_directory_name):
        # If the directory does not exist, create it
        os.makedirs(working_directory_name)
    else:
        # If the directory exists, remove its contents
        for filename in os.listdir(working_directory_name):
            file_path = os.path.join(working_directory_name, filename)
            try:
                # If it's a file, remove it
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                # If it's a directory, remove it and all its contents
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    def generate_or_clean_tmp_directory(proteome, run_name, tmp_dir):
        global var_script_tmp_data_dir
        if tmp_dir == 0:
            # Use system TMPDIR if defined, else use a temporary directory
            base_dir = os.getenv('TMPDIR', None)
            if base_dir is not None:
                # TMPDIR is defined; create a temp directory there
                var_script_tmp_data_dir = tempfile.mkdtemp(prefix=f"{proteome_file_name}_{run_name}_", dir=base_dir)
            else:
                # TMPDIR not defined; create a temp directory using default location
                var_script_tmp_data_dir = tempfile.mkdtemp(prefix=f"{proteome_file_name}_{run_name}_")

            # print(f"Temporary directory created at: {var_script_tmp_data_dir}") # test_print_var

        elif tmp_dir == 1:
            # Define the script TMP data directory path
            var_script_tmp_data_dir = os.path.join(os.getcwd(), f"{proteome_file_name}_{run_name}.tmp")

            # Check if the directory exists
            if not os.path.exists(var_script_tmp_data_dir):
                os.makedirs(var_script_tmp_data_dir)
            else:
                # Move and rename the existing directory before creating a new one
                new_dir_name = f"{var_script_tmp_data_dir}_{datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
                os.rename(var_script_tmp_data_dir, new_dir_name)
                os.makedirs(var_script_tmp_data_dir)

            # print(f"Temporary directory created at: {var_script_tmp_data_dir}") # test_print_var

    generate_or_clean_tmp_directory(proteome, run_name, tmp_dir)

    # Define the directory and log file path
    log_dir = f"./{proteome_file_name}_{run_name}.dir"
    log_file_path = os.path.join(log_dir, f"{proteome_file_name}_{run_name}.log")

    # Ensure the directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Initialize log file and record start time
    time_execution_start = datetime.datetime.now()

    # Writing the starting entry to the log file
    with open(log_file_path, 'w') as log_file:
      log_file.write(f"Starting Processing Proteome: {proteome_file_name} on: {time_execution_start}\n")

    # Function to append messages to the log file
    def append_to_log(message):
        with open(log_file_path, 'a') as log_file:
          log_file.write(message + "\n")

    # Verifying Software Dependency Existence
    append_to_log(f"Verifying Software Dependency Existence on: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Determining Current Computer Platform
    osname = platform.system()
    cputype = platform.machine()
    plt = ""
    if osname == "Linux" and cputype == "x86_64":
      plt = "Linux"
    elif osname == "Darwin" and cputype == "x86_64":
      plt = "Darwin"
    elif osname == "Darwin" and "arm" in cputype:
      plt = "Silicon"
    elif "CYGWIN_NT" in osname or "MINGW" in osname:
      plt = "CYGWIN_NT"
    elif osname == "Linux" and "arm" in cputype:
      plt = "ARM"

    append_to_log(f"Operational System: {osname}")
    append_to_log(f"CPU TYPE: {cputype}")
    append_to_log(f"Detected Platform: {plt}")

    # Determining Python Version (as a stand-in for checking Bash version)
    python_version = platform.python_version()
    required_version = "3.6"  # Example required version

    append_to_log(f"Available Python Version: {python_version}")
    append_to_log(f"Required Minimal Python Version: {required_version}")

    if version.parse(python_version) >= version.parse(required_version):
      append_to_log(f"Python version {python_version} is installed.")
    else:
      append_to_log(f"Python version 3.6 or higher is not installed.")
      append_to_log(f"Please install Python version 3.6 or higher.")
      # Exit the script if the required Python version is not installed
      sys.exit(1)

    # Check for pepstats installation
    def check_dependency(command):
        #original_path = os.environ['PATH']
        #os.environ['PATH'] += os.pathsep + '/opt/local/bin'  # Ensure this is the correct path for pepstats
        result = subprocess.run(["which", command], capture_output=True, text=True)
        #os.environ['PATH'] = original_path  # Reset PATH to original value
        return result.returncode == 0

    # Append dependency check results to log
    if check_dependency("pepstats"):
      append_to_log(f"PepStats is Installed")
    else:
      append_to_log(f"EMBOSS pepstats is Not Installed")
      print (usage)
      # Handle the error as needed, perhaps by calling a custom `func_usage` function or exiting
      sys.exit("Please install EMBOSS PepStats.")

    # Logging platform information
    append_to_log(f"Software Dependencies Verified on: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    append_to_log(f"Script Running on: {osname}, {cputype}")

    # Setting LC_ALL to "C"
    os.environ["LC_ALL"] = "C"  # Affects child processes
    locale.setlocale(locale.LC_ALL, 'C')  # Affects the current Python process

    # Writing command issued and other details to the log
    append_to_log(f"\nCommand Issued Was: {script_name} -p {proteome} -r {run_name} -z {tmp_dir}")
    append_to_log(f"\tProteome Analyzed:\t{proteome_file_name}")
    append_to_log(f"\tFile Type:\t\tProteome")

    # Conditionally writing TMPDIR information based on tmp_dir
    if tmp_dir == 0:
        append_to_log(f"\tTMPDIR Requested:\tNormal Run")
        append_to_log(f"\tTMPDIR Created at:\t{var_script_tmp_data_dir}")
    else:
        append_to_log(f"\tTMPDIR Requested:\tLocal TMPDIR Run")
        append_to_log(f"\tTMPDIR Created at:\t{var_script_tmp_data_dir}")

    # Construct the output file path
    output_file_path = os.path.join(var_script_tmp_data_dir, f"001_{proteome}.out")

    # Check if the file does not exist or is empty
    if not os.path.isfile(output_file_path) or os.path.getsize(output_file_path) == 0:
    # Construct the pepstats command
        pepstats_command = [
            "pepstats",
            "-sequence", f"{proteome_file_name}",
            "-outfile", output_file_path
        ]

    # Execute the command, suppressing stderr
    with open(os.devnull, 'w') as devnull:
        subprocess.run(pepstats_command, stderr=devnull)

    # File and file paths
    file_001 = os.path.join(var_script_tmp_data_dir, f"001_{proteome}.out")
    file_002 = os.path.join(var_script_tmp_data_dir, f"002_{proteome}.out")
    file_003 = os.path.join(var_script_tmp_data_dir, f"003_{proteome}.out")
    file_004 = os.path.join(var_script_tmp_data_dir, f"004_{proteome}.out")
    file_005 = os.path.join(var_script_tmp_data_dir, f"005_{proteome}.out")
    file_006 = os.path.join(var_script_tmp_data_dir, f"006_{proteome}.out")
    file_007 = os.path.join(var_script_tmp_data_dir, f"007_{proteome}.out")
    file_008 = os.path.join(var_script_tmp_data_dir, f"008_{proteome}.out")

    # Define regex patterns for each condition
    patterns = [
        (re.compile(r"PEPSTATS"), 3),
        (re.compile(r"Molecular weight"), 4),
        (re.compile(r"Isoelectric Point ="), -1),
        (re.compile(r"A = Ala"), 5),
        (re.compile(r"C = Cys"), 4),
        (re.compile(r"D = Asp"), 4),
        (re.compile(r"E = Glu"), 4),
        (re.compile(r"F = Phe"), 4),
        (re.compile(r"G = Gly"), 4),
        (re.compile(r"H = His"), 4),
        (re.compile(r"A = Ala"), 4),
        (re.compile(r"I = Ile"), 4),
        (re.compile(r"K = Lys"), 4),
        (re.compile(r"L = Leu"), 4),
        (re.compile(r"M = Met"), 4),
        (re.compile(r"N = Asn"), 4),
        (re.compile(r"P = Pro"), 4),
        (re.compile(r"Q = Gln"), 4),
        (re.compile(r"R = Arg"), 4),
        (re.compile(r"S = Ser"), 4),
        (re.compile(r"T = Thr"), 4),
        (re.compile(r"V = Val"), 4),
        (re.compile(r"W = Trp"), 4),
        (re.compile(r"Y = Tyr"), 4),
        (re.compile(r"Tiny"), -1),
        (re.compile(r"Small"), -1),
        (re.compile(r"Aliphatic"), -1),
        (re.compile(r"Aromatic"), -1),
        (re.compile(r"Non-polar"), -1),
        (re.compile(r"Polar"), -1),
        (re.compile(r"Charged"), -1),
        (re.compile(r"Basic"), -1),
        (re.compile(r"Acidic"), -1),
    ]

    nl = False

    with open(file_001, 'r') as input_file, open(file_002, 'w') as output_file:
        for line in input_file:
            for pattern, field_index in patterns:
                if pattern.search(line):
                    words = line.split()
                    if nl:
                        output_file.write("\n")
                    else:
                        nl = True

                    # Handle the case where field_index is -1 (i.e., use the last field)
                    if field_index == -1:
                        field_index = len(words)
                    output_file.write(f"{words[field_index - 1]} ")
                    break  # Move to the next line after a match

        # Print a final newline at the end of the file
        output_file.write("\n")

    # Format and combine data from file_002 and file_001 into file_003
    # Number of lines in each entry, including the identifier line
    lines_per_entry = 32

    def process_file(file_002, file_003):
        with open(file_002, 'r') as input_file, open(file_003, 'w') as output_file:
            # Initialize a counter to track the number of lines processed for the current entry
            line_count = 0
            # Initialize a list to accumulate lines for the current entry
            current_entry_lines = []

            for line in input_file:
                # Strip leading/trailing whitespace
                line = line.strip()
                # Skip empty lines if they are not expected within an entry
                if not line:
                    continue

                # Add the current line to the entry's lines
                current_entry_lines.append(line)
                line_count += 1

                # Check if we've accumulated all lines for the current entry
                if line_count == lines_per_entry:
                    # Join the lines with a tab separator and write to the output file
                    output_file.write('\t'.join(current_entry_lines) + '\n')
                    # Reset the counter and the list for the next entry
                    line_count = 0
                    current_entry_lines = []

            # Handle the last entry if the file doesn't end with a full set of lines_per_entry
            # This step may be unnecessary if each entry is guaranteed to have exactly lines_per_entry lines
            if current_entry_lines:
                output_file.write('\t'.join(current_entry_lines) + '\n')

    process_file(file_002, file_003)

    # Create a header row and write it to file_004
    header = "Protein_ID\tMolecular_weight\tIsoelectric_Point\t" \
              "Mole%_Ala\tMole%_Cys\tMole%_Asp\tMole%_Glu\tMole%_Phe\tMole%_Gly\tMole%_His\tMole%_Ile\tMole%_Lys\tMole%_Leu\t" \
              "Mole%_Met\tMole%_Asn\tMole%_Pro\tMole%_Gln\tMole%_Arg\tMole%_Ser\tMole%_Thr\tMole%_Val\tMole%_Trp\tMole%_Tyr\t" \
              "Mole%_Tiny\tMole%_Small\tMole%_Aliphatic\tMole%_Aromatic\tMole%_Non-polar\tMole%_Polar\tMole%_Charged\tMole%_Basic\tMole%_Acidic\n"
    with open(file_004, 'w') as f_header:
        f_header.write(header)

    # Concatenate file_004 and file_003 into file_005
    with open(file_005, 'w') as f_final, open(file_004, 'r') as f_header, open(file_003, 'r') as f_data:
        f_final.write(f_header.read())
        f_final.write(f_data.read())

    def transpose_entries(file_002, file_006, lines_per_entry):
        # Read all lines from the input file and group them
        with open(file_002, 'r') as file:
            lines = file.read().strip().split('\n')

        # Group every lines_per_entry lines into an entry
        entries = [lines[i:i + lines_per_entry] for i in range(0, len(lines), lines_per_entry)]

        # Transpose the list of entries
        transposed = list(zip(*entries))

        # Write the transposed lines to the output file, separating entries with tabs
        with open(file_006, 'w') as file:
            for line_group in transposed:
                file.write('\t'.join(line_group) + '\n')

    transpose_entries(file_002, file_006, lines_per_entry)

        # Create a column row and write it to file_007
    column = "Protein_ID\nMolecular_weight\nIsoelectric_Point\n" \
              "Mole%_Ala\nMole%_Cys\nMole%_Asp\nMole%_Glu\nMole%_Phe\nMole%_Gly\nMole%_His\nMole%_Ile\nMole%_Lys\nMole%_Leu\n" \
              "Mole%_Met\nMole%_Asn\nMole%_Pro\nMole%_Gln\nMole%_Arg\nMole%_Ser\nMole%_Thr\nMole%_Val\nMole%_Trp\nMole%_Tyr\n" \
              "Mole%_Tiny\nMole%_Small\nMole%_Aliphatic\nMole%_Aromatic\nMole%_Non-polar\nMole%_Polar\nMole%_Charged\nMole%_Basic\nMole%_Acidic\n"
    with open(file_007, 'w') as f_column:
        f_column.write(column)

    # Open file_008 for writing, and file_007 and file_006 for reading
    with open(file_008, 'w') as f_final, open(file_007, 'r') as f_header, open(file_006, 'r') as f_data:
        # Iterate over the lines of file_007 and file_006 simultaneously
        for header_line, data_line in zip(f_header, f_data):
            # Strip newline characters and concatenate the lines with a tab in between
            combined_line = header_line.strip() + '\t' + data_line.strip() + '\n'
            # Write the combined line to file_008
            f_final.write(combined_line)

    main_pepstats_run = os.path.join(log_dir, f"{proteome_file_name}_{run_name}.00_Main_PepStats_Analysis")
    table_01_pepstats_run = os.path.join(log_dir, f"{proteome_file_name}_{run_name}.01_PepStats_Table_01")
    table_02_pepstats_run = os.path.join(log_dir, f"{proteome_file_name}_{run_name}.02_PepStats_Table_02")

    shutil.move(file_001, main_pepstats_run)
    shutil.move(file_005, table_01_pepstats_run)
    shutil.move(file_008, table_02_pepstats_run)

    # Remove the TMPDIR directory and all its contents
    shutil.rmtree(var_script_tmp_data_dir)

    # Record stop time and calculate duration
    time_execution_stop = datetime.datetime.now()
    execution_duration_seconds = (time_execution_stop - time_execution_start).total_seconds()
    execution_duration_minutes = execution_duration_seconds / 60
    execution_duration_hours = execution_duration_minutes / 60

    # Writing the closing entry to the log file
    with open(log_file_path, 'a') as log_file:  # Open in append mode to add to the file
      log_file.write(f"\nFinishing Processing proteome {proteome} on: {time_execution_stop}\n")
      log_file.write(f"Script Runtime: {execution_duration_seconds} seconds\n")
      log_file.write(f"Script Runtime: {execution_duration_minutes:.2f} minutes\n")
      log_file.write(f"Script Runtime: {execution_duration_hours:.2f} hours\n")

if __name__ == "__main__":
    main()
