NCAS Temperature RH-1 Software Documentation
============================================

This software package processes data from Vaisala HMP155A temperature and humidity sensors and related meteorological instruments at the Chilbolton Atmospheric Observatory (CAO).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   scripts
   api
   contributing

Overview
--------

The NCAS Temperature RH-1 Software provides a suite of tools for:

* Processing raw sensor data to CF-compliant NetCDF files
* Quality control flagging (purge cycles, bad data intervals)
* Data visualization (quicklooks, boxplots)
* Daily file splitting and deduplication

Key Features
------------

* **Data Processing**: Convert raw Campbell Scientific CR1000X data to standardized NetCDF format
* **Quality Control**: Automated detection of purge cycles and manual flagging capabilities
* **Visualization**: Generate daily quicklook plots and statistical summaries
* **Batch Processing**: Shell scripts for processing entire years of data

Quick Start
-----------

Process a single day of data:

.. code-block:: bash

   python process_hmp155.py input_data.dat -m metadata.json -o output_dir/

Flag purge cycles in processed NetCDF files:

.. code-block:: bash

   python flag_purge_times.py -f data.nc -p previous_day.nc

Generate quicklook plots:

.. code-block:: bash

   python make_quicklooks.py -y 2020 -d 20200115

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
