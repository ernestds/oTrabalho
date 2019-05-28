# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 11:24:28 2019

@author: ernesto.saraiva
"""
2
from LTX_Lib import *
import numpy as np
import pandas as pd
import win32com.client
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import os

#Defines para os dados dos strain gauges
def styleForChannel(channel):
    if "-A" in channel:
        return '-'
    if "-T" in channel:
        return '--'
    if "-O" in channel:
        return '-.'

#nesse caso as janelas sao SG120,  as cores variam de acordo com A-, B-, M-
separationList = [["SG120","SG240","SG0"],["-A","-T","-O"], ['A-','B-','M-']]
namesDict = {"SG120":"Strain Gauge at 120º","SG240":"Strain Gauge at 240º","SG0":"Strain Gauge at 0º",
                 "-A":"Strain Gauge Orientation: Axial","-T":"Strain Gauge Orientation: Transversal","-O":"Strain Gauge Orientation: 45º"}


timeUnit = "h"
thisPath = os.path.dirname(os.path.abspath(__file__)) + '\\'
Data = testData(thisPath, timeUnit = timeUnit)
testName =  "BURST RT 01 - FAT01 Without Seal"

print(Data.channels)
print(Data.units)

channelList = []
xaxisList = ['elapsedTime','elapsedTime','elapsedTime','elapsedTime','elapsedTime'
             ,'elapsedTime','elapsedTime','elapsedTime','elapsedTime','elapsedTime',
             'elapsedTime','elapsedTime','elapsedTime','elapsedTime','elapsedTime']
#%%
for index, channel in enumerate(channelList):
    fig, ax = plt.subplots()
    plotString = "ax.plot(Data(" + xaxisList[i]+ "), Data('"+ channel +"'))"
    exec(plotString)
    l33tFunc(fig,plotString, index + 1)
    
pausepls
#%%
fig, ax = plt.subplots(nrows=1,sharex=True)
ax2 = ax.twinx()
fig.suptitle("Burst 01 - FAT Without Seal", fontsize=16)

Data.plot(ax,'SDP-16 - Length', label = 'Axial Displacement', unit = 'h', color = 'C3')
Data.plot(ax2,'Pressure - SP-27', label = 'Pressure', unit = 'h', color = 'C2')

ax.set_xlabel("Time (hours)")
ax.set_ylabel("Displacement (mm)")
ax2.set_ylabel("Pressure (bar)")

ax.set_ylim([0,10])
ax2.set_ylim([280,330])
alignYAxis(ax, 0, ax2, 280)
alignTicks(ax,ax2)
ax.set_xlim([0,25])
#ax.xaxis.set_major_locator(ticker.MaxNLocator(min_n_ticks=15))
#ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator())

ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
ax2.yaxis.set_major_locator(ticker.MultipleLocator(5))

ax.grid()
#ax.grid(b=True, which='major', axis='both', alpha = 0.5, color = (.1,.1,0.1))

joinLegends(ax,ax2)
ax.annotate('Final Pressure: 312 bar',(12.7,4.1))
ax.annotate('Final Displacement: 9.79 mm',(12.7,3.1))

def click(event):
    x, y = event.xdata, event.ydata
    width = event.canvas.get_width_height()[0]
    heigth = event.canvas.get_width_height()[1]
    print("data: " + str((x,y)) + " abs: " + str((event.x/width,event.y/heigth)))
#    print(event.canvas.size())
    fig = event.canvas.figure

fig.canvas.mpl_connect('button_press_event', click)

fig.set_size_inches(15, 9)
fig.savefig(string1,dpi=150)
#%%
for string1 in separationList[0]:
    fig, ax = plt.subplots(nrows=1,sharex=True)
    fig.suptitle(testName, fontsize=16)
    
    for string2 in separationList[1]:
        j = 0
        for string3 in separationList[2]:
            channel = Data.selectChannels(string1,string2,string3)[0]
            Data.plot(ax,channel, linestyle=styleForChannel(channel), color = [(.75,0,0),(0,.75,0),(0,0,.75)][j])
            j = j+1
    

    ax.xaxis.set_major_locator(ticker.MaxNLocator(min_n_ticks=15))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(b=True, which='both', axis='both', alpha = 0.5)
    ax.grid(b=True, which='major', axis='both', alpha = 0.5 ,linewidth = 1 )
    
    ax2 = ax.twinx()
    ax2.fill_between(Data('elapsedTime'), 0,Data('Pressure - SP-27'),alpha = 0.2, label ='Pressure - SP-27' )
    ax2.set_ylim(-75,500)
    ax.set_ylim(bottom = -0.1)
    alignYAxis(ax, 0, ax2, 0)
    alignTicks(ax,ax2)
    joinLegends(ax,ax2, loc='upper right')
    
