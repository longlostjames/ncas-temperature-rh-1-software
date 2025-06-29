#!/bin/bash

# Default values
year=""

# Parse command line options
while getopts "y:" opt; do
    case $opt in
        y) year="$OPTARG" ;;
        *)  
            echo "Usage: $0 -y <year>"
            exit 1
            ;;
    esac
done

# Check if year is provided
if [ -z "$year" ]; then
    echo "Error: Year (-y) is required."
    echo "Usage: $0 -y <year>"
    exit 1
fi

# Base directory for raw data
raw_data_base="/gws/pw/j07/ncas_obs_vol2/cao/raw_data/legacy/chao-analog-format5_chilbolton/data/long-term/format5"

# Date range for the given year
start_date="${year}0101"
end_date="${year}1231"

# Activate conda environment
source ~/anaconda3/etc/profile.d/conda.sh  # or wherever your conda is installed
conda activate cao_3_11

current_date=$start_date
while [ "$current_date" -le "$end_date" ]; do

    YMD=$(date -d "$current_date" +%y%m%d)
    outdir="/gws/pw/j07/ncas_obs_vol2/cao/processing/ncas-temperature-rh-1/data/long-term/level1/$year"

    mkdir -p "$outdir"

    # Calculate the previous day's date
    previous_date=$(date -d "$current_date - 1 day" +%Y%m%d)
    previous_year=$(date -d "$current_date - 1 day" +%Y)

    # Construct paths to the current and previous day's files
    infile="$raw_data_base/chan${YMD}.000"

    mfile="/home/users/cjwalden/git/ncas-temperature-rh-1-software/metadata.json"

    # Run the Python script
    python ~/git/ncas-temperature-rh-1-software/process_hmp155_f5.py "$infile" \
               -m "$mfile" -o "$outdir"

        # Path to the generated NetCDF file
    ncfile="$outdir/ncas-temperature-rh-1_cao_${current_date}_surface-met_v1.0.nc"

    # Add QC flags for purge times
    if [ -f "$ncfile" ]; then
        if [ -z "$previous_ncfile" ]; then
            # No previous file for the first day
            python ~/git/ncas-temperature-rh-1-software/flag_purge_times.py -f "$ncfile"
        else
            # Use the previous day's file for consistency checks
            python ~/git/ncas-temperature-rh-1-software/flag_purge_times.py -f "$ncfile" -p "$previous_ncfile"
        fi
        # Update the previous file to the current file
        previous_ncfile="$ncfile"
    else
        echo "Warning: NetCDF file $ncfile not found. Skipping QC flagging."
    fi

    current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
done
