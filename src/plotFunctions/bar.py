__name__ = u'Bar plot'
__all__=  ['barChartAllMeans']

from openStats import statistics

import numpy
from plotFunctions import _neededLibraries, pltobj
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from statFunctions.frequency import histogram
from pylab import xticks

class barChartAllMeans( _neededLibraries):
    ''''''
    name=      u'Bar chart of all means'
    plotName=  'barChartMeans'
    def __init__(self):
        # getting all required methods
        _neededLibraries.__init__( self)
        self.name=      u'Bar chart of all means'
        self.plotName=  'barChartMeans'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        '''this funtcion is used to plot the bar chart of all means'''
        self.log.write("Bar Chart of All Means")
        self._updateColsInfo()

        self.colours= ["blue", "black",
                  "red", "green", "lightgreen", "darkblue",
                  "yellow", "white"]
        txt2= ["StaticText",   ["Colour"]]
        txt3= ["StaticText",   ["Select data to plot"]]
        btn2= ["Choice",       [self.colours]]
        btn3= ["CheckListBox", [self.columnNames]]
        btn4= ["CheckBox",     ["push the values up to the bars"] ]
        structure= list()
        structure.append( [txt3])
        structure.append( [btn3])
        structure.append( [btn2, txt2])
        structure.append( [btn4])
        setting= {"Title":"Bar chart means of selected columns"}
        return self.dialog(settings= setting, struct= structure)        
    
    def _calc( self, columns, *args, **params):
        return [self.evaluate( col, *args, **params) for col in columns]
        
    def object(self):
        return self
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() != _OK:
            dlg.Destroy()
            return
        
        values=   dlg.GetValue()
        
        self.colNameSelect=  values[0]
        self.colour=         values[1]
        showBarValues=       values[2]

        if self.colour == None:
            self.colour=  self.colours[0]
            
        if self.colNameSelect == None:
            self.log.write("you have to select at least %i column"%self.minRequiredCols)
            return
        
        if isinstance( self.colNameSelect, (str, unicode)):
            self.colNameSelect= [self.colNameSelect]

        if len( self.colNameSelect) < self.minRequiredCols:
            self.SetStatusText( u'You need to select at least %i columns to draw a graph!'%self.minRequiredCols)
            return
        
        # it only retrieves the numerical values
        columns= [statistics( self.grid.GetColNumeric(col),'noname',None).mean for col in self.colNameSelect]
        #columns= [self.grid.GetColNumeric( col) 
                   #for col in self.colNameSelect]
        
        return ( columns, self.colour, showBarValues)
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydat=         args[0]
        color=        args[1]
        showBarValues= args[2]
        
        # evaluating the histogram function to obtain the data to plot        
        plt= pltobj( None, xlabel= 'variable', ylabel= 'value', title= 'Bar Chart of all means')
        plt.gca().hold( True)
        xdat= numpy.arange(1, len(ydat)+1)
        res= plt.gca().bar( xdat, ydat, color= color)
        width= res[0]._width/2.0
        plt.gca().set_xlim( min(xdat)-0.5, max(xdat)+width*2+0.5)
        plt.gca().set_ylim( numpy.array( plt.gca().get_ylim())*numpy.array( [1, 1.05]))
        
        if showBarValues:
            ax= plt.gca()
            for label, xpos, ypos in zip( self.colNameSelect, xdat, ydat):
                xpos+= width
                if isinstance(label, (str,unicode)):
                    ax.annotate(label, (xpos, ypos), va="bottom", ha="center")
                    
                elif type(labels) == type(1):
                    ax.annotate(r"%d" % labels, (xpos, labels), va="bottom", ha="center")
                    
                elif type(labels) == type(1.1):
                    ax.annotate(r"%f" % labels, (xpos, labels), va="bottom", ha="center")
                    
                elif str(type(labels)) == "<type 'numpy.int32'>":
                    ax.annotate(r"%d" % labels, (xpos, labels), va="bottom", ha="center")
        else:
            plt.gca().set_xticks(xdat + width)
            plt.gca().set_xticklabels(self.colNameSelect)
   
        plt.gca().hold( False)
        plt.updateControls()
        plt.canvas.draw()
        return plt
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        result.Show()
        self.log.write(self.plotName+ ' successfull')



## NICE BAR PLOT
#path=     os.path.join( os.path.split( sys.argv[0])[0], "nicePlot", "images", "barplot")
        #figTypes= [fil[:-4] for fil in os.listdir(path) if fil.endswith(".png")]
        #txt1= ["StaticText", ["Bar type"]]
        #txt2= ["StaticText", ["Colour"]]
        #txt3= ["StaticText", ["Select data to plot"]]
        #btn1= ["Choice", [figTypes]]
        #btn2= ["Choice", [colours]]
        #btn3= ["CheckListBox", [waste]]
        #btn4= ["CheckBox", ["push the labels up to the bars"] ]
        #structure= list()
        #structure.append([btn1, txt1])
        #structure.append([btn2, txt2])
        #structure.append([txt3])
        #structure.append([btn3])
        #structure.append([btn4])
        #setting= {"Title":"Bar chart means of selected columns"}
        #dlg= dialog(self, settings= setting, struct= structure)
        #if dlg.ShowModal() != wx.ID_OK:
            #dlg.Destroy()
            #return

        #values=  dlg.GetValue()
        #barType= values[0]
        #colour=  values[1]
        #selectedcols= values[2]
        #showLabels= values[3]

        #if barType == None:
            #barType= "redunca"

        #if colour == None:
            #colour= "random"
        
        #if showLabels:
            #labels= selectedcols
        #else:
            #labels = None

        #dlg.Destroy()
        #if len( selectedcols) == 0:
            #self.SetStatusText( "You need to select some data to draw a graph!")
            #return

        #self.log.write( "barType= "+ "'" + barType.__str__() + "'", False)
        #self.log.write( "colour= "+ "'" + colour.__str__() + "'", False)
        #self.log.write( "selectedcols= "+ selectedcols.__str__(), False)
        #self.log.write( '''data= [statistics( grid.GetColNumeric(col),'noname',None).mean for col in selectedcols]''', False)
        #data = [statistics( self.grid.GetColNumeric( col),"noname",None).mean
                #for col in selectedcols]
        #self.log.write( '''plt= plot(parent=   None,
                  #typePlot= 'plotNiceBar',
                  #data2plot= (numpy.arange(1, len(data)+1), data,  None,  colour, barType,),
                  #xlabel=  'variable',
                  #ylabel=  'value',
                  #title=   'Bar Chart of all means')''', False)
        #plt= plot(parent=   self,
                  #typePlot= "plotNiceBar",
                  #data2plot= (numpy.arange(1, len(data)+1), data,  None,  colour, barType, labels),
                  #xlabel=  "variable",
                  #ylabel=  "value",
                  #title=   "Bar Chart of all means")
        #plt.Show()
        #self.log.write("plt.Show()", False)