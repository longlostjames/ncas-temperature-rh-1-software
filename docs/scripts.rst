Scripts Reference
=================

This section provides detailed documentation for each script in the NCAS Temperature RH-1 Software package.

Data Processing Scripts
-----------------------

process_hmp155.py
~~~~~~~~~~~~~~~~~

Convert raw Campbell Scientific CR1000X data files to CF-compliant NetCDF format.

**Command Line Arguments:**

.. code-block:: text

   usage: process_hmp155.py [-h] [-m METADATA] [-o OUTPUT] input_file

   positional arguments:
     input_file            Input CR1000X DAT file

   optional arguments:
     -h, --help            Show help message and exit
     -m METADATA           Metadata JSON file (default: metadata.json)
     -o OUTPUT             Output directory (default: current directory)

**Features:**

* Reads Campbell Scientific TOA5 format files
* Applies variable scaling and offsets from metadata
* Initializes QC flags to 0 (not used)
* Writes CF-compliant NetCDF with proper time encoding
* Handles timezone conversion to UTC

**Example:**

.. code-block:: bash

   python process_hmp155.py CR1000X_Chilbolton_Rxcabinmet1_20200115.dat \
       -m metadata.json \
       -o /gws/pw/j07/ncas_obs_vol2/cao/2020/

split_cr1000x_data_daily.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Split continuous CR1000X datalogger files into daily files organized by year and month.

**Command Line Arguments:**

.. code-block:: text

   usage: split_cr1000x_data_daily.py [-h] -i INPUT_DIR -o OUTPUT_DIR [-v]

   optional arguments:
     -h, --help            Show help message and exit
     -i INPUT_DIR          Input directory containing CR1000X files
     -o OUTPUT_DIR         Output directory for daily files
     -v                    Verbose output

**Features:**

* Processes all CR1000X_Chilbolton_Rxcabinmet1*.dat files in input directory
* Creates YYYY/YYYYMM directory structure
* Shifts midnight records to previous day
* Deduplicates identical files for the same date
* Preserves TOA5 4-line header format
* Quotes timestamp column

**Example:**

.. code-block:: bash

   python split_cr1000x_data_daily.py \
       -i /path/to/continuous/files \
       -o /gws/pw/j07/ncas_obs_vol2/cao/ \
       -v

Quality Control Scripts
-----------------------

flag_purge_times.py
~~~~~~~~~~~~~~~~~~~

Automatically detect and flag purge cycles and recovery periods in NetCDF files.

**Command Line Arguments:**

.. code-block:: text

   usage: flag_purge_times.py [-h] -f FILE [-p PREV_FILE]
                              [--corr_file_temperature CORR_FILE_TEMPERATURE]
                              [--corr_file_rh CORR_FILE_RH]

   optional arguments:
     -h, --help            Show help message and exit
     -f FILE               NetCDF file to process
     -p PREV_FILE          Previous day's NetCDF file for continuity
     --corr_file_temperature CORR_FILE_TEMPERATURE
                           Text file with temperature correction intervals
     --corr_file_rh CORR_FILE_RH
                           Text file with RH correction intervals

**Detection Parameters:**

* Window size: 8 minutes (240 seconds)
* Temperature flat threshold: 0.07 K standard deviation
* RH flat threshold: 0.03 % standard deviation
* RH exclusion: Values ≥ 99.8%
* Recovery period: 6 minutes after purge end

**QC Flag Values:**

* 1: Good data
* 2: Bad data (from correction files)
* 3: Purge cycle
* 4: Recovery period (RH only)

**Example:**

.. code-block:: bash

   python flag_purge_times.py \
       -f ncas-temperature-rh-1_cao_20200115_surface-met_v1.0.nc \
       -p ncas-temperature-rh-1_cao_20200114_surface-met_v1.0.nc \
       --corr_file_temperature temp_bad_intervals.txt

manual_flag_purge_times.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Manually flag purge cycles based on previous day's purge times or explicit intervals.

**Command Line Arguments:**

.. code-block:: text

   usage: manual_flag_purge_times.py [-h] -f FILE [--prev-file PREV_FILE]
                                     [--shift-seconds SHIFT_SECONDS]
                                     [-s START] [-e END]
                                     [--clear-purge-flags]

   optional arguments:
     -h, --help            Show help message and exit
     -f FILE               NetCDF file to process
     --prev-file PREV_FILE Previous day's file to copy purge times from
     --shift-seconds SHIFT_SECONDS
                           Time shift to apply to purge times (default: 0.0)
     -s START              Start time of purge interval (can be repeated)
     -e END                End time of purge interval (can be repeated)
     --clear-purge-flags   Clear existing purge flags before applying new ones

**Features:**

* Copies purge times from previous day's file
* Applies time-of-day matching (ignores date)
* Supports time shift adjustment
* Allows explicit purge interval specification
* Flags both temperature and RH QC flags as 3

**Example:**

.. code-block:: bash

   # Use previous day's purge times
   python manual_flag_purge_times.py \
       -f today.nc \
       --prev-file yesterday.nc \
       --shift-seconds 0.0

   # Specify explicit intervals
   python manual_flag_purge_times.py \
       -f today.nc \
       -s "2020-01-15 12:00:00" -e "2020-01-15 12:08:00" \
       -s "2020-01-15 18:00:00" -e "2020-01-15 18:08:00"

flag_low_temperature.py
~~~~~~~~~~~~~~~~~~~~~~~~

Flag temperature values below a threshold as bad data.

**Command Line Arguments:**

.. code-block:: text

   usage: flag_low_temperature.py [-h] -f FILE [--threshold THRESHOLD]

   optional arguments:
     -h, --help            Show help message and exit
     -f FILE               NetCDF file to process
     --threshold THRESHOLD Temperature threshold in Kelvin (default: 245)

**Features:**

* Flags both air_temperature and relative_humidity QC flags
* Default threshold: 245 K (-28.15 °C)
* Sets QC flag value to 2 (bad data)

**Example:**

.. code-block:: bash

   python flag_low_temperature.py -f data.nc --threshold 240

Visualization Scripts
---------------------

make_quicklooks.py
~~~~~~~~~~~~~~~~~~

Generate daily quicklook plots showing temperature, humidity, and QC flags.

**Command Line Arguments:**

.. code-block:: text

   usage: make_quicklooks.py [-h] -i INPUT_DIR -o OUTPUT_DIR -y YEAR -d DAY

   optional arguments:
     -h, --help            Show help message and exit
     -i INPUT_DIR          Input directory containing NetCDF files
     -o OUTPUT_DIR         Output directory for PNG plots
     -y YEAR               Year (YYYY)
     -d DAY                Day (YYYYMMDD)

**Plot Features:**

* Temperature displayed in degrees Celsius
* Full-day overview plot
* Zoomed plots for each purge period
* Color-coded QC flag visualization:
  
  * Red dots/shading: Purge cycles (flag 3)
  * Blue dots/peachpuff shading: RH recovery (flag 4)
  * Grey shading: Bad data (flag 2)

* No duplicate legend entries
* Overlapping flag intervals combined

**Example:**

.. code-block:: bash

   python make_quicklooks.py \
       -i /gws/pw/j07/ncas_obs_vol2/cao/ \
       -o /path/to/plots/ \
       -y 2020 \
       -d 20200115

boxplot_temperature.py
~~~~~~~~~~~~~~~~~~~~~~

Generate daily or weekly temperature boxplot summaries for a year.

**Command Line Arguments:**

.. code-block:: text

   usage: boxplot_temperature.py [-h] -y YEAR [-f {daily,weekly}]

   optional arguments:
     -h, --help            Show help message and exit
     -y YEAR               Year (YYYY)
     -f {daily,weekly}     Frequency: daily or weekly (default: daily)

**Features:**

* Reads from YYYY subdirectory structure
* Filters out bad data (QC flag 2)
* Converts temperature to Celsius
* Default input directory: /gws/pw/j07/ncas_obs_vol2/cao/

**Example:**

.. code-block:: bash

   # Daily boxplots
   python boxplot_temperature.py -y 2020 -f daily

   # Weekly boxplots
   python boxplot_temperature.py -y 2020 -f weekly

Utility Scripts
---------------

find_purge_shift.py
~~~~~~~~~~~~~~~~~~~

Calculate the time-of-day shift between purge cycles in two NetCDF files.

**Command Line Arguments:**

.. code-block:: text

   usage: find_purge_shift.py file1 file2

   positional arguments:
     file1                 First NetCDF file
     file2                 Second NetCDF file

**Features:**

* Reports shift in seconds with microsecond precision
* Compares only time-of-day (ignores date)
* Uses first purge period from each file

**Example:**

.. code-block:: bash

   python find_purge_shift.py yesterday.nc today.nc

count_purge_flags.py
~~~~~~~~~~~~~~~~~~~~

Count the number of purge flag occurrences in a NetCDF file.

**Example:**

.. code-block:: bash

   python count_purge_flags.py data.nc

Batch Processing
----------------

proc_year.sh
~~~~~~~~~~~~

Shell script to process an entire year of data sequentially.

**Usage:**

.. code-block:: text

   ./proc_year.sh YEAR [CORR_FILE_TEMP] [CORR_FILE_RH]

**Arguments:**

* YEAR: Four-digit year to process
* CORR_FILE_TEMP: Optional temperature correction file
* CORR_FILE_RH: Optional RH correction file

**Workflow:**

1. Loops through all dates in the specified year
2. Processes each day with process_hmp155.py
3. Applies QC flags with flag_purge_times.py
4. Uses previous day's file for continuity
5. Skips processing if output file already exists

**Example:**

.. code-block:: bash

   # Process without corrections
   ./proc_year.sh 2020

   # Process with correction files
   ./proc_year.sh 2020 temp_corrections.txt rh_corrections.txt
