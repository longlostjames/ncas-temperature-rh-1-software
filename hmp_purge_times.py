#!/usr/local/anaconda3/envs/chil_3_8/bin/python

# =========================================================================
# hmp_purge_times
# Plots 6 days T and RH data from HMP155 T/RH sensor to identify purge times 
#
# Author:        Judith Jeffery, RAL 
# Version:	 0.1
# Created: 12/05/2020 
# =========================================================================

import getopt, sys
#This makes it possible to produce plots without an X window, e.g. from a cronjob
#Needs to be in here, not just in any function that's imported
import matplotlib as mpl
#mpl.use('Agg')	#This is needed if you want to run code e.g. as a cronjob, but otherwise it stops a plot being produced on the screen!
import numpy as np
import os, re, sys, getopt, shutil, zipfile, string, pwd
import netCDF4 as nc4

import datetime
import time
import calendar
import scipy.signal
from pylab import *
import matplotlib.pyplot as plt

# Respond to key press by ending click options
def onkey(event):
    print('Key pressed')
    #rect = patches.Rectangle((50,100),40,30,linewidth=1,edgecolor='r',facecolor='none')
    #ax.add_patch(rect)
    fig.canvas.mpl_disconnect(bid)
    plt.close(1)
    return

# -------------------------
# Explain function usage
# Needs to be before main()
# -------------------------
def usage():

    print("\n")
    print("Command line structure")
    print("./hmp_purge_times_display.py -s yyyymmdd (of start day) -x spacing of days (default 5), -f minimum time on graph (default 9 hours)")

# ------------------------------------------------------------------------
#def main():
# ------------------------------------------------------------------------

#startday = ''
#sensor = ''

if len(sys.argv) <= 1:	#no arguments provided
    usage()
    sys.exit(2)
try:
    #opts, args = getopt.getopt(sys.argv[1:], "hs:x:", ["startday=", "sensor=", "help"])
    opts, args = getopt.getopt(sys.argv[1:], "hs:x:f:")
    print(getopt.getopt(sys.argv[1:], "hs:x:f:"))
except getopt.GetoptError as err:
    # print help information and exit:
    print("In except function, ", str(err)) # will print something like "option -a not recognized"
    usage()	#Need a usage function, typically print statements
    sys.exit(2)


# --------------
# Default values 
# --------------
tinc = 5	#Spacing between days 
min_x_val = 9.0	#Minimum time on x-axis

# --------------------
# Command line parsing
# --------------------
for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--startday"):
            #startday = int(a)
            startday = str(a)
        elif o in ("-x", "--sensor"):
            #endday = int(a)
            tinc = int(a)
        elif o in ("-f"):
            min_x_val = float(a)
        else:
            assert False, "unhandled option"

print("start day: ", startday)
print("Time increment: ", tinc) 

startnum = int(date2num(datetime.datetime(int(startday[0:4]),int(startday[4:6]),int(startday[6:8]),0,0,0)))
print("start day, number: ", startday, startnum)

#file_path = '/data/amof-netCDF/diagnostics/ncas-nocorr-temperature-rh-1/'
file_path = '/data/amof-netCDF/ncas-temperature-rh-1/'
out_plot_file = '/data/amof-netCDF/diagnostics/hmp_plots/hmp_plot_' + startday +'.png'
colval = ['k', 'r', 'g', 'b', 'c', 'm']

#fig = plt.figure(1, figsize = (5,8))
fig, (ax1, ax2) = plt.subplots(2, figsize = (6,8))

for nn in range(6):

    nday = startnum + nn * tinc
    ndat             = num2date(nday)
    year             = ndat.year
    month            = ndat.month
    day              = ndat.day
    dat              = datetime.datetime(year,month,day,0,0,0)
    datestring       = dat.strftime("%Y%m%d")


    print("Date = ",datestring)

    #file_in = 'ncas-nocorr-temperature-rh-1_cao_' + datestring + '_surface-met_v1.0.nc'
    file_in = 'ncas-temperature-rh-1_cao_' + datestring + '_surface-met_v1.0.nc'
    file_in = file_path + file_in
    plot_file = '/home/jla/hmp_plots/hmp_purge_' + datestring + '.png'
    ncfile = nc4.Dataset(file_in, 'r',format='NETCDF4_CLASSIC')
    ncfile.set_auto_maskandscale(False)
    var_time = ncfile.variables['time']
    var_time = (var_time - var_time[0])/3600.0
    n_points = var_time.size
    #print n_points,var_time[0:9]
    x_axis_title = 'Time (hours since midnight)'
    
    temp_var_y = ncfile.variables['air_temperature']
    air_temperature = temp_var_y[:]
    temp_var_y = ncfile.variables['relative_humidity']
    relative_humidity = temp_var_y[:]

    ncfile.close()

    im = ax1.plot(var_time, air_temperature, colval[nn], linewidth = 1)
    #ax1.set_xlim(9.8, 10.3)
    ax1.set_xlim(min_x_val, (min_x_val + 0.5))
    ax1.set_title(startday + ' Blk Red Grn Blu Cyn Mag')
    ax1.set_ylabel('Temperature (K)')
    ax1.grid(True, which='major', axis='x')

    im = ax2.plot(var_time, relative_humidity, colval[nn], linewidth = 1)
    #ax2.set_xlim(9.8, 10.3)
    ax2.set_xlim(min_x_val, (min_x_val + 0.5))
    ax2.set_xlabel(x_axis_title)
    ax2.set_ylabel('RH (%)')
    ax2.grid(True, which='major', axis='x')
    #ax = fig.add_subplot(211)
    #ax.plot(var_time, air_temperature, colval[nn], linewidth=1)
    #ax.set_xlim(9.8, 10.3)
    ##ax.set_ylim(265.0, 285.0)
    #ax.set_title(startday + ' Blk Red Grn Blu Cyn Mag')
    #ax.set_ylabel('Temperature (K)')
    #ax = fig.add_subplot(212)
    #ax.plot(var_time, relative_humidity, colval[nn], linewidth=1)
    #ax.set_xlim(9.8, 10.3)
    #ax.set_xlabel(x_axis_title)
    #ax.set_ylabel('RH (%)')

bid = fig.canvas.mpl_connect('key_press_event', onkey)

#plt.show(1)
plt.show()
#plt.savefig(out_plot_file,format='png')






# ------------------------------------------------------------------------
# Define the general netcdf generation function, common to all sensors
# ------------------------------------------------------------------------
def generate_netcdf_common(nday):

    # -----------------------------
    # Date-time numbers and strings
    # -----------------------------
    ndat             = num2date(nday)
    year             = ndat.year
    month            = ndat.month
    day              = ndat.day
    dat              = datetime.datetime(year,month,day,0,0,0)
    nowdat           = datetime.datetime.now()
    nowstring        = nowdat.strftime("%Y-%m-%d %H:%M:%S")
    datestring       = dat.strftime("%Y%m%d")
    start_of_day_str = dat.strftime("%Y-%m-%d %H:%M")

    return year,month,day,datestring,start_of_day_str,nowstring


