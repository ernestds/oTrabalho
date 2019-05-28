# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 09:18:28 2019

@author: ernesto.saraiva
"""
import numpy as np
import pandas as pd
import win32com.client
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import time
import io
import os
import datetime
import uuid
import math
import MySQLdb as SQL
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import keyboard  # using module keyboard

def l33tFunc(fig,plotString, index):
    i  = index
#    execString = """Data.plot(ax,'"""+ xaxis +"""','"""+ yaxis + """',unit = '""" + unit + """')"""
    execString = plotString
#    print(execString)
    totalString = """\"\"\"
fig, ax = plt.subplots()
"""+ execString + """
ax.set_xlim([\"\"\" + str(posStart[0][0]) + ", " + str(posStart[1][0]) + \"\"\"])
ax.set_ylim([\"\"\" + str(posStart[0][1]) + ", " + str(posStart[1][1]) + \"\"\"])
#ax.set_ylabel('Deslocamento [mm]')
#ax.set_xlabel('Tempo [segundos]') 

#alignYAxis(ax, 0, ax2, 280)
#alignTicks(ax,ax2)
#ax.set_xlim([0,25])
#ax.xaxis.set_major_locator(ticker.MaxNLocator(min_n_ticks=15))
#ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator())

#ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
#ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
#ax2.yaxis.set_major_locator(ticker.MultipleLocator(5))

#ax.grid()
#ax.grid(b=True, which='major', axis='both', alpha = 0.5, color = (.1,.1,0.1))

#joinLegends(ax,ax2)
\"\"\""""
    
#    fig, ax = plt.subplots()
#    exec(execString)
#    ax.grid()
    posStart = []
    scope = locals()
    #fazer tmb coordenadas do axes
    exec("""
import keyboard  # using module keyboard
def mouse_press(event):
    global posStart
    width = event.canvas.get_width_height()[0]
    heigth = event.canvas.get_width_height()[1]
    index = int(""" + str(index) + """)
    xdata, ydata = event.xdata, event.ydata
    xabs, yabs = event.x, event.y
    xrel, yrel = event.x/width, event.y/heigth
             
    if keyboard.is_pressed('control'):
        print("Figure " + str(index)+" pos@Data: " + str((xdata,ydata)) + " posRel@Fig: " + str((xrel,yrel)))
                 
    if keyboard.is_pressed('shift'):
        posStart.append([xdata,ydata])
        if len(posStart)==2:
            if  (posStart[0][0]) >  (posStart[1][0]):
                print('trocando x')
                temp =  posStart[0][0]
                posStart[0][0] = posStart[1][0]
                posStart[1][0] = temp
            if  (posStart[0][1]) >  (posStart[1][1]):
                temp =  posStart[0][1]
                posStart[0][1] = posStart[1][1]
                posStart[1][1] = temp
            print("Code figure " + str(index)+ ":")
            print("-----------------------------------------------------")
            print(""" + totalString + """)
            print("-----------------------------------------------------")
            print("posições dos dois pontos @ data: " + str(posStart))
            posStart = []
                     
    #print(event.canvas.size())
    fig = event.canvas.figure
    """, scope)
#    print(scope)
#    a.append(click)
    fig.canvas.mpl_connect('button_press_event', scope['mouse_press'])
    
def scopeMouse(fig):
    def mouse_press(event):
        global posStart
        width = event.canvas.get_width_height()[0]
        heigth = event.canvas.get_width_height()[1]
        xdata, ydata = event.xdata, event.ydata
        xabs, yabs = event.x, event.y
        xrel, yrel = event.x/width, event.y/heigth
        print("Figure pos@Data: " + str((xdata,ydata)) + " posRel@Fig: " + str((xrel,yrel)))
    fig.canvas.mpl_connect('button_press_event', mouse_press)

def joinLegends(ax2,ax, **kwargs):
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.figure.legend(h1+h2, l1+l2,  **kwargs)
    
def alignTicks(ax2,ax):
    l = ax2.get_ylim()
    l2 = ax.get_ylim()
    f = lambda x : l2[0]+(x-l[0])/(l[1]-l[0])*(l2[1]-l2[0])
    ticks = f(ax2.get_yticks())
    ax.yaxis.set_major_locator(ticker.FixedLocator(ticks))
    
def alignYAxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
    miny, maxy = ax2.get_ylim()
    ax2.set_ylim(miny+dy, maxy+dy)
    


    
def selectChannels(validChannels,*arg):
    a = [element for element in validChannels if arg[0] in element]
    arg2 = arg[1:]
    for word in arg2:
        a = [element for element in a if word in element]
    return list(a)

def getDataFrame(path,fileString="", frequency = 0):
    LynxFile = win32com.client.Dispatch("LynxFile.FileTS");
    filesWithZList = (glob.glob(path+fileString+"*Z*.LTX"))
    filesList = (glob.glob(path+fileString+"*.LTX"))
    files = [element for element in filesList if element not in filesWithZList]
    allData = pd.DataFrame()
    validChannels = {}
    print('Arquivos abertos:')
    for file in files:
        print(file)
        df = pd.DataFrame()
        LynxFile.OpenFile(file)
        frequency = LynxFile.SampleFreq
        
        for i in range(LynxFile.nChannels):
                channelName = LynxFile.SnName(i)
                validChannels[channelName] = i
                Buf = np.zeros(LynxFile.nSamples)
                r,Buf,NOut = LynxFile.ReadBuffer(i, 0, LynxFile.nSamples, Buf)
                df[channelName] = Buf
        
        if df.empty:
            print('WARNING: ' + file + ' vazio')
        else:
            timestamped = False
            for item in validChannels.items():
                timestamped = ('Timestamp High' in item) or timestamped
            if timestamped:
                
                timeHighStart = np.zeros(1)
                timeHighEnd = np.zeros(1)
                timeLowStart = np.zeros(1)
                timeLowEnd = np.zeros(1)
                
                r,timeHighStart,NOut = LynxFile.ReadBuffer(validChannels['Timestamp High'],0,1,timeHighStart)
                r,timeHighEnd,NOut = LynxFile.ReadBuffer(validChannels['Timestamp High'],LynxFile.nSamples -1 ,1,timeHighEnd)
                r,timeLowStart,NOut = LynxFile.ReadBuffer(validChannels['Timestamp Low'],LynxFile.nSamples -1 ,1,timeLowStart)
                r,timeLowEnd,NOut = LynxFile.ReadBuffer(validChannels['Timestamp Low'],LynxFile.nSamples -1 ,1,timeLowEnd)
                
                df['UnixTime'] = df['Timestamp High'] + 1.0/1000000000.0 *df['Timestamp Low']
            
                df['date'] = pd.to_datetime(df['UnixTime'],unit='s')
                
            else:
                df['UnixTime'] = np.nan;
                df['UnixTime'][-1:] = (len(df.index) - 1) / frequency 
                df['UnixTime'][0] = 0
                df['UnixTime'] = df['UnixTime'].interpolate()
            
            allData = allData.append(df, ignore_index = True)
        
    
#    print(LynxFile.nSamples)
    if allData.empty:
        pass
    else:
        allData['elapsedTime'] = allData['UnixTime']-df['UnixTime'][0]
        allData['elapsedTime'] = allData['elapsedTime']
    return allData, validChannels, LynxFile
    
class testData:
    """ 
    afsd
    """
    timeMultipliers = {"s":1,"m":1.0/60.00,"h":1.0/3600.0,"d":1.0/3600.0/24.0}
    timeUnit = ''
    def __init__(self, path, fileString = "", timeUnit = "s", frequency = 0):
        self.dfOrig, self.validChannels, self.LynxFile = getDataFrame(path,fileString, frequency = frequency)
        self.units = {}
        self.channels = []
        self.df = self.dfOrig.copy()
        for name,value in self.validChannels.items():
            self.channels.append(name)
            self.units[name] = self.LynxFile.SnUnit(value)
            if self.units[name] == "µm/m":
                self.df[name] = self.df[name] * 10**-6 * 100
                self.units[name] = "%"
            if self.units[name] == "mm/m":
                self.df[name] = self.df[name] * 10**-3 * 100
                self.units[name] = "%"
            if self.units[name] == "m/m":
                self.df[name] = self.df[name] * 10**1 * 100
                self.units[name] = "%"
        self.timeUnit = timeUnit
        self.timeOffset = 0
    def setTimeOffset(self,timeOffset,unit = None):
        if unit==None:
            unit = self.timeUnit
        temp  = self.df['elapsedTime'].copy(deep = True) - self.timeOffset + timeOffset / self.timeMultipliers[unit]
        self.df['elapsedTime'] = temp.copy(deep = True)
        self.timeOffset = timeOffset / self.timeMultipliers[unit]
    def cutInterval(self,initialTime=-999999,endTime=999999,unit = None):
        if unit==None:
            unit = self.timeUnit
        self.df = self.df[self.df['elapsedTime'] > initialTime / self.timeMultipliers[unit]]
        self.df = self.df[self.df['elapsedTime'] < endTime / self.timeMultipliers[unit]]
        
    def setOriginalDF(self):
        self.df = self.dfOrig.copy(deep = True)
        self.timeOffset = 0
    def __call__(self,*arg2,initialTime = -99999, endTime = 999999,unit = None, offset = 0):
        if unit==None:
            unit = self.timeUnit
        arg = arg2[:]
        arg = list(arg)
        tempdf = self.df[arg[0]]
        tempdf = tempdf[self.df['elapsedTime'] > initialTime / self.timeMultipliers[unit]]
        tempdf = tempdf[self.df['elapsedTime'] < endTime / self.timeMultipliers[unit]]
        if arg[0] == 'elapsedTime':
            return tempdf*self.timeMultipliers[unit] + offset
        else:
            return tempdf
                    
    def selectChannels(self,*arg):
        a = [element for element in self.channels if arg[0] in element]
        arg2 = arg[1:]
        for word in arg2:
            a = [element for element in a if word in element]
        return a
    
    def writeToTxt(self, channels = None,unit = None,fileName = 'data.txt', separator = '\t', digits = 7):
        if unit == None:
            unit = self.timeUnit
        if channels == None:
            channels = self.channels
        df2 = pd.DataFrame()
        df2['elapsedTime'] = self('elapsedTime',unit = unit)
        unitsString = unit + separator
        headerString = 'time\t'
        for channel in channels:
            df2[channel] = self(channel)
            unitsString = unitsString + separator + self.units[channel]
            headerString = headerString + separator + channel
        headerString = headerString + '\n'
        unitsString = unitsString + '\n'
        bio = io.BytesIO()
        np.savetxt(bio, df2.values, delimiter = separator, fmt='%1.' + str(digits) + 'f')
        mystr = bio.getvalue().decode('latin1')
        text_file = open(fileName, "w")
        text_file.write(headerString + unitsString + mystr)
        text_file.close()
    
    def plot(self, axis ,x1,  x2 = None,unit = None,fmt = None, label = None, **kwargs):
        ''' teste'''
        if unit == None:
            unit = self.timeUnit
        if label == None:
            if x2 == None:
                label = x1
            else:
                label = x2
                
        #example :Data.plot(ax,'Input Pres - SP-19', label = 'Input Pres - SP-19', fmt = 'r-')
        if fmt == None:
            
            if x2 == None:
                axis.plot(self('elapsedTime', unit = unit), self(x1),label = x1, **kwargs)
                axis.set_ylabel(self.units[x1])
                axis.set_xlabel("Time("+unit+")")
            else:
                axis.plot(self(x1, unit = unit), self(x2),label = x2, **kwargs)
                axis.set_ylabel(self.units[x2])
        else:
            if x2 == None:
                axis.plot(self('elapsedTime', unit = unit), self(x1),fmt,label = x1 ,**kwargs)
                axis.set_ylabel(self.units[x1]) 
                axis.set_xlabel("Time("+unit+")")
            else:
                axis.plot(self(x1, unit = unit), self(x2),fmt,label = x2, **kwargs)
                axis.set_ylabel(self.units[x2]) 
                
         

def commitToMySQL(path, filename = "",channelban = None, username = None, password = None,ip = 'localhost', db = 'simeros'):
    start = time.time()
    con = SQL.connect(host=ip, user=username, passwd=password)
    mycursor = con.cursor()
    con.select_db(db)
    
    if channelban == None:
        channelban = []
    channelban.append('Timestamp')
    channelban.append('date')
    channelban.append('elapsedTime')
    channelban.append('UnixTime')
    channelban.append('UIDInstrumentation')
#    path = "C:\\Users\\ernesto.saraiva\\Desktop\\03.05\\"
    filesWithZList = (glob.glob(path+"*Z*.LTX"))
    filesList = (glob.glob(path+"*.LTX"))
    files = [os.path.basename(element) for element in filesList if element not in filesWithZList]
    tests = []
    todosArquivosOk = True
    mycursor.execute("SELECT path FROM tbinstrumentation")
    result = mycursor.fetchall()
    filesAlreadyThere = []
    for a in result:
        filesAlreadyThere.append(os.path.basename(a[0]))
    filesToAdd = {}
    for file in files:
        numindex = []

            
        for i, char in enumerate(file[::-1][4:]):
            if char in ['0','1','2','3','4','5','6','7','8','9']:
                numindex.append(len(file) - 1 - i - 4)
            else:
                if char == '_':
                    _index = len(file) - i - 4 - 1
                else:
                    _index = len(file) - i - 4
                break
#        print(file)
#        print(numindex)
#        print(_index)
        if len(numindex) == 0:
            print('arquivo ' + file +' sem index')
            todosArquivosOk = False
        else:
            if not (file[0:_index].replace('-','_') in tests):
                tests.append(file[0:_index].replace('-','_'))
                filesToAdd[file[0:_index].replace('-','_')] = []
            if file not in filesAlreadyThere:
                filesToAdd[file[0:_index].replace('-','_')].append(file)
                
    if not todosArquivosOk:
        print('arquivos sem index nao vao ser adicionados')
        
    print("Arquivos a serem adicionados: " + str(filesToAdd))
    
    ##por os arquivos do filesToAdd no instrumentationtbh ah e cada file tem seu proprio instrumentation uid entao tem q muda isso ae e n ser por table blz
    for test in tests:
        df = pd.DataFrame()
        
        for file in filesToAdd[test]:
            
            insertString = "INSERT INTO "+ "tbinstrumentation" +" (UID,Path, Created) VALUES (%s,%s,%s)"
            fileUUID = uuid.uuid4()
            values = (fileUUID, file, datetime.datetime.now())
            mycursor.execute(insertString, values)
            df, validChannels, LynxFile = getDataFrame(path,fileString=file[:-4], frequency = 0)
            df['UIDInstrumentation'] = fileUUID 
            #df = df.append(temp, ignore_index = True)
#        print(df.describe())

            if df.empty:
                pass
            else:
                mycursor.execute("SHOW TABLES")
                dateString = str(df['date'][0].year)[2:] + '' + '{:0>2d}'.format(df['date'][0].month) + '' + '{:0>2d}'.format(df['date'][0].day)
                tableName = test + '_' + dateString
                tableExists = False
                for x in mycursor:
                    tableExists = tableExists or (tableName.lower() in x)
                
                if not tableExists:
                    createString = "CREATE TABLE " + tableName + "(UID VARCHAR(36), UIDInstrumentation VARCHAR(36),Time DOUBLE, Value DOUBLE, CH VARCHAR(50))"
                    print('criada table ' + tableName)
                    mycursor.execute(createString)
                    
                else:
                    mycursor = con.cursor()
                    print('tabela ' + tableName + ' já existe')
                
                
        #        VER MINIMO E MAXIMO DA TABELA VER SE O DATAFRAME TA DENTRO DESSE SE ESTIVER PARCIALEMENTE CORTAR DF
                previousDay = df['date'][0].day
                for index,row in df.iterrows():
                    
                    if previousDay != row['date'].day:
                        print('mudou o dia' + str(previousDay) + ' ' + str(row['date'].day) )
                        
                        mycursor.execute("SHOW TABLES")
                        dateString = str(row['date'].year)[2:] + '' + str(row['date'].month) + '' + str(row['date'].day)
                        tableName = test + '_' + dateString
                        tableExists = False
                        for x in mycursor:
                            tableExists = tableExists or (tableName.lower() in x)
                        
                        if not tableExists:
                            createString = "CREATE TABLE " + tableName + "(UID VARCHAR(36), UIDInstrumentation VARCHAR(36),Time DOUBLE, Value DOUBLE, CH VARCHAR(50))"
                            mycursor.execute(createString)
                            print('criada table ' + tableName)
                        else:
                            mycursor = con.cursor()
                            print('tabela ' + tableName + ' já existe')
                    previousDay = row['date'].day
                    
    #                for columnName in df:
    #                    if ("Timestamp" not in columnName) and ("date" not in columnName) and ("elapsedTime" not in columnName) and ('UnixTime' not in columnName) and ('UIDInstrumentation' not in columnName):
    #                        values = (str(uuid.uuid4()),str(row['UIDInstrumentation']), row['UnixTime'], row[columnName], columnName)
    #    #                    print(tableName)
    #                        if math.isnan(values[2]) or math.isnan(values[3]):
    #    #                        print("Not a Number no Index: "+ str(index) + " na coluna "+ rowName +  " valor não adicionado")
    #                            pass
    #                        else:
    #                            insertString = "INSERT INTO "+ tableName +" (UID,UIDInstrumentation,Time, Value ,CH) VALUES (%s,%s,%s, %s, %s)"
    #                            mycursor.execute(insertString, values)
                    values = []
                    for columnName in df:
                        if columnName not in channelban:
                            tempvalues = (str(uuid.uuid4()),str(row['UIDInstrumentation']), row['UnixTime'], row[columnName], columnName)
                            
                            if math.isnan(tempvalues[2]) or math.isnan(tempvalues[3]):
        #                        print("Not a Number no Index: "+ str(index) + " na coluna "+ rowName +  " valor não adicionado")
                                pass
                            else:
                                values.append(tempvalues)
                                
                                
    #                            mycursor.execute(insertString, values)
                    insertString = "INSERT INTO "+ tableName +" (UID,UIDInstrumentation,Time, Value ,CH) VALUES (%s,%s,%s, %s, %s)"  
                    mycursor.executemany(insertString, values)
                    
              
        del(df)
    con.commit()
    con.close()
    end = time.time()
    print('Tempo de execucao: ' + str(end - start) + 's')
    
    
    
    