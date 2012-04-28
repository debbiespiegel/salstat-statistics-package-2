#!/usr/bin/env python

"""SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed 
under the GNU General Public License (GPL). See the file COPYING for full
details of this license. """

# import wx stuff
#from wxPython.wx import *
#from wxPython.stc import *
#from wxPython.grid import *
#from wxPython.html import *
#from wxPython.lib.editor import wxEditor
import wx
import os
from grid import MyGrid, MyContextGrid
from matplotlib import mlab

import wx.aui
import wx.lib.agw.aui as aui

# import wx # getting ready for the new namespace
import wx.lib.wxpTag
# import system modules
import string, os, os.path, pickle
# import SalStat specific modules
import salstat_stats, images
import numpy, math  
# and for plots!
#from wxPython.lib.wxPlotCanvas import *
#from wxPython.lib import wxPlotCanvas
import wx.lib.plot as pyplot
# set ip the xml modules
from xml.dom import minidom
#---------------------------------------------------------------------------
# set up id's for menu events - all on menu, some also available elsewhere
ID_FILE_NEW = wx.ID_ANY
ID_FILE_NEWOUTPUT = wx.ID_ANY
ID_FILE_OPEN = wx.ID_ANY
ID_FILE_SAVE = wx.ID_ANY
ID_FILE_SAVEAS = wx.ID_ANY
ID_FILE_PRINT = wx.ID_ANY
ID_FILE_EXIT = wx.ID_ANY
ID_EDIT_CUT = wx.ID_ANY
ID_EDIT_COPY = wx.ID_ANY
ID_EDIT_PASTE = wx.ID_ANY
ID_EDIT_SELECTALL = wx.ID_ANY
ID_EDIT_FIND = wx.ID_ANY
ID_EDIT_DELETECOL = wx.ID_ANY
ID_EDIT_DELETEROW = wx.ID_ANY
ID_PREF_VARIABLES = wx.ID_ANY
ID_PREF_GRID = wx.ID_ANY
ID_PREF_CELLS = wx.ID_ANY
ID_PREF_FONTS = wx.ID_ANY
ID_PREPARATION_DESCRIPTIVES = wx.ID_ANY
ID_PREPARATION_TRANSFORM = wx.ID_ANY
ID_PREPARATION_OUTLIERS = wx.ID_ANY
ID_PREPARATION_NORMALITY = wx.ID_ANY
ID_TRANSFORM_SQUAREROOT = wx.ID_ANY
ID_TRANSFORM_SQUARE = wx.ID_ANY
ID_TRANSFORM_INVERSE = wx.ID_ANY
ID_TRANSFORM_OTHER = wx.ID_ANY
ID_ANALYSE_1COND = wx.ID_ANY
ID_ANALYSE_2COND = wx.ID_ANY
ID_ANALYSE_3COND = wx.ID_ANY
ID_ANALYSE_CORRELATION = wx.ID_ANY
ID_ANALYSE_2FACT = wx.ID_ANY
ID_ANALYSE_SCRIPT = wx.ID_ANY
ID_ANALYSE2_1COND = wx.ID_ANY
ID_ANALYSE2_2COND = wx.ID_ANY
ID_ANALYSE2_3COND = wx.ID_ANY
ID_ANALYSE2_1_TTEST = wx.ID_ANY
ID_ANALYSE2_1_SIGN = wx.ID_ANY
ID_CHART = wx.ID_ANY
ID_CHART_DRAW = wx.ID_ANY
ID_BARCHART_DRAW = wx.ID_ANY
ID_HELP_WIZARD = wx.ID_ANY
ID_HELP_TOPICS = wx.ID_ANY
ID_HELP_SCRIPTING = wx.ID_ANY
ID_HELP_LICENCE = wx.ID_ANY
ID_HELP_ABOUT = wx.ID_ANY
ID_OFILE_NEW = wx.ID_ANY
ID_OFILE_OPEN = wx.ID_ANY
ID_OFILE_SAVE = wx.ID_ANY
ID_OFILE_SAVEAS = wx.ID_ANY
ID_OFILE_PRINT = wx.ID_ANY
ID_OFILE_CLOSE = wx.ID_ANY
ID_OEDIT_CUT = wx.ID_ANY
ID_OEDIT_COPY = wx.ID_ANY
ID_OEDIT_PASTE = wx.ID_ANY
ID_OEDIT_SELECTALL = wx.ID_ANY
ID_OPREF_FONT = wx.ID_ANY
ID_FILE_GSAVEAS = wx.ID_ANY
ID_FILE_GPRINTSETUP = wx.ID_ANY
ID_FILE_GPRINTPREVIEW = wx.ID_ANY
ID_FILE_GPRINT = wx.ID_ANY
ID_FILE_GCLOSE = wx.ID_ANY
ID_TITLE_GYAXIS = wx.ID_ANY
ID_TITLE_GXAXIS = wx.ID_ANY
ID_TITLE_GTITLE = wx.ID_ANY
ID_TITLE_LEGEND = wx.ID_ANY
ID_TITLE_GRID = wx.ID_ANY

DescList=['N','Sum','Mean','Variance','Standard Deviation','Standard Error',\
          'Sum of Squares','Sum of Squared Devs', \
          'Coefficient of Variation','Minimum',   \
          'Maximum','Range','Number Missing',     \
          'Geometric Mean','Harmonic Mean',       \
          'Skewness','Kurtosis', 'Median',        \
          'Median Absolute Deviation','Mode',     \
          'Interquartile Range',                  \
          'Number of Unique Levels']

HypList = ['One tailed','Two tailed']
inits={}    # dictionary to hold the config values
ColsUsed = []
RowsUsed = []
missingvalue = -99.999
global filename # ugh
filename = 'UNTITLED'
global BWidth, BHeight # ugh again!
BWidth = 80
BHeight = 25
HOME = os.getcwd()

if os.name == 'nt':
    face1 = 'Courier New'
    face2 = 'Times New Roman'
    face3 = 'Courier New'
    fontsizes = [7,8,10,12,16,22,30]
    pb = 12
    wind = 50
    DOCDIR = 'c:\My Documents'
    INITDIR = os.getcwd()
else:
    face1 = 'Helvetica'
    face2 = 'Times'
    face3 = 'Courier'
    fontsizes = [10,12,14,16,19,24,32]
    pb = 12
    wind = 0
    DOCDIR = os.environ['HOME']
    INITDIR = DOCDIR

class History:
    def __init__(self):
        self.history = '' # change this for the proper DTD please!

    def AppendEvent(self, xmltags):
        self.history = self.history + xmltags

    def ClearHistory(self):
        self.history = ''

class SaveDialog(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Save Data?", \
                           size=(270+wind,100+wind), style = wx.DIALOG_EX_METAL)
        icon = images.getIconIcon()
        self.SetIcon(icon)
        self.Choice = 'none'
        vbox = wx.BoxSizer(wx.VERTICAL)
        l1 = wx.StaticText(self, -1, 'You have unsaved Data')
        l2 = wx.StaticText(self, -1, 'Do you wish to save it?')
        vbox.Add(l1,1, wx.ALIGN_CENTER)
        vbox.Add(l2,1, wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.ALIGN_CENTER_HORIZONTAL)
        saveButton = wx.Button(self, 331, "Save...", size=(BWidth, BHeight))
        discardButton = wx.Button(self, 332, "Discard", size=(BWidth, BHeight))
        CancelButton = wx.Button(self, 333, "Cancel", size=(BWidth, BHeight))
        hbox.Add(saveButton, 0, wx.ALL, 5)
        hbox.Add(discardButton, 0, wx.ALL, 5)
        hbox.Add(CancelButton, 0, wx.ALL, 5)
        vbox.Add(hbox,1)
        self.SetAutoLayout(True)
        self.SetSizer(vbox)
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.SaveData, id = 331)
        self.Bind(wx.EVT_BUTTON, self.DiscardData, id = 332)
        self.Bind(wx.EVT_BUTTON, self.CancelDialog, id = 333)

    def SaveData(self, event):
        frame.grid.Saved = True
        frame.grid.SaveAsDataASCII(self) # will it be ASCII or XML?
        output.Close(True)
        frame.Close(True)
        self.Close(True)

    def DiscardData(self, event):
        output.Close(True)
        frame.Close(True)
        self.Close(True)

    def CancelDialog(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# creates an init file in the home directory of the user
class GetInits:
    """This class deals with a users init file. The coords and sizes of the
    various widgets are kept here, and are stored throughout the program
    as a dictionary for easy access. When the program starts, the home
    directory is checked for the init files existence. If absent, it is
    created with a series of default values. If it is present, the values are
    read into the dictionary in a slightly roundabout way! I am sure that
    there is a more "Python" way of doing this, but this way works for now"""
    def __init__(self):
        self.initfile = os.path.join(INITDIR, '.salstatrc')
        if os.path.isfile(self.initfile):
            self.ReadInitFile(self.initfile)
        else:
            self.CreateInitFile(self.initfile)

    def ReadInitFile(self, initfilename):
        inits.clear()
        fin = file(initfilename, 'r')
        for i in range(28):
            a = fin.readline()
            a = string.split(a)
            tmpdict = {a[0]:a[1]}
            inits.update(tmpdict)

    def CreateInitFile(self, initfilename):
        inits = {
            'gridsizex': '600',
            'gridsizey': '420',
            'gridposx': '50',
            'gridposy': '20',
            'gridcellsx': '20',
            'gridcellsy': '80',
            'outputsizex': '500',
            'outputsizey': '400',
            'outputposx': '20',
            'outputposy': '50',
            'scriptsizex': '600',
            'scriptsizey': '400',
            'scriptposx': '35',
            'scriptposy': '35',
            'chartsizex': '600',
            'chartsizey': '400',
            'chartposx': '50',
            'chartposy': '50',
            'helpsizex': '600',
            'helpsizey': '400',
            'helpposx': '40',
            'helpposy': '40',
            'lastfile1': "...",
            'lastfile2': "...",
            'lastfile3': "...",
            'lastfile4': "...",
            'opendir': DOCDIR,
            'savedir': DOCDIR
        }
        initskeys = inits.keys()
        initsvalues = inits.values()
        fout = file(initfilename,'w')
        for i in range(len(initskeys)):
            fout.write(str(initskeys[i])+' '+str(initsvalues[i])+'\n')
        fout.close()
        self.ReadInitFile(initfilename) # damn hack!

#---------------------------------------------------------------------------
# class to output the results of several "descriptives" in one table
class ManyDescriptives:
    def __init__(self, source, ds):
        __x__ = len(ds)
        outstring = ""
        outstring = outstring +'<table border = "1"><tr><td>Statistic</td>'
        for i in range(__x__):
            outstring = outstring +'<td>'+ds[i].Name+'</td>'
        if source.DescChoice.IsChecked(0):
            outstring = outstring +'</tr><tr><td>N </td>'
            for i in range(__x__):
                outstring = outstring +'<td>'+str(ds[i].N)+'</td>'
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="N"'+col+str(ds[i].N)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(1):
            outstring = outstring +'</tr><tr><td>Sum </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].sum
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Sum"'+col+str(ds[i].sum)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(2):
            outstring = outstring +'</tr><tr><td>Mean </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].mean
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Mean"'+col+str(ds[i].mean)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(3):
            outstring = outstring +'</tr><tr><td>Variance </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].samplevar
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Sample Variance"'+col+str(ds[i].samplevar)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(4):
            outstring = outstring +'</tr><tr><td>Standard Deviation </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].stddev
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Standard Deviation"'+col+str(ds[i].stddev)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(5):
            outstring = outstring +'</tr><tr><td>Standard Error </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].stderr
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Standard Error"'+col+str(ds[i].stderr)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(6):
            outstring = outstring +'</tr><tr><td>Sum of Squares </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].sumsquares
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Sum of Squares"'+col+str(ds[i].sumsquares)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(7):
            outstring = outstring +'</tr><tr><td>Sum of Squared Deviations </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].ssdevs
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Sum of Squared Deviations"'+col+str(ds[i].ssdevs)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(8):
            outstring = outstring +'</tr><tr><td>Coefficient of Variation </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].coeffvar
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Coefficient of Variation"'+col+str(ds[i].coeffvar)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(9):
            outstring = outstring +'</tr><tr><td>Minimum </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].minimum
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Minimum"'+col+str(ds[i].minimum)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(10):
            outstring = outstring +'</tr><tr><td>Maximum </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].maximum
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Maximum"'+col+str(ds[i].maximum)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(11):
            outstring = outstring +'</tr><tr><td>Range </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].range
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Range"'+col+str(ds[i].range)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(12):
            outstring = outstring +'</tr><tr><td>Number Missing</td>'
            for i in range(__x__):
                outstring = outstring +'<td>%6d</td>'%ds[i].missing
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Number Missing"'+col+str(ds[i].missing)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(13):
            outstring = outstring +'</tr><tr><td>Geometric Mean</td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].geomean
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Geometric Mean"'+col+str(ds[i].geomean)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(14):
            outstring = outstring +'</tr><tr><td>Harmonic Mean</td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].harmmean
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Harmonic Mean"'+col+str(ds[i].harmmean)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(15):
            outstring = outstring +'</tr><tr><td>Skewness </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].skewness
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Skewness"'+col+str(ds[i].skewness)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(16):
            outstring = outstring +'</tr><tr><td>Kurtosis </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].kurtosis
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Kurtosis"'+col+str(ds[i].kurtosis)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(17):
            outstring = outstring +'</tr><tr><td>Median </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].median
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Median"'+col+str(ds[i].median)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(18):
            outstring = outstring +'</tr><tr><td>Median Absolute Deviation </td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].mad
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Mean Absolute Deviation"'+col+str(ds[i].mad)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(19):
            outstring = outstring +'</tr><tr><td>Mode</td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5.5f</td>'%ds[i].mode
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Mode"'+col+str(ds[i].mode)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        if source.DescChoice.IsChecked(21):
            outstring = outstring +'</tr><tr><td>Number Unique Levels</td>'
            for i in range(__x__):
                outstring = outstring +'<td>%5d</td>'%ds[i].numberuniques
                col = ' column="'+str(i)+'">'
                xmlevt = '<describe test="Number of Unique Values"'+col+str(ds[i].numberuniques)+'</describe>\n'
                hist.AppendEvent(xmlevt)
        output.htmlpage.Addhtml(outstring+'</table>')

#---------------------------------------------------------------------------
# class for grid - used as datagrid.
class SimpleGrid(MyGrid):# wxGrid
    def __init__(self, parent, log):
        MyGrid.__init__(self, parent, -1)
        self.Saved = True
        self.moveTo = None
        ##self.m_grid.SetGridLineColour(wx.Color(0,0,0))
        #self.m_grid.CreateGrid(int(inits.get("gridcellsy")), \
        #                            int(inits.get("gridcellsx")))
        self.m_grid.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        for i in range(20):
            self.m_grid.SetColFormatFloat(i, 8, 4)
        self.m_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.AlterSaveStatus)
        self.m_grid.Bind(wx.grid.EVT_GRID_CMD_LABEL_RIGHT_DCLICK, self.RangeSelected)
        self.m_grid.wildcard = "Any File (*.*)|*.*|" \
            "ASCII data format (*.dat)|*.dat|" \
            "SalStat Format (*.xml)|*.xml"
        pass

    def RangeSelected(self, event):
        if event.Selecting():
            self.tl = event.GetTopLeftCoords()
            self.br = event.GetBottomRightCoords()

    def AlterSaveStatus(self, event):
        # this is activated when the user enters some data
        self.Saved = False
        # also record in the history file
        col = self.m_grid.GetGridCursorCol()
        row = self.m_grid.GetGridCursorRow()
        value = self.m_grid.GetCellValue(row, col)
        xmlevt = '<data row="'+str(row)+'" col="'+str(col)+'">'+str(value)+'</data>\n'
        hist.AppendEvent(xmlevt)
        print hist.history

    def CutData(self, event):
        buffer = wx.TextDataObject()
        currentcol = self.m_grid.GetGridCursorCol()
        currentrow = self.m_grid.GetGridCursorRow()
        if self.m_grid.IsSelection():
            data = 'range' # change this to coords self.tl self.br
        else:
            data = self.m_grid.GetCellValue(currentrow, currentcol)
        if (wx.TheClipboard.Open()):
            buffer.SetText(data)
            wx.TheClipboard.SetData(buffer)
            wx.TheClipboard.Close()
            self.m_grid.SetCellValue(currentrow, currentcol, '')

    def CopyData(self, event):
        buffer = wx.TextDataObject()
        currentcol = self.m_grid.GetGridCursorCol()
        currentrow = self.m_grid.GetGridCursorRow()
        #if self.IsSelection(): # extend this only if SalStat can paste lists
        #    data = [2,3,4,5]
        #else:
        data = self.m_grid.GetCellValue(currentrow, currentcol)
        if (wx.TheClipboard.Open()):
            buffer.SetText(data)
            wx.TheClipboard.SetData(buffer)
            wx.TheClipboard.Close()

    def PasteData(self, event):
        buffer = wx.TextDataObject()
        currentcol = self.m_grid.GetGridCursorCol()
        currentrow = self.m_grid.GetGridCursorRow()
        res = wx.TheClipboard.Open()
        if res:
            res = wx.TheClipboard.GetData(buffer)
            wx.TheClipboard.Close()
            if res:
                self.Saved = False
                if type(buffer.GetText()) != list:
                    self.m_grid.SetCellValue(currentrow, currentcol, buffer.GetText())
                else:
                    self.m_grid.SetCellValue(currentrow, currentcol, 'list!')

    def EditGrid(self, event, numrows):
        insert = self.AppendRows(numrows)

    def DeleteCurrentCol(self, event):
        currentcol = self.m_grid.GetGridCursorCol()
        self.m_grid.DeleteCols(currentcol, 1)
        self.m_grid.AdjustScrollbars()
        xmlevt = '<deleteColumn>'+str(currentcol)+'</deleteColumn>\n'
        hist.AppendEvent(xmlevt)

    def DeleteCurrentRow(self, event):
        currentrow = self.m_grid.GetGridCursorRow()
        self.m_grid.DeleteRows(currentrow, 1)
        self.m_grid.AdjustScrollbars()
        xmlevt = '<deleteRow>'+str(currentrow)+'</deleteRow>\n'
        hist.AppendEvent(xmlevt)

    def SelectAllCells(self, event):
        self.m_grid.SelectAll()

    # adds columns and rows to the grid
    def AddNCells(self, numcols, numrows):
        insert = self.m_grid.AppendCols(numcols)
        insert = self.m_grid.AppendRows(numrows)
        for i in range(self.m_grid.GetNumberCols() - numcols):
            self.SetColLabelAlignment(wxALIGN_LEFT, wxALIGN_BOTTOM)
            self.SetColFormatFloat(i, 8, 4)
        self.AdjustScrollbars()
        xmlevt = '<appendColumn>'+str(numcols)+'</appendColumn>\n'
        hist.AppendEvent(xmlevt)
        xmlevt = '<appendRow>'+str(numrows)+'</appendRow>\n'
        hist.AppendEvent(xmlevt)

    # function finds out how many cols contain data - all in a list
    #(ColsUsed) which has col #'s
    def GetUsedCols(self):
        ColsUsed = []
        colnums = []
        cols = self.m_grid.GetNumberCols()
        for i in range(cols):
            dat = self.m_grid.GetCellValue(0, i)
            if (dat!=''):
                ColsUsed.append(self.m_grid.GetColLabelValue(i))
                colnums.append(i)
        return ColsUsed, colnums

    def GetColsUsedList(self):
        colsusedlist = []
        for i in range(self.GetNumberCols()):
            try:
                tmp = float(self.GetCellValue(0,i))
                colsusedlist.append(i)
            except ValueError:
                colsusedlist.append(0)
        return colsusedlist

    def GetUsedRows(self):
        RowsUsed = []
        for i in range(self.GetNumberCols()):
            if (self.GetCellValue(0, i) != ''):
                for j in range(self.GetNumberRows()):
                    if (self.GetCellValue(j,i) == ''):
                        RowsUsed.append(j)
                        break
        return RowsUsed

    def SaveAsDataASCII(self, event):
        default = inits.get('savedir')
        dlg = wx.FileDialog(self, "Save Data File", default,"",\
                            "ASCII Text (*.dat)|*.dat", wx.SAVE)
                                    #"ASCII Text (*.dat)|*.dat|SalStat File (*.xml)|*.xml|", wxSAVE)
        icon = images.getIconIcon()
        dlg.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK:
            inits.update({'savedir': dlg.GetDirectory()})
            filename = dlg.GetPath()
            fout = open(filename, "w")
            cols,waste = self.GetUsedCols()
            if (dlg.GetFilterIndex() == 0):
                #save as plain text
                rows = self.GetUsedRows()
                maxrows = max(rows) 
                for i in range(len(cols)):
                    for j in range(maxrows):
                        if (self.GetCellValue(j,i) == ''):
                            self.SetCellValue(j,i,'.')
                for i in range(maxrows):
                    datapoint=[]
                    for j in range(len(cols)):
                        try:
                            datapoint.append(self.GetCellValue(i, j))
                        except:
                            datapoint.append("0")
                        line = string.join(datapoint)
                    fout.write(line)
                    fout.write('\n')
            elif (dlg.GetFilterIndex() == 1):
                # save as native format
                print "cannot do this just yet!"
            fout.close
            self.Saved = True

    def SaveDataASCII(self, event):
        default = inits.get('savedir')
        if (filename == 'UNTITLED'):
            self.SaveAsDataASCII(event)
            """dlg = wxFileDialog(self, "Save Data File", default,"",\
                                    "ASCII Text (*.dat)|*.dat| \
                                    numpy Array (*.npy)|*.npy| \
                                    Any (*.*)| \
                                    *.*", wxSAVE)
            icon = images.getIconIcon()
            dlg.SetIcon(icon)
            if dlg.ShowModal() == wxID_OK:
                inits.update({'savedir': dlg.GetDirectory()})
                filename = dlg.GetPath()
            else:
                return"""
        fout = open(filename, "w")
        cols, waste = self.GetUsedCols()
        rows = self.GetUsedRows()
        maxrows = max(rows) + 1
        for i in range(maxrows):
            datapoint=[]
            for j in range(len(cols)):
                try:
                    datapoint.append(self.GetCellValue(i, j))
                except:
                    datapoint.append("0")
            line = string.join(datapoint)
            fout.write(line)
            fout.write('\n')
        fout.close
        self.Saved = True

    # Loads an ASCII data file - only with all datapoints filled though!
    # also does csv values as well
    def LoadDataASCII(self, event):
        default = inits.get('opendir')
        dlg = wx.FileDialog(self, "Load Data File", default,"",
                            wildcard= "SalStat Native (*.xml)|*.xml|",
                            style = wx.OPEN)
                #, wxOPEN)
        icon = images.getIconIcon()
        dlg.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if filename[-3:] == 'xml':
                self.LoadNativeXML(filename)
            else:
                inits.update({'opendir': dlg.GetDirectory()})
                self.ClearGrid()
                # exception handler here!
                try:
                    fin = open(filename, "r")
                except IOError:
                    pass # what to do if they filename isn't visible? Messagebox?
                gridline = 0
                self.Freeze()
                for i in fin.readlines():
                    words = string.split(i)
                    if len(words) > self.GetNumberCols():
                        NumberCols = len(words) - self.GetNumberCols() + 10
                        self.AddNCells(NumberCols, 0)
                    for j in range(len(words)):
                        self.SetCellValue(gridline, j, words[j])
                    gridline = gridline + 1
                    if (gridline == self.GetNumberRows()):
                        self.AddNCells(0,10)
                fin.close()
                self.Thaw()
            self.ForceRefresh()

    def getData(self, x):
        for i in range(len(x)):
            try:
                row = int(x[i].attributes["row"].value)
                col = int(x[i].attributes["column"].value)
                datavalue = float(self.getText(x[i].childNodes))
                self.SetCellValue(row, col, str(datavalue))
            except ValueError:
                print "problem importing the xml"

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def LoadNativeXML(self, filename):
        # also get rid of the old history
        if os.path.isfile(filename) == 0:
            pass
        else:
            # now start the XML processing
            self.ClearGrid()
            self.Freeze()
            xmldoc = minidom.parse(filename)
            datatags = xmldoc.getElementsByTagName('data')
            self.getData(datatags)
            deleteRowTags = xmldoc.getElementsByTagName('deleteRow')
            for i in range(len(deleteRowTags)):
                rownum = int(self.getText(deleteRowTags[i].childNodes))
                self.DeleteRows(rownum, 1)
            deleteColTags = xmldoc.getElementsByTagName('deleteColumn')
            for i in range(len(deleteColTags)):
                colnum = int(self.getText(deleteColTags[i].childNodes))
                self.DeleteCols(colnum, 1)
            appendRowTags = xmldoc.getElementsByTagName('appendRow')
            for i in range(len(appendRowTags)):
                rownum = int(self.getText(appendRowTags[i].childNodes))
                self.AppendRows()
            appendColTags = xmldoc.getElementsByTagName('appendColumn')
            for i in range(len(appendColTags)):
                colnum = int(self.getText(appendRowTags[i].childNodes))
                self.AppendCols()
            deleteColTags = xmldoc.getElementsByTagName('deleteColumn')
            for i in range(len(deleteColTags)):
                colnum = int(self.getText(deleteColTags[i].childNodes))
                self.DeleteCurrentCol(colnum)
            deleteRowTags = xmldoc.getElementsByTagName('deleteRow')
            for i in range(len(deleteRowTags)):
                rownum = int(self.getText(deleteRowTags[i].childNodes))
                self.DeleteCurrentRow(rownum)
            # there is a problem here - the html tags embedded between the <results> tags
            # are parsed as XML, but I want the whole lot available as a string.
            output.htmlpage.SetPage('<P><B>SalStat Statistics</B></P>')
            output.htmlpage.WholeOutString = ''
            resultsTags = xmldoc.getElementsByTagName('results')
            for i in range(len(resultsTags)):
                outputText = self.getText(resultsTags[i].childNodes)
                print "out" + outputText # debugging!
                output.htmlpage.Addhtml(outputText)
            #describeTags = xmldoc.getElementsByTagName('describe')
            #for i in range(len(describeTags)):
            self.Thaw()

    def LoadDataASCII2(self, event):
        # redundant routine
        default = inits.get('opendir')
        dlg = wxFileDialog(self, "Load Data File", default,"",\
                           "ASCII Text (*.dat)|*.dat",wxOPEN)
                #numpy Array (*.npy)|*.npy|", wxOPEN)
        icon = images.getIconIcon()
        dlg.SetIcon(icon)
        if dlg.ShowModal() == wxID_OK:
            inits.update({'opendir': dlg.GetDirectory()})
            filename = dlg.GetPath()
            self.ClearGrid()
            # exception handler here!
            fin = open(filename, "r")
            #if filename[-3:] == 'dat':
            if 1:
                # text data file
                # size the datafile first
                dataheight = 0
                line = fin.readline()
                words = string.split(line)
                datawidth = len(words)
                while 1:
                    try:
                        line = fin.readline()
                    except:
                        pass
                    if (line == ''):
                        break
                    dataheight = dataheight + 1
                gridwidth = self.GetNumberCols()
                gridheight = self.GetNumberRows()
                if (datawidth > gridwidth):
                    self.AddNCols(-1, (datawidth - gridwidth + 5))
                if (dataheight > gridheight):
                    self.AddNRows(-1, (dataheight -  gridheight + 5))
                fin.close
                fin = open(filename, "r")
                currentrow = 0
                for i in range(dataheight):
                    line = fin.readline()
                    if (line == ''):
                        break
                    line = string.replace(line, ',', ' ')
                    words = string.split(line)
                    for i in range(len(words)):
                        self.SetCellValue(currentrow, i, words[i])
                    currentrow = currentrow + 1
            elif filename[-3:] == 'npy':
                p = pickle.Unpickler(fin)
                dataset = p.load()
                # put dataset into grid
            fin.close()
            self.ForceRefresh()

    def LoadNumericData(self, event):
        default = inits.get('opendir')
        dlg = wxFileDialog(self, "Load Data File", default,"","*.\
                                    dat|*.*", wxOPEN)
        icon = images.getIconIcon()
        dlg.SetIcon(icon)
        if dlg.ShowModal() == wxID_OK:
            inits.update({'opendir': dlg.GetDirectory()})
            filename = dlg.GetPath()
            self.ClearGrid()
            # exception handler here!
            fin = open(filename, "r")
            p = pickle.Unpickler(fin)
            dataset = p.load()
            fin.close()
            # put dataset into grid

    def CleanRowData(self, row):
        indata = []
        for i in range(self.GetNumberCols()):
            datapoint = self.GetCellValue(row, i)
            if (datapoint != ''):
                value = float(datapoint)
                if (value != missingvalue):
                    indata.append(value)
        return indata

    # Routine to return a "clean" list of data from one column
    def CleanData(self, col):
        indata = []
        self.missing = 0
        for i in range(self.m_grid.GetNumberRows()):
            datapoint = self.m_grid.GetCellValue(i, col)
            if (datapoint != '') and (datapoint != '.'):
                try:
                    value = float(datapoint)
                    if (value != missingvalue):
                        indata.append(value)
                    else:
                        self.missing = self.missing + 1
                except ValueError:
                    pass
        return indata

    def GetEntireDataSet(self, numcols):
        """Returns the data specified by a list 'numcols' in a Numeric
        array"""
        biglist = []
        for i in range(len(numcols)):
            smalllist = frame.grid.CleanData(numcols[i])
            biglist.append(smalllist)
        return numpy.array((biglist), numpy.float)

#---------------------------------------------------------------------------
# DescChoice-wxCheckListBox with list of descriptive stats in it
class DescChoiceBox(wx.CheckBox): # CheckListBox
    def __init__(self, parent, id):
        wxCheckListBox.__init__(self, parent, -1, pos=(250,30), \
                                size=(240,310), choices=DescList)

    def SelectAllDescriptives(self, event):
        for i in range(len(DescList)):
            self.Check(i, True)

    def SelectNoDescriptives(self, event):
        for i in range(len(DescList)):
            self.Check(i, False)

#---------------------------------------------------------------------------
# base class for getting number of columns/rows to add
class EditGridFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Change Grid Size", \
                           size=(205, 100+wind))
        icon = images.getIconIcon()
        self.SetIcon(icon)
        l1 = wxStaticText(self, -1, 'Add Columns',pos=(10,15))
        l2 = wxStaticText(self, -1, 'Add Rows',pos=(10,55))
        self.numnewcols = wxSpinCtrl(self, -1, "", wxPoint(110,10), wxSize(80,25))
        self.numnewcols.SetRange(0, 100)
        self.numnewcols.SetValue(0)
        self.numnewRows = wxSpinCtrl(self, -1, "", wxPoint(110, 50), wxSize(80,25))
        self.numnewRows.SetRange(0, 100)
        self.numnewRows.SetValue(0)
        okaybutton = wxButton(self, 421, "Okay", wxPoint(10, 90),\
                              wxSize(BWidth, BHeight))
        cancelbutton = wxButton(self, 422, "Cancel", wxPoint(110,90), \
                                wxSize(BWidth, BHeight))
        EVT_BUTTON(self, 421, self.OkayButtonPressed)
        EVT_BUTTON(self, 422, self.CancelButtonPressed)

    def OkayButtonPressed(self, event):
        colswanted = self.numnewcols.GetValue()
        rowswanted = self.numnewRows.GetValue()
        frame.grid.AddNCells(colswanted, rowswanted)
        self.Close(True)

    def CancelButtonPressed(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# grid preferences - set row & col sizes
class GridPrefs(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Cell Size", \
                           size=(205,100+wind))
        icon = images.getIconIcon()
        self.SetIcon(icon)
        self.colwidth = wxSpinCtrl(self, -1, "", wxPoint(110,10), wxSize(80,25))
        self.colwidth.SetRange(1,200)
        self.colwidth.SetValue(frame.grid.m_grid.GetDefaultColSize())
        self.rowheight= wxSpinCtrl(self, -1, "", wxPoint(110,50), wxSize(80,25))
        self.rowheight.SetRange(1,100)
        self.rowheight.SetValue(frame.grid.m_grid.GetDefaultRowSize())
        l1 = wxStaticText(self, -1, 'Column Width:',pos=(10,15))
        l2 = wxStaticText(self, -1, 'Row Height:',pos=(10,55))
        okaybutton = wxButton(self, 321, "Okay", wxPoint(10, 90), \
                              wxSize(BWidth, BHeight))
        cancelbutton = wxButton(self, 322, "Cancel", wxPoint(110,90),\
                                wxSize(BWidth, BHeight))
        EVT_BUTTON(self, 321, self.OkayButtonPressed)
        EVT_BUTTON(self, 322, self.OnCloseGridPrefs)

    def OkayButtonPressed(self, event):
        frame.grid.m_grid.SetDefaultColSize(self.colwidth.GetValue(), True)
        frame.grid.m_grid.SetDefaultRowSize(self.rowheight.GetValue(), True)
        frame.grid.m_grid.ForceRefresh()
        self.Close(True)

    def OnCloseGridPrefs(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# shows the scripting window for entering Python syntax commands
class ScriptFrame(wx.Frame):
    def __init__(self, parent, id):
        dimx = int(inits.get('scriptsizex'))
        dimy = int(inits.get('scriptsizey'))
        posx = int(inits.get('scriptposx'))
        posy = int(inits.get('scriptposy'))
        wx.Frame.__init__(self, parent, id, "Scripting Window", \
                          size=(dimx, dimy), pos=(posx,posy))
        #set icon for frame (needs x-platform separator!
        icon = images.getIconIcon()
        self.SetIcon(icon)
        self.scripted = wx.TextCtrl(self,-1)
        GoIcon = images.getApplyBitmap()
        OpenIcon = images.getOpenBitmap()
        SaveIcon = images.getSaveBitmap()
        SaveAsIcon = images.getSaveAsBitmap()
        PrintIcon = images.getPrintBitmap()
        CutIcon = images.getCutBitmap()
        CopyIcon = images.getCopyBitmap()
        PasteIcon = images.getPasteBitmap()
        HelpIcon = images.getHelpBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL|wxNO_BORDER| \
                                     wxTB_3DBUTTONS)
        toolBar.AddSimpleTool(710, GoIcon,"Run Script","Run the Script")
        toolBar.AddSimpleTool(711, OpenIcon,"Open","Open Script from a File")
        toolBar.AddSimpleTool(712, SaveIcon,"Save","Save Script to a file")
        toolBar.AddSimpleTool(713, SaveAsIcon,"Save As","Save Script under \
                                    a new filename")
        toolBar.AddSimpleTool(714, PrintIcon,"Print","Print Out Script")
        toolBar.AddSimpleTool(715, CutIcon, "Cut", "Cut selection to \
                                    clipboard")
        toolBar.AddSimpleTool(716, CopyIcon, "Copy", "Copy selection to \
                                    clipboard")
        toolBar.AddSimpleTool(717, PasteIcon, "Paste", "Paste selection \
                                    from clipboard")
        toolBar.AddSimpleTool(718, HelpIcon, "Help", "Get some help!")
        toolBar.SetToolBitmapSize((24,24))
        toolBar.Realize()
        EVT_TOOL(self, 710, self.ExecuteScript)
        EVT_TOOL(self, 711, self.OpenScript)
        EVT_TOOL(self, 713, self.SaveScriptAs)
        EVT_TOOL(self,715, self.CutSelection)
        EVT_TOOL(self, 716, self.CopySelection)
        EVT_TOOL(self, 717, self.PasteSelection)
        EVT_TOOL(self, 718, self.ShowHelp)

    def ExecuteScript(self, event):
        mainscript = self.scripted.GetText()
        execscript = string.join(mainscript, '\n')
        exec(execscript)

    def CutSelection(self, event):
        self.scripted.OnCutSelection(event)

    def CopySelection(self, event):
        self.scripted.OnCopySelection(event)

    def PasteSelection(self, event):
        self.scripted.OnPaste(event)

    def ShowHelp(self, event):
        win = AboutFrame(frame, -1, 2)
        win.Show(True)

    # the open script method needs work
    def OpenScript(self, event):
        default = inits.get('opendir')
        dlg = wxFileDialog(self, "Open Script File",default,"",\
                           "Any (*)|*",wxOPEN)
        if dlg.ShowModal() == wxID_OK:
            filename = dlg.GetPath()
            fin = file(filename, "r")
            TextIn = fin.readlines()

            self.scripted.SetText(TextIn)
            fin.close()

    def SaveScriptAs(self, event):
        default = inits.get('savedir')
        dlg = wxFileDialog(self, "Save Script File", default,"",\
                           "Any (*)|*", wxSAVE)
        if dlg.ShowModal() == wxID_OK:
            filename = dlg.GetPath()
            fout = open(filename, "w")
            script = self.scripted.GetText()
            for i in range(len(script)):
                fout.write(script[i]+'\n')
            fout.close
#---------------------------------------------------------------------------
# Simply display the About box w/html frame in it
class AboutFrame(wx.Frame):
    def __init__(self, parent, id, tabnumber):
        dimx = int(inits.get('scriptsizex'))
        dimy = int(inits.get('scriptsizey'))
        posx = int(inits.get('scriptposx'))
        posy = int(inits.get('scriptposy'))
        wx.Frame.__init__(self, parent, id, "About SalStat", \
                          size=(dimx, dimy), pos=(posx, posy))
        #set icon for frame (needs x-platform separator!
        icon = images.getIconIcon()
        self.SetIcon(icon)
        GoIcon = images.getApplyBitmap()

        BackIcon = images.getLeftBitmap()
        ForeIcon = images.getRightBitmap()
        HomeIcon = images.getHomeBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL | \
                                     wx.TB_3DBUTTONS)
        toolBar.AddSimpleTool(210, BackIcon, "Back","")
        toolBar.AddSimpleTool(211, ForeIcon, "Forward","")
        toolBar.AddSimpleTool(212, HomeIcon, "Home","")
        toolBar.SetToolBitmapSize((24,24))
        toolBar.Realize()
        self.SetToolBar(toolBar)
        self.tabs = wx.Notebook(self, -1)
        self.wizard = MyHtmlWindow(self.tabs, -1)
        self.topics = MyHtmlWindow(self.tabs, -1)
        self.scripting = MyHtmlWindow(self.tabs, -1)
        licence = MyHtmlWindow(self.tabs, -1)
        peeps = MyHtmlWindow(self.tabs, -1)
        self.tabs.AddPage(self.wizard, "Help Choosing a test!")
        self.wizard.LoadPage('help/wizard.html')
        self.tabs.AddPage(self.topics, "Topics")
        self.topics.LoadPage('help/index.html')
        self.tabs.AddPage(licence, "Licence")
        licence.LoadPage('help/COPYING')
        self.tabs.AddPage(peeps, "Peeps")
        peeps.LoadPage('help/about.html')
        self.tabs.SetSelection(tabnumber)
        self.Bind(wx.EVT_TOOL, self.GoBackPressed, id =  210)
        self.Bind(wx.EVT_TOOL, self.GoForwardPressed, id =  211)
        self.Bind(wx.EVT_TOOL, self.GoHomePressed, id =212)

    def GoBackPressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.GoBack(event)
        if (pagenum == 1):
            self.topics.GoBack(event)

    def GoForwardPressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.GoForward(event)
        if (pagenum == 1):
            self.topics.GoForward(event)

    def GoHomePressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.LoadPage('wizard.html')
        if (pagenum == 1):
            self.topics.LoadPage('help/index.html')

    def OnCloseAbout(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()

#---------------------------------------------------------------------------
# user can change settings like variable names, decimal places, missing no.s
# using a SimpleGrid Need event handler - when new name entered, must be
#checked against others so no match each other

class VariablesFrame(wx.Dialog):
    def __init__(self,parent,id):
        wx.Dialog.__init__(self, parent,id,"SalStat - Variables", \
                           size=(500,185+wind))

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        okaybutton = wx.Button(self.m_panel1 , 2001, "Okay", wx.DefaultPosition, wx.DefaultSize, 0 )
        cancelbutton = wx.Button(self.m_panel1 , 2002, "Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )

        bSizer2.Add( okaybutton, 0, wx.ALL, 5 )
        bSizer2.Add( cancelbutton , 0, wx.ALL, 5 )

        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo().Bottom().
                            CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).
                            Dock().Resizable().FloatingSize( wx.Size( 170,54 ) ).
                            DockFixed( False ).LeftDockable( False ).RightDockable( False ).
                            MinSize( wx.Size( -1,30 ) ).Layer( 10 ) )


        self.m_grid1 = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.vargrid = wx.grid.Grid(self,-1,) #
        self.vargrid.SetRowLabelSize(120)
        self.vargrid.SetDefaultRowSize(27, True)
        maxcols = frame.grid.m_grid.GetNumberCols()
        self.vargrid.CreateGrid(3,maxcols)
        for i in range(maxcols):
            oldlabel = frame.grid.m_grid.GetColLabelValue(i)
            self.vargrid.SetCellValue(0, i, oldlabel)
        self.vargrid.SetRowLabelValue(0,"Variable Name")
        self.vargrid.SetRowLabelValue(1,"Decimal Places")
        self.vargrid.SetRowLabelValue(2,"Missing Value")

        self.m_mgr.AddPane( self.vargrid, wx.aui.AuiPaneInfo() .Left() .CaptionVisible( False ).PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).CentrePane() )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        self.Bind(wx.EVT_BUTTON, self.OnOkayVariables, id= 2001)
        self.Bind(wx.EVT_BUTTON, self.OnCloseVariables, id =  2002)

    # this method needs to work out the other variables too
    def OnOkayVariables(self, event):
        for i in range(frame.grid.m_grid.GetNumberCols()-1):
            newlabel = self.vargrid.GetCellValue(0, i)
            if (newlabel != ''):
                frame.grid.m_grid.SetColLabelValue(i, newlabel)
            newsig = self.vargrid.GetCellValue(1, i)
            if (newsig != ''):
                try:
                    frame.grid.m_grid.SetColFormatFloat(i, -1, int(newsig))
                except ZeroDivisionError:
                    pass
        frame.grid.m_grid.ForceRefresh()
        self.Close(True)

    def OnCloseVariables(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# base html window class
class MyHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id):
        wx.html.HtmlWindow.__init__(self, parent, id)
        ##wx.Image_AddHandler(wxJPEGHandler()) # just in case!
        self.WholeOutString = ''
        self.Saved = True

    """def OnLinkClicked(self, linkinfo):
        ref = string.split(linkinfo.GetHref(),',')
        means = []
        for i in range(1, len(ref), 2):
            if ref[i] == 'M':
                means.append(float(ref[i+1]))
            elif ref[i] == 'k':
                k = int(ref[i+1])
            elif ref[i] == 'n':
                n = int(ref[i+1])
            elif ref[i] == 'p':
                p = float(ref[i+1])
        self.Addhtml(str(means)+' '+str(k)+' '+str(n)+' '+str(p))
        if ref[0] == 'friedman':
            waste = salstat_stats.FriedmanComp(means, k, n, p)"""

    def Addhtml(self, htmlline):
        self.Saved = False
        self.AppendToPage(htmlline)
        self.WholeOutString = self.WholeOutString+htmlline + '\n'

    def write(self, TextIn):
        TextIn = '<br>'+TextIn
        self.Addhtml(TextIn)

    def LoadHtmlPage(self, event):
        dlg = wxFileDialog(self, "Load Output File", "","","*.html|*.*", \
                           wxOPEN)
        if dlg.ShowModal() == wxID_OK:
            outputfilename = dlg.GetPath()
            self.LoadPage(outputfilename)
            inits.update({'opendir': dlg.GetDirectory()})

    def SaveHtmlPage(self, event):
        dlg = wxFileDialog(self, "Save Output","","","*.html|*>*",wxSAVE)
        if dlg.ShowModal() == wxID_OK:
            outputfilename = dlg.GetPath()
            fout = open(outputfilename, "w")
            fout.write(self.WholeOutString)
            fout.close()
            inits.update({'savedir': dlg.GetDirectory()})
            self.Saved = True

    def PrintHtmlPage(self, event):
        dlg = wxPrintDialog(self)
        if dlg.ShowModal() == wxID_OK:
            None #null

    def GoBack(self, event):
        if self.HistoryCanBack():
            self.HistoryBack()

    def GoForward(self, event):
        if self.HistoryCanForward():
            self.HistoryForward()

#---------------------------------------------------------------------------
# output window w/html class for output. Also has status bar and menu.Opens
# in new frame
class OutputSheet(wx.Frame):
    def __init__(self, parent, id):
        dimx = int(inits.get('outputsizex'))
        dimy = int(inits.get('outputsizey'))
        posx = int(inits.get('outputposx'))
        posy = int(inits.get('outputposy'))
        wx.Frame.__init__(self, parent, -1, "SalStat Statistics - Output", \
                          size=(dimx, dimy), pos=(posx, posy))
        #set icon for frame (needs x-platform separator!
        icon = images.getIconIcon()
        self.SetIcon(icon)
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        pref_menu = wx.Menu()
        help_menu = wx.Menu()
        file_menu.Append(ID_FILE_NEW, '&New')
        file_menu.Append(ID_OFILE_OPEN, '&Open...')
        file_menu.Append(ID_OFILE_SAVE, '&Save')
        file_menu.Append(ID_OFILE_SAVEAS, 'Save &As...')
        file_menu.Append(ID_OFILE_PRINT, '&Print...')
        file_menu.Append(ID_OFILE_CLOSE, '&Close')
        edit_menu.Append(ID_OEDIT_CUT, 'Cu&t')
        edit_menu.Append(ID_OEDIT_COPY, '&Copy')
        edit_menu.Append(ID_OEDIT_PASTE, '&Paste')
        edit_menu.Append(ID_OEDIT_SELECTALL, 'Select &All')
        help_menu.Append(ID_HELP_WIZARD, '&What Test Should I Use...')
        help_menu.Append(ID_HELP_TOPICS, '&Topics...')
        help_menu.Append(ID_HELP_LICENCE, '&Licence...')
        help_menu.Append(ID_HELP_ABOUT, '&About...')
        omenuBar = wx.MenuBar()
        omenuBar.Append(file_menu, '&File')
        omenuBar.Append(edit_menu, '&Edit')
        omenuBar.Append(pref_menu, '&Pref')
        omenuBar.Append(help_menu, '&Help')
        self.SetMenuBar(omenuBar)
        #wxInitAllImageHandlers()
        NewIcon = images.getNewBitmap()
        OpenIcon = images.getOpenBitmap()
        SaveAsIcon = images.getSaveAsBitmap()
        PrintIcon = images.getPrintBitmap()
        HelpIcon = images.getHelpBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORZ_LAYOUT| \
                                     wx.TB_3DBUTTONS)
        toolBar.AddSimpleTool(401, NewIcon,"New","New Data Sheet in \
                                    separate window")
        toolBar.AddSimpleTool(402, OpenIcon,"Open","Open Data from a File")
        toolBar.AddSimpleTool(403, SaveAsIcon,"Save As","Save Data under \
                                    a new filename")
        toolBar.AddSimpleTool(404, PrintIcon,"Print","Print Out Results")
        toolBar.AddSimpleTool(405, HelpIcon, "Help", "Get some help!")
        toolBar.SetToolBitmapSize((24,24))
        # more toolbuttons are needed: New Output, Save, Print, Cut, \
        # Variables, and Wizard creates the toolbar
        toolBar.Realize()
        self.SetToolBar(toolBar)
        self.CreateStatusBar()
        self.SetStatusText('SalStat Statistics')
        self.htmlpage = MyHtmlWindow(self, -1)
        self.htmlpage.Addhtml('<P><B>SalStat Statistics</B></P>')
        ##self.printer = wx.html.html()
        self.Bind(wx.EVT_MENU, self.htmlpage.SaveHtmlPage, id = ID_FILE_SAVEAS)
        ##EVT_CLOSE(self, self.DoNothing)
        self.Bind(wx.EVT_MENU, self.ClearAll, id = ID_FILE_NEW, )
        self.Bind(wx.EVT_MENU, self.PrintOutput, id = ID_OFILE_PRINT)
        self.Bind(wx.EVT_MENU,  self.htmlpage.LoadHtmlPage, id = ID_FILE_OPEN)
        self.Bind(wx.EVT_MENU, frame.GoHelpAboutFrame, id = ID_HELP_ABOUT)
        self.Bind(wx.EVT_MENU, frame.GoHelpWizardFrame, id =  ID_HELP_WIZARD)
        self.Bind(wx.EVT_MENU, frame.GoHelpTopicsFrame, id = ID_HELP_TOPICS)
        self.Bind(wx.EVT_MENU, frame.GoHelpLicenceFrame, id  = ID_HELP_LICENCE)


        self.Bind(wx.EVT_TOOL_ENTER, self.ClearAll,  id = 401)
        self.Bind(wx.EVT_TOOL_ENTER, self.htmlpage.LoadHtmlPage, id = 402)
        self.Bind(wx.EVT_TOOL_ENTER, self.htmlpage.SaveHtmlPage, id =  403)
        self.Bind(wx.EVT_TOOL_ENTER, self.PrintOutput, id = 404)
        self.Bind(wx.EVT_TOOL_ENTER,  frame.GoHelpTopicsFrame, id= 405)

    def PrintOutput(self, event):
        data = wxPrintDialogData()
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)
        data.EnableSelection(True)
        dlg = wxPrintDialog(output, data)
        if dlg.ShowModal() == wxID_OK:
            #print out html
            self.printer.PrintText(self.htmlpage.WholeOutString)
        dlg.Destroy()

    def DoNothing(self, event):
        pass

    def ClearAll(self, event):
        # check output has been saved
        self.htmlpage.SetPage('<P><B>SalStat Statistics</B></P>')
        self.htmlpage.WholeOutString = ''

#---------------------------------------------------------------------------
# user selects which cols to analyse, and what stats to have
class DescriptivesFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, \
                           "Descriptive Statistics", \
                           size=(500,400+wind))
        x = self.GetClientSize()
        winheight = x[1]
        icon = images.getIconIcon()
        self.SetIcon(icon)
        ColumnList, self.colnums  = frame.grid.GetUsedCols()
        # ColumnList is the col headings, colnums is the column numbers
        l0 = wxStaticText(self,-1,"Select Column(s) to Analyse",pos=(10,10))
        l4 = wxStaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.DescChoice = DescChoiceBox(self, 1107)
        self.ColChoice = wxCheckListBox(self,1102, wxPoint(10,30), \
                                        wxSize(230,(winheight * 0.8)), ColumnList)
        okaybutton = wxButton(self,1103,"Okay",wxPoint(10,winheight-35),\
                              wxSize(BWidth, BHeight))
        cancelbutton = wxButton(self,1104,"Cancel",wxPoint(100,winheight-35),\
                                wxSize(BWidth, BHeight))
        if wxPlatform == '__WXMSW__': 
            # Darn! Some cross-platform voodoo needed...
            allbutton = wxButton(self, 105, "Select All", wxPoint(250,winheight-70),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 106, "Select None", wxPoint(360,winheight-70),\
                                  wxSize(BWidth, BHeight))
        else:
            allbutton = wxButton(self, 105, "Select All", wxPoint(250,winheight-50),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 106, "Select None", wxPoint(360,winheight-50),\
                                  wxSize(BWidth, BHeight))
        EVT_BUTTON(okaybutton, 1103, self.OnOkayButton)
        EVT_BUTTON(cancelbutton, 1104, self.OnCloseContDesc)
        EVT_BUTTON(allbutton, 105, self.DescChoice.SelectAllDescriptives)
        EVT_BUTTON(nonebutton, 106, self.DescChoice.SelectNoDescriptives)

    def OnOkayButton(self, event):
        descs = []
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                name = frame.grid.m_grid.GetColLabelValue(i)
                descs.append(salstat_stats.FullDescriptives( \
                    frame.grid.CleanData(i), name, \
                    frame.grid.missing))
        ManyDescriptives(self, descs)
        self.Close(True)

    def OnCloseContDesc(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# Same as DescriptivesContinuousFrame, but for nominal descriptives
class OneConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "One Condition Tests", \
                           size=(500,400+wind))
        x = self.GetClientSize()
        winheight = x[1]
        icon = images.getIconIcon()
        self.SetIcon(icon)
        ColumnList, self.colnums = frame.grid.GetUsedCols()
        self.ColBox = wxChoice(self, 101,(10,30), (110,20), choices = ColumnList)
        self.ColBox.SetSelection(0)
        cID = wx.ID_ANY
        l0 = wxStaticText(self,-1,"Select Column to Analyse",pos=(10,10))
        l1 = wxStaticText(self,-1,"Choose Test(s):", pos=(10,60))
        if wxPlatform == '__WXMSW__':
            l3a = wxStaticText(self,-1,'User Hypothesised', pos=(10,335))
            l3b = wxStaticText(self,-1,'Mean:',pos=(10,352))
            self.UserMean = wxTextCtrl(self,219,pos=(140,345),size=(70,20))
            allbutton = wxButton(self, 105, "Select All", wxPoint(250,winheight-70),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 106, "Select None", wxPoint(360,winheight-70),\
                                  wxSize(BWidth, BHeight))
        else:
            l3a = wxStaticText(self,-1,'User Hypothesised', pos=(10,325))
            l3b = wxStaticText(self,-1,'Mean:',pos=(10,342))
            self.UserMean = wxTextCtrl(self,219,pos=(140,335),size=(70,20))
            allbutton = wxButton(self, 105, "Select All", wxPoint(250,winheight-50),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 106, "Select None", wxPoint(360,winheight-50),\
                                  wxSize(BWidth, BHeight))
        l4 = wxStaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        Tests = ['t-test','Sign test','Chi square test for variance']
        self.TestChoice = wxCheckListBox(self,213,wxPoint(10,80),\
                                         wxSize(230,180),Tests)
        self.hypchoice=wxRadioBox(self, 205,"Select Hypothesis",\
                                  wxPoint(10,270),wxDefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        self.okaybutton = wxButton(self,103,"Okay",wxPoint(10,winheight-35),\
                                   wxSize(BWidth, BHeight))
        #self.okaybutton.Enable(False)
        cancelbutton = wxButton(self,104,"Cancel",wxPoint(100,winheight-35),\
                                wxSize(BWidth, BHeight))
        self.DescChoice = DescChoiceBox(self, 104)
        EVT_BUTTON(self.okaybutton, 103, self.OnOkayButton)
        EVT_BUTTON(cancelbutton, 104, self.OnCloseOneCond)
        EVT_BUTTON(allbutton, 105, self.DescChoice.SelectAllDescriptives)
        EVT_BUTTON(nonebutton, 106, self.DescChoice.SelectNoDescriptives)
        # enable the okay button if something is entered as a hyp mean.
        # Can the wxTextCtrl allow only numbers to be entered?
        #EVT_TEXT(self.UserMean, 107, self.EnteredText) # doesn't work on Windows!

    def EnteredText(self, event):
        self.okaybutton.Enable(True)

    def OnOkayButton(self, event):
        x1 = self.ColBox.GetSelection()
        name = frame.grid.GetColLabelValue(x1)
        if (x1 < 0): # add top limits of grid to this
            self.Close(True)
            return
        try:
            umean = float(self.UserMean.GetValue())
        except:
            output.htmlpage.Addhtml('<p>Cannot do test - no user \
                                    hypothesised mean specified')
            self.Close(True)
            return
        x = frame.grid.CleanData(x1)
        TBase = salstat_stats.OneSampleTests(frame.grid.CleanData(x1), name, \
                                             frame.grid.missing)
        d=[0]
        d[0] = TBase.d1
        x2=ManyDescriptives(self, d)
        # One sample t-test
        if self.TestChoice.IsChecked(0):
            output.htmlpage.Addhtml('<p><b>One sample t-test</b>')
            TBase.OneSampleTTest(umean)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<br>All elements are the same, \
                                    test not possible')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<br>t(%d) = %5.3f, p (approx) = \
                                    %1.6f'%(TBase.df, TBase.t, TBase.prob))
                #now draw up the xml history stuff
                xmlevt = '<analyse test="one sample t-test" column = "'+str(x1)
                xmlevt = xmlevt+' hyp_value = "'+str(umean)+'" tail="'
                if (self.hypchoice.GetSelection() == 0):
                    xmlevt = xmlevt+'1">'
                else:
                    xmlevt = xmlevt+'2">'
                xmlevt = xmlevt+'t ('+str(TBase.df)+') = '+str(TBase.t)+', p = '+str(TBase.prob)
                xmlevt = xmlevt+'</analyse>'
                hist.AppendEvent(xmlevt)
        # One sample sign test
        if self.TestChoice.IsChecked(1):
            output.htmlpage.Addhtml('<p><b>One sample sign test</b>')
            TBase.OneSampleSignTest(x, umean)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<br>All data are the same - no \
                                    analysis is possible')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<br>N = %5.0f, z = %5.3f, p = %1.6f'%\
                                        (TBase.ntotal, TBase.z, TBase.prob))
        # chi square test for variance
        if self.TestChoice.IsChecked(2):
            output.htmlpage.Addhtml('<p><b>One sample chi square</b>')
            TBase.ChiSquareVariance(umean)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            if (TBase.prob == None):
                TBase.prob = 1.0
            output.htmlpage.Addhtml('<br>Chi square (%d) = %5.3f, p = %1.6f'%\
                                    (TBase.df, TBase.chisquare, TBase.prob))
        self.Close(True)

    def OnCloseOneCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
#dialog for 2 sample tests
class TwoConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "Two Condition Tests", \
                           size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        x = self.GetClientSize()
        icon = images.getIconIcon()
        self.SetIcon(icon)
        colsselected =  frame.grid.GetColsUsedList()
        l0 = wxStaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        l1 = wxStaticText(self, -1, "Select Test(s) to Perform:", pos=(10,60))
        if wxPlatform == '__WXMSW__':
            l3a = wxStaticText(self,-1,'User Hypothesised', pos=(10,335))
            l3b = wxStaticText(self,-1,'Mean:',pos=(10,352))
            self.UserMean = wxTextCtrl(self,219,pos=(140,345),size=(70,20))
            allbutton = wxButton(self, 218, "Select All", wxPoint(250,winheight-70),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 220, "Select None", wxPoint(360,winheight-70),\
                                  wxSize(BWidth, BHeight))
        else:
            l3a = wxStaticText(self,-1,'User Hypothesised', pos=(10,325))
            l3b = wxStaticText(self,-1,'Mean:',pos=(10,342))
            self.UserMean = wxTextCtrl(self,219,pos=(140,335),size=(70,20))
            allbutton = wxButton(self, 218, "Select All", wxPoint(250,winheight-50),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 220, "Select None", wxPoint(360,winheight-50),\
                                  wxSize(BWidth, BHeight))
        l4 = wxStaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.ColBox1 = wxChoice(self,211, (10,30), (110,20), ColumnList)
        self.ColBox2 = wxChoice(self,212, (130,30), (110,20), ColumnList)
        x1 = 0
        x2 = 1
        self.ColBox1.SetSelection(x1)
        self.ColBox2.SetSelection(x2)
        x1len = len(frame.grid.CleanData(x1))
        x2len = len(frame.grid.CleanData(x2))
        if (x1len != x2len):
            self.equallists = False
        else:
            self.equallists = True
        # list of tests in alphabetical order
        Tests = ['chi square','F test','Kolmogorov-Smirnov', \
                 'Linear Regression', 'Mann-Whitney U', \
                 'Paired Sign', 't-test paired','t-test unpaired', \
                 'Wald-Wolfowitz Runs', 'Wilcoxon Rank Sums', \
                 'Wilcoxon Signed Ranks'] # nb, paired permutation test missing
        self.paratests = wxCheckListBox(self,213,wxPoint(10,80),\
                                        wxSize(230,180),Tests)
        self.hypchoice=wxRadioBox(self, 205,"Select Hypothesis",\
                                  wxPoint(10,270),wxDefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        self.DescChoice = DescChoiceBox(self, 215)
        okaybutton = wxButton(self,216,"Okay",wxPoint(10,winheight-35), \
                              wxSize(BWidth, BHeight))
        cancelbutton = wxButton(self,217,"Cancel",wxPoint(100,winheight-35), \
                                wxSize(BWidth, BHeight))
        self.UserMean = wxTextCtrl(self,219,pos=(140,345),size=(70,20))
        # using self.equallists, if True, enable all items in the checklist \
        # box, otherwise set the within subs and correlations to be
        # disabled as they cannot be used with unequal list lengths!
        # Also disble the f-test unless something is entered into the
        # user hyp variance box
        EVT_BUTTON(okaybutton, 216, self.OnOkayButton)
        EVT_BUTTON(cancelbutton, 217, self.OnCloseTwoCond)
        EVT_BUTTON(allbutton, 218, self.DescChoice.SelectAllDescriptives)
        EVT_BUTTON(nonebutton, 220, self.DescChoice.SelectNoDescriptives)
        #EVT_CHOICE(self.ColBox1, 211, self.ChangeCol1)
        #EVT_CHOICE(self.ColBox2, 212, self.ChangeCol1)
        EVT_TEXT(self.UserMean, 219, self.ChangeText)

    def ChangeText(self, event):
        pass

    def ChangeCol1(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.CleanData(self.ColBox1.GetSelection()))
        x2 = len(frame.grid.CleanData(self.ColBox2.GetSelection()))
        if (x1 != x2):
            # disable some tests in the listbox
            self.paratests.Check(0,FALSE)
        else:
            pass
            # enable all tests in the listbox

    def ChangeCol2(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.CleanData(self.ColBox1.GetSelection()))
        x2 = len(frame.grid.CleanData(self.ColBox2.GetSelection()))
        if (x1 != x2):
            pass
        else:
            pass

    def OnOkayButton(self, event):
        x1 = self.ColBox1.GetSelection()
        y1 = self.ColBox2.GetSelection()
        name1 = frame.grid.GetColLabelValue(x1)
        name2 = frame.grid.GetColLabelValue(y1)
        if (x1 < 0) or (y1 < 0):
            self.Close(True)
            return
        x = frame.grid.CleanData(x1)
        xmiss = frame.grid.missing
        y = frame.grid.CleanData(y1)
        ymiss = frame.grid.missing
        TBase = salstat_stats.TwoSampleTests(x, y, name1, name2,xmiss,ymiss)
        d = [0,0]
        d[0] = TBase.d1
        d[1] = TBase.d2
        x2 = ManyDescriptives(self, d)
        # chi square test
        if self.paratests.IsChecked(0):
            output.htmlpage.Addhtml('<p><b>Chi square</b>')
            TBase.ChiSquare(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do chi square - \
                                    unequal data sizes')
            else:
                output.htmlpage.Addhtml('<br>chi (%d) = %5.3f, p = %1.6f'% \
                                        (TBase.df, TBase.chisq, TBase.prob))

        # F-test for variance ratio's
        if self.paratests.IsChecked(1):
            output.htmlpage.Addhtml('<P><B>F test for variance ratio (\
                                    independent samples)</B>')
            try:
                umean = float(self.UserMean.GetValue())
            except:
                output.htmlpage.Addhtml('<p>Cannot do test - no user \
                                    hypothesised mean specified')
            else:
                TBase.FTest(umean)
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>f(%d, %d) = %5.3f, p = %1.6f'% \
                                        (TBase.df1,TBase.df2, TBase.f, TBase.prob))

        # Kolmorogov-Smirnov 2 sample test
        if self.paratests.IsChecked(2):
            output.htmlpage.Addhtml('<P><B>Kolmogorov-Smirnov test \
                                    (unpaired)</B>')
            TBase.KolmogorovSmirnov()
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<BR>D = %5.3f, p = %1.6f'%(TBase.d, \
                                                                TBase.prob))

        # Linear Regression
        if self.paratests.IsChecked(3):
            output.htmlpage.Addhtml('<p><b>Linear Regression</b>')
            TBase.LinearRegression(x,y)
            #s, i, r, prob, st = salstat_stats.llinregress(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do linear regression - \
                                    unequal data sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    self.prob = self.prob / 2
                output.htmlpage.Addhtml('<BR>Slope = %5.3f, Intercept = %5.3f,\
                                    r = %5.3f, Estimated Standard Error = \
                                    %5.3f' %(TBase.slope, TBase.intercept, \
                                             TBase.r, TBase.sterrest))
                output.htmlpage.Addhtml('<br>t (%d) = %5.3f, p = %1.6f' \
                                        %(TBase.df, TBase.t, TBase.prob))
        # Mann-Whitney U
        if self.paratests.IsChecked(4):
            output.htmlpage.Addhtml('<P><B>Mann-Whitney U test (unpaired \
                                    samples)</B>')
            TBase.MannWhitneyU(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do Mann-Whitney U test \
                                    - all numbers are identical')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>z = %5.3f, small U = %5.3f, \
                                    big U = %5.3f, p = %1.6f'%(TBase.z, \
                                                               TBase.smallu, TBase.bigu, TBase.prob))

        # Paired permutation test
        """if self.paratests.IsChecked(5):
            output.htmlpage.Addhtml('<P><B>Paired Permutation test</B></P>')
            TBase.PairedPermutation(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do test - not paired \
                                    samples')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>Utail = %5.0f, nperm = %5.3f, \
                        crit = %5.3f, p = %1.6f'%(TBase.utail, TBase.nperm, \
                        TBase.crit, TBase.prob))"""

        # Paired sign test
        if self.paratests.IsChecked(5):
            output.htmlpage.Addhtml('<P><B>2 sample sign test</B></P>')
            TBase.TwoSampleSignTest(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do test - not paired \
                                    samples')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>N = %5.0f, z = %5.3f, p = %1.6f'\
                                        %(TBase.ntotal, TBase.z, TBase.prob))

        # Paired t-test
        if self.paratests.IsChecked(6):
            output.htmlpage.Addhtml('<p><b>t-test paired</b>')
            TBase.TTestPaired(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<br>Cannot do paired t test - \
                                    unequal data sizes')
            else:
                if self.hypchoice.GetSelection() == 0:
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>t(%d) = %5.3f, p = %1.6f'% \
                                        (TBase.df, TBase.t, TBase.prob))

        # unpaired t-test
        if self.paratests.IsChecked(7):
            output.htmlpage.Addhtml('<p><b>t-test unpaired</b>')
            TBase.TTestUnpaired()
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<BR>t(%d) = %5.3f, p =  %1.6f'% \
                                    (TBase.df, TBase.t, TBase.prob))

        # Wald-Wolfowitz runs test (no yet coded)
        if self.paratests.IsChecked(8):
            pass

        # Wilcoxon Rank Sums
        if self.paratests.IsChecked(9):
            output.htmlpage.Addhtml('<P><B>Rank Sums test (unpaired \
                                    samples)</B>')
            TBase.RankSums(x, y)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<BR>t = %5.3f, p = %1.6f'%(TBase.z, \
                                                                TBase.prob))

        # Wilcoxon Signed Ranks
        if self.paratests.IsChecked(10):
            output.htmlpage.Addhtml('<P><B>Wilcoxon t (paired samples)</B>')
            TBase.SignedRanks(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do Wilcoxon t test - \
                                    unequal data sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>z = %5.3f, t = %5.3f, p = %1.6f'%\
                                        (TBase.z, TBase.wt, TBase.prob))
        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# dialog for single factor tests with 3+ conditions
class ThreeConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "Three Condition Tests", \
                           size = (500,400+wind))
        x = self.GetClientSize()
        winheight = x[1]
        icon = images.getIconIcon()
        self.SetIcon(icon)
        alltests = ['anova between subjects','anova within subjects',\
                    'Kruskall Wallis','Friedman test',\
                    'Cochranes Q']
        ColumnList, self.colnums = frame.grid.GetUsedCols()
        l0 = wxStaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        #l1 = wxStaticText(self, -1, "Select IV:", pos=(10,60))
        l2 = wxStaticText(self, -1, "Select Data", pos=(10,170))
        l4 = wxStaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        if wxPlatform == '__WXMSW__':
            allbutton = wxButton(self, 518, "Select All", wxPoint(250,winheight-70),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 520, "Select None", wxPoint(360,winheight-70),\
                                  wxSize(BWidth, BHeight))
        else:
            allbutton = wxButton(self, 518, "Select All", wxPoint(250,winheight-50),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 520, "Select None", wxPoint(360,winheight-50),\
                                  wxSize(BWidth, BHeight))

        self.TestChoice = wxCheckListBox(self, 514,wxPoint(10,190), \
                                         wxSize(230,120),alltests)
        self.hypchoice=wxRadioBox(self, 205,"Select Hypothesis",\
                                  wxPoint(10,320),wxDefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        self.ColChoice = wxCheckListBox(self,511, wxPoint(10,30), \
                                        wxSize(230,130), ColumnList)
        for i in range(len(self.colnums)):
            self.ColChoice.Check(i, True)
        self.DescChoice = DescChoiceBox(self, 512)
        okaybutton = wxButton(self,516,"Okay",wxPoint(10,winheight-35), \
                              wxSize(BWidth, BHeight))
        cancelbutton = wxButton(self,517,"Cancel",wxPoint(100,winheight-35), \
                                wxSize(BWidth, BHeight))
        EVT_BUTTON(okaybutton, 516, self.OnOkayButton)
        EVT_BUTTON(cancelbutton, 517, self.OnCloseThreeCond)
        EVT_BUTTON(allbutton, 518, self.DescChoice.SelectAllDescriptives)
        EVT_BUTTON(nonebutton, 520, self.DescChoice.SelectNoDescriptives)

    def OnOkayButton(self, event):
        biglist = []
        ns = []
        sums = []
        means = []
        names = []
        miss = []
        k = 0
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                k = k + 1
                tmplist = frame.grid.CleanData(self.colnums[i])
                miss.append(frame.grid.missing)
                biglist.append(tmplist)
                names.append(frame.grid.GetColLabelValue(i))
        k = len(biglist)
        d = []
        for i in range(k):
            x2=salstat_stats.FullDescriptives(biglist[i], names[i], miss[i])
            ns.append(x2.N)
            sums.append(x2.sum)
            means.append(x2.mean)
            d.append(x2)
        x2=ManyDescriptives(self, d)
        if (len(biglist) < 2):
            output.htmlpage.Addhtml('<p><b>Not enough columns selected for \
                                    test!</b>')
            self.Close(True)
            return
        TBase = salstat_stats.ThreeSampleTests()
        #single factor between subjects anova
        if self.TestChoice.IsChecked(0):
            cols = []
            output.htmlpage.Addhtml('<P><B>Single Factor anova - between \
                                    subjects</B></P>')
            output.htmlpage.Addhtml('<P><i>Warning!</i> This test is based \
                                    on the following assumptions:')
            output.htmlpage.Addhtml('<P>1) Each group has a normal \
                                    distribution of observations')
            output.htmlpage.Addhtml('<P>2) The variances of each observation \
                                    are equal across groups (homogeneity of \
                                    variance)')
            output.htmlpage.Addhtml('<P>3) The observations are statistically \
                                    independent')
            TBase.anovaBetween(d)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<table border="1"><tr><td></td><td>SS \
                                    </td><td>df</td><td>MS</td><td>F</td>  \
                                    <td>p-value</TD></tr>')
            output.htmlpage.Addhtml('<tr><td>FACTOR</td><td>%5.3f</td><td> \
                                    %5d</td><td>%5.3f</td><td>%5.3f</td>   \
                                    <td>%1.6f</td></tr>'%(TBase.SSbet,     \
                                                          TBase.dfbet, TBase.MSbet, TBase.F,\
                                                          TBase.prob))
            output.htmlpage.Addhtml('<tr><td>Error</td><td>%5.3f</td><td>  \
                                    %5d</td><td>%5.3f</td><td></td><td>    \
                                    </td></tr>'%(TBase.SSwit, TBase.dferr, \
                                                 TBase.MSerr))
            output.htmlpage.Addhtml('<tr><td>Total</td><td>%5.3f</td><td>  \
                                    %5d</td><td></td><td></td><td></td></tr>\
                                    </table>'%(TBase.SStot, TBase.dftot))
        # single factor within subjects anova
        if self.TestChoice.IsChecked(1):
            output.htmlpage.Addhtml('<P><B>Single Factor anova - within  \
                                    subjects</b></P>')
            output.htmlpage.Addhtml('<P><i>Warning!</i> This test is based \
                                    on the following assumptions:')
            output.htmlpage.Addhtml('<P>1) Each group has a normal \
                                    distribution of observations')
            output.htmlpage.Addhtml('<P>2) The variances of each observation \
                                    are equal across groups (homogeneity of \
                                    variance)')
            output.htmlpage.Addhtml('<P>3) The observations are statistically \
                                    indpendent')
            output.htmlpage.Addhtml('<P>4) The variances of each participant \
                                    are equal across groups (homogeneity of \
                                    covariance)')
            TBase.anovaWithin(biglist, ns, sums, means)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<table border="1"><tr><td></td><td>SS \
                                    </td><td>df</td><td>MS</td><td>F</td>  \
                                    <td>p-value</TD></tr>')
            output.htmlpage.Addhtml('<tr><td>FACTOR</td><td>%5.3f</td><td> \
                                    %5d</td><td>%5.3f</td><td>%5.3f</td>   \
                                    <td>%1.6f</td></tr>'%(TBase.SSbet,  \
                                                          TBase.dfbet, TBase.MSbet, TBase.F,  \
                                                          TBase.prob))
            output.htmlpage.Addhtml('<tr><td>Within</td><td>%5.3f</td><td>%5d\
                                    </td><td>%5.3f</td><td></td><td></td> \
                                    </tr>'%(TBase.SSwit, TBase.dfwit,     \
                                            TBase.MSwit))
            output.htmlpage.Addhtml('<tr><td>Error</td><td>%5.3f</td><td> \
                                    %5d</td><td>%5.3f</td><td></td><td></td> \
                                    </tr>'%(TBase.SSres, TBase.dfres,   \
                                            TBase.MSres))
            output.htmlpage.Addhtml('<tr><td>Total</td><td>%5.3f</td><td>%5d \
                                    </td><td></td><td></td><td></td>'% \
                                                                     (TBase.SStot, TBase.dftot))
            output.htmlpage.Addhtml('</table>')

        # kruskal wallis H
        if self.TestChoice.IsChecked(2):
            output.htmlpage.Addhtml('<p><b>Kruskal Wallis H Test</b>')
            TBase.KruskalWallisH(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<br>H(%d) = %5.3f, p = %1.6f'% \
                                    (TBase.df, TBase.h, TBase.prob))

        # Friedman test
        if self.TestChoice.IsChecked(3):
            output.htmlpage.Addhtml('<p><b>Friedman Chi Square</b>')
            TBase.FriedmanChiSquare(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
                alpha = 0.10
            else:
                alpha = 0.05
            output.htmlpage.Addhtml('<br>Chi(%d) = %5.3f, p = %1.6f'% \
                                    (TBase.df, TBase.chisq, TBase.prob))
            # the next few lines are commented out & are experimental. They
            # help perform multiple comparisons for the Friedman test.
            #outstring = '<a href="friedman,'
            #for i in range(k):
            #    outstring = outstring+'M,'+str(TBase.sumranks[i])+','
            #outstring = outstring+'k,'+str(k)+','
            #outstring = outstring+'n,'+str(d[0].N)+','
            #outstring = outstring+'p,'+str(alpha)+'">Multiple Comparisons</a>'
            #output.htmlpage.Addhtml('<p>'+outstring+'</p>')

        # Cochranes Q
        if self.TestChoice.IsChecked(4):
            output.htmlpage.Addhtml('<p><b>Cochranes Q</b>')
            TBase.CochranesQ(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<br>Q (%d) = %5.3f, p = %1.6f'% \
                                    (TBase.df, TBase.q, TBase.prob))
        self.Close(True)

    def OnCloseThreeCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
class CorrelationTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        winheight = 500 + wind
        wx.Dialog.__init__(self, parent, id, "Correlations", \
                           size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        icon = images.getIconIcon()
        self.SetIcon(icon)
        colsselected =  frame.grid.GetColsUsedList()
        l0 = wxStaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        l1 = wxStaticText(self, -1, "Select Test(s) to Perform:", pos=(10,60))
        # No user hypothesised mean / variance needed here!
        if wxPlatform == '__WXMSW__':
            allbutton = wxButton(self, 218, "Select All", wxPoint(250,winheight-70),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 220, "Select None", wxPoint(360,winheight-70),\
                                  wxSize(BWidth, BHeight))
        else:
            allbutton = wxButton(self, 218, "Select All", wxPoint(250,winheight-50),\
                                 wxSize(BWidth, BHeight))
            nonebutton = wxButton(self, 220, "Select None", wxPoint(360,winheight-50),\
                                  wxSize(BWidth, BHeight))
        l4 = wxStaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.ColBox1 = wxComboBox(self,211,"Select Column", wxPoint(10,30),\
                                  wxSize(110,20),ColumnList)
        self.ColBox2 = wxComboBox(self,212,"Select Column",wxPoint(130,30),\
                                  wxSize(110,20),ColumnList)
        x1 = 0
        x2 = 1
        self.ColBox1.SetSelection(x1)
        self.ColBox2.SetSelection(x2)
        x1len = len(frame.grid.CleanData(x1))
        x2len = len(frame.grid.CleanData(x2))
        if (x1len != x2len):
            self.equallists = False
        else:
            self.equallists = True
        # list of tests in alphabetical order
        Tests = ['Kendalls tau','Pearsons correlation','Point Biserial r', \
                 'Spearmans rho']
        self.paratests = wxCheckListBox(self,213,wxPoint(10,80),\
                                        wxSize(230,180),Tests)
        self.hypchoice=wxRadioBox(self, 205,"Select Hypothesis",\
                                  wxPoint(10,270),wxDefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        self.DescChoice = DescChoiceBox(self, 215)
        okaybutton = wxButton(self,216,"Okay",wxPoint(10,winheight-35), \
                              wxSize(BWidth, BHeight))
        cancelbutton = wxButton(self,217,"Cancel",wxPoint(100,winheight-35), \
                                wxSize(BWidth, BHeight))
        EVT_BUTTON(okaybutton, 216, self.OnOkayButton)
        EVT_BUTTON(cancelbutton, 217, self.OnCloseTwoCond)
        EVT_BUTTON(allbutton, 218, self.DescChoice.SelectAllDescriptives)
        EVT_BUTTON(nonebutton, 220, self.DescChoice.SelectNoDescriptives)
        EVT_COMBOBOX(self.ColBox1, 211, self.ChangeCol1)
        EVT_COMBOBOX(self.ColBox2, 212, self.ChangeCol1)

    def ChangeCol1(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.CleanData(self.ColBox1.GetSelection()))
        x2 = len(frame.grid.CleanData(self.ColBox2.GetSelection()))
        if (x1 != x2):
            print "unequal"
            # disable some tests in the listbox
        else:
            print "equal"
            # enable all tests in the listbox

    def ChangeCol2(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        x1 = len(frame.grid.CleanData(self.ColBox1.GetSelection()))
        x2 = len(frame.grid.CleanData(self.ColBox2.GetSelection()))
        if (x1 != x2):
            print "unequal"
        else:
            print "equal"

    def OnOkayButton(self, event):
        x1 = self.ColBox1.GetSelection()
        y1 = self.ColBox2.GetSelection()
        name1 = frame.grid.GetColLabelValue(x1)
        name2 = frame.grid.GetColLabelValue(y1)
        if (x1 < 0) or (y1 < 0):
            self.Close(True)
            return
        x = frame.grid.CleanData(x1)
        xmiss = frame.grid.missing
        y = frame.grid.CleanData(y1)
        ymiss = frame.grid.missing
        TBase = salstat_stats.TwoSampleTests(x, y, name1, name2,xmiss,ymiss)
        d = [0,0]
        d[0] = TBase.d1
        d[1] = TBase.d2
        x2 = ManyDescriptives(self, d)
        # Kendalls tau correlation
        if self.paratests.IsChecked(0):
            output.htmlpage.Addhtml('<P><B>Kendalls Tau correlation</B>')
            TBase.KendallsTau(x, y)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<BR>tau = %5.3f, z = %5.3f, p = %1.6f'% \
                                    (TBase.tau, TBase.z, TBase.prob))

        # Pearsons r correlation
        if self.paratests.IsChecked(1):
            output.htmlpage.Addhtml('<P><B>Pearsons correlation</B>')
            TBase.PearsonsCorrelation(x, y)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            output.htmlpage.Addhtml('<BR>r (%d) = %5.3f, t = %5.3f, p = %1.6f'% \
                                    (TBase.df, TBase.r, TBase.t, TBase.prob))

        # Point Biserial r
        if self.paratests.IsChecked(2):
            pass
        # Spearmans rho correlation
        if self.paratests.IsChecked(3):
            output.htmlpage.Addhtml('<P><B>Spearmans rho correlation</B>')
            TBase.SpearmansCorrelation(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do Spearmans correlation \
                                    - unequal data sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>rho(%d) = %5.3f, p = %1.6f'% \
                                        (TBase.df, TBase.rho, TBase.prob))

        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
class MFanovaFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Multi-factorial anova", \
                           size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        icon = images.getIconIcon()
        self.SetIcon(icon)
        ColumnList, self.colnums = frame.grid.GetUsedCols()
        l0 = wxStaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        l1 = wxStaticText(self, -1, "Select IV:", pos=(10,60))
        l2 = wxStaticText(self, -1, "Select DV", pos=(10,170))
        l4 = wxStaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.IVbox = wxCheckListBox(self, 413,wxPoint(10,30),\
                                    wxSize(230,130),ColumnList)
        self.DVbox = wxCheckListBox(self, 414,wxPoint(10,190), \
                                    wxSize(230,120),ColumnList)
        self.hypchoice=wxRadioBox(self, 205,"Select Hypothesis",\
                                  wxPoint(10,320),wxDefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        #self.DescChoice = DescChoiceBox(self, 215)
        # I might leave the descriptives out and implement a feedback box
        # that tells the user about the analysis (eg, how many factors, # 
        # levels per factor, # interactions etc which might be useful. It
        # would be updated whenever the user changes a selection.
        okaybutton = wxButton(self,216,"Okay",wxPoint(10,winheight-35), \
                              wxSize(BWidth, BHeight))
        cancelbutton = wxButton(self,217,"Cancel",wxPoint(100,winheight-35), \
                                wxSize(BWidth, BHeight))
        allbutton = wxButton(self, 218,"Select All",wxPoint(250,winheight-70),\
                             wxSize(BWidth, BHeight))
        nonebutton = wxButton(self, 220, "Select None", wxPoint(360, \
                                                                winheight-70),wxSize(BWidth, BHeight))
        self.DescChoice = DescChoiceBox(self, 104)
        EVT_BUTTON(okaybutton, 216, self.OnOkayButton)
        EVT_BUTTON(cancelbutton, 217, self.OnCloseTwoCond)
        EVT_BUTTON(allbutton, 218, self.DescChoice.SelectAllDescriptives)
        EVT_BUTTON(nonebutton, 220, self.DescChoice.SelectNoDescriptives)
        # Need to check that a col ticked in one box is not ticked in the other
        #EVT_CHECKLISTBOX(self.IVbox, 413, self.CheckforIXbox)
        #EVT_CHECKLISTBOX(self.DVbox,414,self.CheckforDVbox)

    def OnOkayButton(self, event):
        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# instance of the tool window that contains the test buttons
# note this is experimental and may not be final
class TestFrame(wx.MiniFrame):
    def __init__(self, parent, title):
        self.parent = parent
        wx.MiniFrame.__init__(self, parent, -1, 'Tests', size=(120,400), pos=(5,5))
        descButton = wxButton(self, 151,'Descriptives (F1)',wxPoint(0,0),wxSize(115,40))
        sign1Button=wxButton(self,153,'sign test 1 sample',wxPoint(0,40),wxSize(115,40))
        ttestpairedButton=wxButton(self,154,'t-test paired <F2>',wxPoint(0,80),wxSize(115,40))
        ttestunpairedButton = wxButton(self, 155, 't-test unpaired <F3>',wxPoint(0,120),wxSize(115,40))
        chisquareButton = wxButton(self,156,'Chi square <F4>',wxPoint(0,160),wxSize(155,40))
        mannwhitneyButton=wxButton(self,157,'Mann-Whitney U',wxPoint(0,200),wxSize(115,40))
        kolmogorovButton=wxButton(self,158,'Kolmogorov-Smirnov',wxPoint(0,240),wxSize(115,40))
        anovaButton=wxButton(self,159,'anova between',wxPoint(0,280),wxSize(115,40))
        anovaWButton=wxButton(self,160,'anova within',wxPoint(0,320),wxSize(115,40))
        # and so on...
        # only put keyboard shortcuts for the most required ones. DONT allow the user to change this
        EVT_CLOSE(self, self.DoNothing)
        EVT_BUTTON(descButton, 151, self.GetDescriptives)

    def DoNothing(self, event):
        pass

    def GetDescriptives(self, event):
        print self.parent.grid.GetSelectedCols()

#---------------------------------------------------------------------------
class TransformFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Transformations", \
                           size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        icon = images.getIconIcon()
        self.SetIcon(icon)
        self.transform = ""
        self.transformName = ""
        self.ColumnList, self.colnums = frame.grid.GetUsedCols()
        self.cols = frame.grid.GetNumberCols()
        l0 = wxStaticText(self,-1,"Select Columns to Transform",pos=(10,10))
        self.ColChoice = wxCheckListBox(self,1102, wxPoint(10,30), \
                                        wxSize(230,(winheight * 0.8)), self.ColumnList)
        okaybutton = wxButton(self,1105,"Okay",wxPoint(10,winheight-35),\
                              wxSize(BWidth, BHeight))
        cancelbutton = wxButton(self,1106,"Cancel",wxPoint(100,winheight-35),\
                                wxSize(BWidth, BHeight))
        # common transformations:
        l1 = wxStaticText(self, -1, "Common Transformations:", pos=(250,30))
        squareRootButton = wxButton(self, 1110, "Square Root", wxPoint(250, 60), \
                                    wxSize(BWidth, BHeight))
        logButton = wxButton(self, 1111, "Logarithmic",wxPoint(250, 100), \
                             wxSize(BWidth, BHeight))
        reciprocalButton = wxButton(self, 1112, "Reciprocal", wxPoint(250,140), \
                                    wxSize(BWidth, BHeight))
        squareButton = wxButton(self, 1113, "Square", wxPoint(250,180), \
                                wxSize(BWidth, BHeight))
        l2 = wxStaticText(self, -1, "Function :", wxPoint(250, 315)) 
        self.transformEdit = wxTextCtrl(self,1114,pos=(250,335),size=(150,20))
        EVT_BUTTON(okaybutton, 1105, self.OnOkayButton)
        EVT_BUTTON(cancelbutton, 1106, self.OnCloseFrame)
        EVT_BUTTON(squareRootButton, 1110, self.squareRootTransform)
        EVT_BUTTON(logButton , 1111, self.logTransform)
        EVT_BUTTON(reciprocalButton, 1112, self.reciprocalTransform)
        EVT_BUTTON(squareButton, 1113, self.squareTransform)

    def squareRootTransform(self, event):
        self.transform = "math.sqrt(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Square Root"

    def logTransform(self, event):
        self.transform = "math.log(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Logarithm"

    def reciprocalTransform(self, event):
        self.transform = "1 / x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Reciprocal"

    def squareTransform(self, event):
        self.transform = "x * x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Square"

    def OnOkayButton(self, event):
        pass # start transforming!
        # process: collect each selected column, then pass the contents through the self.transform function
        # then put the resulting column into a new column, and retitle it with the original variable 
        # name plus the function.
        self.transform = self.transformEdit.GetValue()
        cols = range(self.cols)
        emptyCols = []
        for i in cols:
            if cols[i] not in self.colnums:
                emptyCols.append(cols[i])
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                oldcol = frame.grid.CleanData(i)
                newcol = [0]*len(oldcol)
                for j in range(len(oldcol)):
                    x = oldcol[j]
                    try:
                        newcol[j] = eval(self.transform)
                    except: # which exception would this be?
                        pass # need to do something here.
                PutData(emptyCols[i], newcol)
                # put in a nice new heading
                oldHead = frame.grid.GetColLabelValue(self.colnums[i])
                if self.transformName == "":
                    self.transformName = ' ' + self.transform
                oldHead = oldHead + self.transformName
                frame.grid.SetColLabelValue(emptyCols[i], oldHead)
                emptyCols.pop(emptyCols[i])
        self.Close(True)

    def OnCloseFrame(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# Plot Window
# This frame holds the plots using the wxPlotCanvas widget
class PlotFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1,"SalStat Plot (Basic!)", \
                          size=(500,400))
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        title_menu = wx.Menu()
        file_menu.Append(ID_FILE_GSAVEAS, 'Save &As...')
        file_menu.Append(ID_FILE_GPRINTSETUP, 'Page Setup...')
        file_menu.Append(ID_FILE_GPRINTPREVIEW, 'Print Preview...')
        file_menu.Append(ID_FILE_GPRINT, '&Print...')
        file_menu.Append(ID_FILE_GCLOSE, '&Close')
        title_menu.Append(ID_TITLE_GTITLE, '&Graph Title...')
        title_menu.Append(ID_TITLE_GXAXIS, '&X Axis Label...')
        title_menu.Append(ID_TITLE_GYAXIS, '&Y Axis Label...')
        title_menu.Append(ID_TITLE_LEGEND, '&Enable Legend', kind=wx.wxITEM_CHECK)
        title_menu.Append(ID_TITLE_GRID, 'Enable &Grid', kind=wx.wxITEM_CHECK)
        gmenuBar = wx.Menur()
        gmenuBar.Append(file_menu, '&File')
        gmenuBar.Append(edit_menu, '&Edit')
        gmenuBar.Append(title_menu, '&Plot')
        self.Bind(wx.EVT_MENU, ID_FILE_GSAVEAS, self.SaveAs)
        self.Bind(wx.EVT_MENU, ID_FILE_GPRINTSETUP, self.PrintSetup)
        self.Bind(wx.EVT_MENU, ID_FILE_GPRINTPREVIEW, self.PrintPreview)
        self.Bind(wx.EVT_MENU, ID_FILE_GPRINT, self.PrintGraph)
        self.Bind(wx.EVT_MENU, ID_FILE_GCLOSE, self.CloseWindow)
        self.Bind(wx.EVT_MENU, ID_TITLE_GTITLE, self.SetTitle)
        self.Bind(wx.EVT_MENU, ID_TITLE_GXAXIS, self.SetXAxis)
        self.Bind(wx.EVT_MENU, ID_TITLE_GYAXIS, self.SetYAxis)
        self.Bind(wx.EVT_MENU, ID_TITLE_LEGEND, self.EnableLegend)
        self.Bind(wx.EVT_MENU, ID_TITLE_GRID, self.EnableGrid)
        self.SetMenuBar(gmenuBar)
        self.client = pyplot.PlotCanvas(self)

    def EnableGrid(self, event):
        self.client.SetEnableGrid(event.IsChecked())

    def SetTitle(self, event):
        dlg = wxTextEntryDialog(self, 'Enter the graph title','Graph Title')
        dlg.SetValue(self.client.getTitle())
        # the previous line doesn't work.
        if dlg.ShowModal() == wxID_OK:
            self.client.setTitle(dlg.GetValue())

    def SetXAxis(self, event):
        pass

    def SetYAxis(self, event):
        pass

    def EnableLegend(self, event):
        self.client.SetEnableLegend(event.IsChecked())

    def PrintSetup(self, event):
        self.client.PageSetup()

    def PrintPreview(self, event):
        self.client.PrintPreview()

    def PrintGraph(self, event):
        self.client.Printout()

    def SaveAs(self, event):
        self.client.SaveFile()

    def CloseWindow(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# call instance of DataGrid
# This is main interface of application
class DataFrame(wx.Frame):
    def __init__(self, parent, log):
        # size the frame to 600x400 - will fit in any VGA screen
        dimx = int(inits.get('gridsizex'))
        dimy = int(inits.get('gridsizey'))
        posx = int(inits.get('gridposx'))
        posy = int(inits.get('gridposy'))
        wx.Frame.__init__(self,parent,-1,"SalStat Statistics", size=(dimx,\
                                                                     dimy), pos=(posx,posy))
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        #set icon for frame (needs x-platform separator!
        icon = images.getIconIcon()
        self.SetIcon(icon)

        #-----------------------
        # Se crea el menubar
        #set up menus
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        prefs_menu = wx.Menu()
        describe_menu = wx.Menu()
        analyse_menu = wx.Menu()
        #analyse2_menu = wx.Menu()
        preparation_menu = wx.Menu()
        chart_menu = wx.Menu()
        help_menu = wx.Menu()
        #add contents of menu
        file_menu.Append(ID_FILE_NEW,'&New Data')
        #file_menu.Append(ID_FILE_NEWOUTPUT, 'New &Output Sheet')
        file_menu.Append(ID_FILE_OPEN, '&Open...')
        file_menu.Append(ID_FILE_SAVE, '&Save')
        file_menu.Append(ID_FILE_SAVEAS, 'Save &As...')
        file_menu.AppendSeparator()
        file_menu.Append(ID_FILE_PRINT, '&Print...')
        file_menu.AppendSeparator()
        file_menu.Append(ID_FILE_EXIT, 'E&xit')
        edit_menu.Append(ID_EDIT_CUT, 'Cu&t')
        edit_menu.Append(ID_EDIT_COPY, '&Copy')
        edit_menu.Append(ID_EDIT_PASTE, '&Paste')
        edit_menu.Append(ID_EDIT_SELECTALL, 'Select &All')
        edit_menu.Append(ID_EDIT_FIND, '&Find and Replace...')
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_EDIT_DELETECOL, 'Delete Current Column')
        edit_menu.Append(ID_EDIT_DELETEROW, 'Delete Current Row')
        prefs_menu.Append(ID_PREF_VARIABLES, 'Variables...')
        prefs_menu.Append(ID_PREF_GRID, 'Add Columns and Rows...')
        prefs_menu.Append(ID_PREF_CELLS, 'Change Cell Size...')
        prefs_menu.Append(ID_PREF_FONTS, 'Change the Font...')
        preparation_menu.Append(ID_PREPARATION_DESCRIPTIVES, 'Descriptive Statistics...')
        preparation_menu.Append(ID_PREPARATION_TRANSFORM, 'Transform Data...')
        #preparation_menu.Append(ID_PREPARATION_OUTLIERS, 'Check for Outliers...')
        #preparation_menu.Append(ID_PREPARATION_NORMALITY, 'Check for Normal Distribution...')
        analyse_menu.Append(ID_ANALYSE_1COND, '&1 Condition Tests...')
        analyse_menu.Append(ID_ANALYSE_2COND, '&2 Condition Tests...')
        analyse_menu.Append(ID_ANALYSE_3COND, '&3+ Condition Tests...')
        analyse_menu.Append(ID_ANALYSE_CORRELATION,'&Correlations...')
        #analyse_menu.Append(ID_ANALYSE_2FACT, '2+ &Factor Tests...')
        analyse_menu.AppendSeparator()
        analyse_menu.Append(ID_ANALYSE_SCRIPT, 'Scripting Window...')
        chart_menu.Append(ID_CHART_DRAW, 'Line Chart of All Means...')
        # the bar chart is *not* ready yet!
        chart_menu.Append(ID_BARCHART_DRAW, 'Bar Chart of All Means...')
        help_menu.Append(ID_HELP_WIZARD, '&What Test Should I Use...')
        help_menu.Append(ID_HELP_TOPICS, '&Topics...')
        help_menu.Append(ID_HELP_LICENCE, '&Licence...')
        help_menu.Append(ID_HELP_ABOUT, '&About...')
        #set up menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(file_menu, '&File')
        menuBar.Append(edit_menu, '&Edit')
        menuBar.Append(prefs_menu, '&Preferences')
        menuBar.Append(preparation_menu, 'P&reparation')
        menuBar.Append(analyse_menu, '&Analyse')
        menuBar.Append(chart_menu, '&Graph')
        menuBar.Append(help_menu, '&Help')
        self.SetMenuBar(menuBar)
        #------------------------

        #create small status bar
        self.CreateStatusBar()
        self.SetStatusText('SalStat Statistics')

        #----------------------
        # se crea una barra de herramientas
        # Get icons for toolbar
        NewIcon =    images.getNewBitmap()
        OpenIcon =   images.getOpenBitmap()
        SaveIcon =   images.getSaveBitmap()
        SaveAsIcon = images.getSaveAsBitmap()
        PrintIcon =  images.getPrintBitmap()
        CutIcon =    images.getCutBitmap()
        CopyIcon =   images.getCopyBitmap()
        PasteIcon =  images.getPasteBitmap()
        PrefsIcon =  images.getPreferencesBitmap()
        HelpIcon =   images.getHelpBitmap()
        #create toolbar (nothing to add yet!)
        tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            agwStyle=  aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)

        self.bt1 = tb1.AddSimpleTool(10, "New",  NewIcon,"New")
        self.bt2 = tb1.AddSimpleTool(20, "Open", OpenIcon,"Open")
        self.bt3 = tb1.AddSimpleTool(30, "Save", SaveIcon,"Save")
        self.bt4 = tb1.AddSimpleTool(40, "Save As",SaveAsIcon,"Save As")
        self.bt5 = tb1.AddSimpleTool(50, "Print",PrintIcon,"Print")
        self.bt6 = tb1.AddSimpleTool(60, "Cut",  CutIcon, "Cut")
        self.bt7 = tb1.AddSimpleTool(70, "Copy", CopyIcon, "Copy")
        self.bt8 = tb1.AddSimpleTool(80, "Paste",PasteIcon, "Paste")
        self.bt9 = tb1.AddSimpleTool(85, "Preferences",PrefsIcon, "Preferences")
        self.bt10= tb1.AddSimpleTool(90, "Help", HelpIcon, "Help")
        tb1.SetToolBitmapSize((24,24))
        # more toolbuttons are needed: New Output, Save, Print, Cut, \
        # Variables, and Wizard creates the toolbar
        tb1.Realize()
        self.m_mgr.AddPane( tb1, wx.aui.AuiPaneInfo().Top().Dock().
                            Resizable(False).FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).Layer(1).ToolbarPane().
                            LeftDockable( False ).RightDockable(False).
                            CloseButton(False ) )
        #--------------------

        #still need to define event handlers
        #set up the datagrid

        self.grid = SimpleGrid(self, log)
        self.grid.m_grid.SetDefaultColSize(60, True)
        self.grid.m_grid.SetRowLabelSize(40)

        self.m_mgr.AddPane(self.grid, 
                           wx.aui.AuiPaneInfo().CenterPane().
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))
        self.m_mgr.Update()
        self.BindEvents()

    def BindEvents(self):
        self.Bind(wx.EVT_MENU, self.GoClearData,        id = self.bt1.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveDataASCII, id = self.bt3.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveAsDataASCII,id= self.bt4.GetId())
        self.Bind(wx.EVT_MENU, self.grid.LoadDataASCII, id = self.bt2.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CutData,       id = self.bt6.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CopyData,      id = self.bt7.GetId())
        self.Bind(wx.EVT_MENU, self.grid.PasteData,     id = self.bt8.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SelectAllCells,id = ID_EDIT_SELECTALL)
        self.Bind(wx.EVT_MENU, self.GoFindDialog,       id = ID_EDIT_FIND)
        self.Bind(wx.EVT_MENU, self.grid.DeleteCurrentCol,id=ID_EDIT_DELETECOL)
        self.Bind(wx.EVT_MENU, self.grid.DeleteCurrentRow,id=ID_EDIT_DELETEROW)
        self.Bind(wx.EVT_MENU, self.GoVariablesFrame,   id = ID_PREF_VARIABLES)
        self.Bind(wx.EVT_MENU, self.GoEditGrid,         id = ID_PREF_GRID)
        self.Bind(wx.EVT_MENU, self.GoGridPrefFrame,    id = ID_PREF_CELLS)
        self.Bind(wx.EVT_MENU, self.GoFontPrefsDialog,  id = ID_PREF_FONTS)
        self.Bind(wx.EVT_MENU, self.GoContinuousDescriptives, id=ID_PREPARATION_DESCRIPTIVES)
        self.Bind(wx.EVT_MENU, self.GoTransformData,    id = ID_PREPARATION_TRANSFORM)
        self.Bind(wx.EVT_MENU, self.GoCheckOutliers,    id = ID_PREPARATION_OUTLIERS)
        self.Bind(wx.EVT_MENU, self.GoOneConditionTest, id = ID_ANALYSE_1COND)
        self.Bind(wx.EVT_MENU, self.GoTwoConditionTest, id = ID_ANALYSE_2COND)
        self.Bind(wx.EVT_MENU, self.GetThreeConditionTest,id=ID_ANALYSE_3COND)
        self.Bind(wx.EVT_MENU, self.GetCorrelationsTest,id = ID_ANALYSE_CORRELATION)
        #self.Bind(wx.EVT_MENU, ID_ANALYSE_2FACT, self.GoMFanovaFrame)
        self.Bind(wx.EVT_MENU, self.GoScriptWindow,     id = ID_ANALYSE_SCRIPT)
        self.Bind(wx.EVT_MENU, self.GoChartWindow,      id = ID_CHART_DRAW)
        self.Bind(wx.EVT_MENU, self.GoBarChartWindow,   id = ID_BARCHART_DRAW)
        self.Bind(wx.EVT_MENU, self.GoHelpAboutFrame,   id = ID_HELP_ABOUT)
        self.Bind(wx.EVT_MENU, self.GoHelpWizardFrame,  id = ID_HELP_WIZARD)
        self.Bind(wx.EVT_MENU, self.GoHelpTopicsFrame,  id = ID_HELP_TOPICS)
        self.Bind(wx.EVT_MENU, self.GoHelpLicenceFrame, id = ID_HELP_LICENCE)
        self.Bind(wx.EVT_MENU, self.EndApplication,     id = ID_FILE_EXIT)

        self.Bind(wx.EVT_MENU, self.GoClearData, id=10) ### VERUIFICAr
        # self.Bind(wx.EVT_MENU, ID_FILE_NEWOUTPUT, self.GoNewOutputSheet)
        # unsure if I want this - maybe restrict user to just one?
        self.Bind(wx.EVT_MENU, self.grid.SaveDataASCII, id =  30)
        self.Bind(wx.EVT_MENU, self.grid.SaveAsDataASCII, id= 40)
        #self.Bind(wx.EVT_MENU, ID_FILE_OPEN, self.grid.LoadNumericData)
        self.Bind(wx.EVT_MENU, self.grid.LoadDataASCII, id = 20)
        #EVT_TOOL(self, 20, self.grid.LoadNumericData)
        self.Bind(wx.EVT_MENU, self.grid.CutData, id= 60)
        self.Bind(wx.EVT_MENU, self.grid.CopyData, id = 70)
        self.Bind(wx.EVT_MENU,  self.grid.PasteData, id = 80)
        self.Bind(wx.EVT_MENU, self.GoVariablesFrame, id = 85)
        self.Bind(wx.EVT_MENU,self.GoHelpAboutFrame, id = 90)
        ##self.Bind(EVT_CLOSE, self, self.EndApplication)

    def GoClearData(self, evt):
        #shows a new data entry frame
        self.grid.m_grid.ClearGrid()

    def GoNewOutputSheet(self, evt):
        #shows a new output frame
        SheetWin = OutputSheet(frame, -1)
        SheetWin.Show(True)

    def GoFindDialog(self, event):
        # Shows the find & replace dialog
        # NOTE - this doesn't appear to work on the grid, so I might be missing something...
        data = wxFindReplaceData()
        dlg = wxFindReplaceDialog(self.grid, data, 'Find and Replace', \
                                  wxFR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)

    def GoEditGrid(self, event):
        #shows dialog for editing the data grid
        win = EditGridFrame(frame, -1)
        win.Show(True)

    def GoVariablesFrame(self, evt):
        # shows Variables dialog
        win = VariablesFrame(frame, -1)
        win.Show(True)

    def GoGridPrefFrame(self, evt):
        # shows Grid Preferences form
        win = GridPrefs(frame, -1)
        win.Show(True)

    def GoFontPrefsDialog(self, evt):
        # shows Font dialog for the data grid (output window has its own)
        data = wxFontData()
        dlg = wxFontDialog(frame, data)
        icon = images.getIconIcon()
        self.SetIcon(icon)
        if dlg.ShowModal() == wxID_OK:
            data = dlg.GetFontData()
            #data2 = data.GetChosenFont()
            self.grid.SetDefaultCellFont(data.GetChosenFont())

    def GoContinuousDescriptives(self, evt):
        # shows the continuous descriptives dialog
        win = DescriptivesFrame(frame, -1)
        win.Show(True)

    def GoTransformData(self, event):
        win = TransformFrame(frame, -1)
        win.Show(True)

    def GoCheckOutliers(self, event):
        pass

    def GoOneConditionTest(self, event):
        # shows One Condition Test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 0):
            win = OneConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need to enter 1 data column for this!')

    def GoTwoConditionTest(self,event):
        # show Two Conditions Test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = TwoConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need 2 data columns for that!')

    def GetThreeConditionTest(self, event):
        # shows three conditions or more test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = ThreeConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need some data for that!')

    def GetCorrelationsTest(self, event):
        # Shows the correlations dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = CorrelationTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need 2 data columns for that!')

    def GoMFanovaFrame(self, event):
        win = MFanovaFrame(frame, -1)
        win.Show(True)

    def GoScriptWindow(self, event):
        # Shows the scripting window
        win = ScriptFrame(frame, -1)
        win.Show(True)

    def GoChartWindow(self, event):
        # Draws a line chart based on the means
        waste, colnums = self.grid.GetUsedCols()
        if colnums != []:
            nameslist = [0]*len(colnums)
            meanlist = numpy.zeros(len(colnums)*2)
            meanlist.shape = (len(colnums),2)
            for i in range(len(colnums)):
                d = salstat_stats.FullDescriptives(self.grid.CleanData(colnums[i]))
                meanlist[i,1] = d.mean
                nameslist[i] = frame.grid.GetColLabelValue(i)
            meanlist[:,0] = numpy.arange(len(colnums))
            lines = pyplot.PolyLine(meanlist, legend="Red Line", colour='red')
            #lines2 = pyplot.PolyBars(meanlist)
            self.win = PlotFrame(self, -1)
            self.win.Show(True)
            self.win.client.Draw(pyplot.PlotGraphics([lines],"Graph","X","Y"))
            #self.win.client.draw(lines2,'automatic','automatic',None, nameslist)
        else:
            self.SetStatusText('You need some data to draw a graph!')

    def GoBarChartWindow(self, event):
        # Draws a bar chart based on the means
        waste, colnums = self.grid.GetUsedCols()
        if colnums != []:
            nameslist = [0]*len(colnums)
            meanlist = numpy.zeros(len(colnums)*2)
            meanlist.shape = (len(colnums),2)
            for i in range(len(colnums)):
                d = salstat_stats.FullDescriptives(self.grid.CleanData(colnums[i]))
                meanlist[i,1] = d.mean
                nameslist[i] = frame.grid.GetColLabelValue(i)
            meanlist[:,0] = numpy.arange(len(colnums))
            lines = PolyBars(meanlist)
            self.win = PlotFrame(self, -1)
            self.win.Show(True)
            self.win.client.draw(lines,'automatic','automatic',None, nameslist)
        else:
            self.SetStatusText('You need some data to draw a graph!')

    def GoHelpWizardFrame(self, event):
        # shows the "wizard" in the help box
        win = AboutFrame(frame, -1, 0)
        win.Show(True)

    def GoHelpTopicsFrame(self, event):
        # shows the help topics in the help box
        win = AboutFrame(frame, -1, 1)
        win.Show(True)

    def GoHelpLicenceFrame(self, evt):
        # shows the licence in the help box
        win = AboutFrame(frame, -1, 2)
        win.Show(True)

    def GoHelpAboutFrame(self, evt):
        # Shows the "About" thing in the help box
        win = AboutFrame(frame, -1, 3)
        win.Show(True)

    def EndApplication(self, evt):
        # close the application (need to check for new data since last save)
        # need to save the inits dictionary to .salstatrc
        dims = self.GetSizeTuple()
        inits.update({'gridsizex': dims[0]})
        inits.update({'gridsizey': dims[1]})
        dims = self.GetPositionTuple()
        inits.update({'gridposx': dims[0]})
        inits.update({'gridposy': dims[1]})
        dims = output.GetSizeTuple()
        inits.update({'outputsizex': dims[0]})
        inits.update({'outputsizey': dims[1]})
        dims = output.GetPositionTuple()
        inits.update({'outputposx': dims[0]})
        inits.update({'outputposy': dims[1]})
        initskeys = inits.keys()
        initsvalues = inits.values()
        initfilename = ini.initfile
        fout = file(initfilename,'w')
        for i in range(len(initskeys)):
            fout.write(str(initskeys[i])+' '+str(initsvalues[i])+'\n')
        fout.close()
        if self.grid.Saved == False:
            win = SaveDialog(self, -1)
            win.Show(True)
            self.grid.Saved = True
        else:
            frame.Destroy()

#---------------------------------------------------------------------------
# Scripting API is defined here. So far, only basic (but usable!) stuff.
def GetData(column):
    """This function enables the user to extract the data from the data grid.
    The data are "clean" and ready for analysis."""
    return frame.grid.CleanData(column)

def GetDataName(column):
    """This function returns the name of the data variable - in other words,
    the column label from the grid."""
    return frame.grid.GetColLabelValue(column)

def Display(text):
    """writes the text onto the html page. Handles lists and numerics"""
    text = str(text)
    output.htmlpage.write(string.join(text, ""))

def Describe(datain):
    """Provides OO descriptive statistics. Called by >>>x = Describe(a)
    and then a.N for the N, a.sum for the sum etc"""
    if (type(datain) == int):
        datain = frame.grid.CleanData(col2)
    return salstat_stats.FullDescriptives(datain)


def PutData(column, data):
    """This routine takes a list of data, and puts it into the datagrid
    starting at row 0. The grid is resized if the list is too large. This
    routine desparately needs to be updated to prevent errors"""
    n = len(data)
    if (n > frame.grid.GetNumberRows()):
        frame.grid.AddNCols(-1, (datawidth - gridwidth + 5))
    for i in range(n):
        frame.grid.SetCellValue(i, column, str(data[i]))

#---------------------------------------------------------------------------
# API statistical analysis functions
#One sample tests:
def DoOneSampleTTest(col1, usermean, tail = 2):
    """This routine performs a 1 sample t-test using the given data and
    a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.OneSampleTTest(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        raise #return Error

def DoOneSampleSignTest(col1, usermean, tail = 2):
    """This routine performs a 1 sample sign-test using the given data and
    a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.OneSampleSignTest(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.nplus, TBase.nminus, TBase.z, TBase.prob
    else:
        raise #return Error

def DoChiSquareVariance(col1, usermean, tail = 2):
    """This routine performs a chi square for variance ratio test using 
    the given data and a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.ChiSquareVariance(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.chisquare, TBase.df, TBase.prob
    else:
        raise #return Error

#Two sample tests:
def DoPairedTTest(col1, col2, tail = 2):
    """This routine performs a paired t-test using the data contained in
    col1 and col2 on the grid, with the passed alpha value which defaults
    to 0.05 (5%). If col1 and col2 are lists, then the data contained in the
    lists are used instead. There is a modicum of bounds checking on the
    passed variables to ensure that they are the right types (and bounds)"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col2)
    elif (type(col2) != list):
        error = error +'Invalid information for column 2\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TTestPaired(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        raise # return Error

def DoUnpairedTTest(col1, col2, tail = 2):
    """This function performs an unpaired t-test on the data passed. If the
    passed parameters are a list, then that is used as the data, otherwise
    if the parameters are an integer, then that integers columns data are
    retrieved."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TTestUnpaired()
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        return error

def DoPearsonsCorrelation(col1, col2, tail = 2):
    """This function performs a Pearsons correlation upon 2 data sets."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.PearsonsCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.r, TBase.df, TBase.prob
    else:
        return error

def DoFTest(col1, col2, uservar, tail = 2):
    """This performs an F-test for variance ratios upon 2 data sets. Passed
    in addition to the datasets is the user variance"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.r, TBase.df, TBase.prob
    else:
        return error

def DoSignTest(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.prob
    else:
        return error

def DoKendallsCorrelation(col1, col2, tail = 2):
    """This function performs a Kendalls tau correlation"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.KendalssTau(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.tau, TBase.z, TBase.prob
    else:
        return error

def DoKSTest(col1, col2, tail = 2):
    """This function performs a Komogorov-Smirnov test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.KolmogorovSmirnov(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.d, TBase.prob
    else:
        return error

def DoSpearmansCorrelation(col1, col2, tail = 2):
    """This function performs a Spearmans correlation on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.SpearmansCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.rho, TBase.t, TBase.df, TBase.prob
    else:
        return error

def DoRankSums(col1, col2, tail = 2):
    """This function performs a Wilcoxon rank sums test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    selobu = salstat_stats.TwoSampleTests(col1,col2)    
    TBase = selobu.RankSums(col1, col2) # salstat_stats.RankSums(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.prob
    else:
        return error

def DoSignedRanks(col1, col2, tail = 2):
    """This function performs a Wilcoxon signed ranks test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.SignedRanks(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.wt, TBase.prob
    else:
        return error

def DoMannWhitneyTest(col1, col2, tail = 2):
    """This function performs a Mann-Whitney U test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.MannWhitneyU(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.bigu, TBase.smallu, TBase.z, TBase.prob
    else:
        return error

def DoLinearRegression(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.LinearRegression(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.df, TBase.r, TBase.slope, TBase.intercept, \
               TBase.sterrest, TBase.prob
    else:
        return error

def DoPairedPermutation(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.PairedPermutation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.nperm, TBase.prob
    else:
        return error

# Three+ sample tests:

# Probability values
def GetChiProb(chisq, df):
    """This function takes the chi square value and the df and returns the
    p-value"""
    return salstat_stats.chisqprob(chisq, df)

def GetInverseChiProb(prob, df):
    """This function returns a chi value that matches the probability and
    df passed"""
    return salstat_stats.inversechi(prob, df)

def GetZProb(z):
    """This function returns the probability of z"""
    return salstat_stats.zprob(z)

def GetKSProb(ks):
    """This function returns the probability of a Kolmogorov-Smirnov test
    being significant"""
    return salstat_stats.ksprob(ks)

def GetTProb(t, df):
    """Gets the p-value for the passed t statistic and df"""
    return salstat_stats.betai(0.5*self.df,0.5,float(self.df)/(self.df+ \
                                                               self.t*self.t))

def GetFProb(f, df1, df2):
    """This returns the p-value of the F-ratio and the 2 df's passed"""
    return salstat_stats.fprob(df1, df2, f)

def GetInverseFProb(prob, df1, df2):
    """Returns the f-ratio of the given p-value and df's"""
    return salstat_stats.inversef(prob, df1, df2)


#---------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    import sys
    # find init file and read otherwise create it
    ini = GetInits()
    historyClass = History()
    hist = historyClass
    app = wx.App()
    frame = DataFrame(None, sys.stdout)
    frame.grid.SetFocus()
    output = OutputSheet(frame, -1)
    frame.Show(True)
    output.Show(True)
    app.MainLoop()

#---------------------------------------------------------------------------