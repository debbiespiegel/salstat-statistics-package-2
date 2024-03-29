__name__ = u"Frequency Stats"
__all__=  ['itemfreq', 'scoreatpercentile', 'percentileofscore',
           'histogram', 'cumfreq', 'relfreq']

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size

class itemfreq(_genericFunc):
    ''''''
    name=      __(u'item frequency')
    statName=  'itemfreq'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __('item frequency')
        self.statName=  'itemfreq'
        self._scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
        self.moment= None
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(220,300)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   [__('Select the columns to analyse')]]
        bt2= ['CheckListBox', [self.columnNames]]
        structure = list()
        structure.append([bt1,])
        structure.append([bt2,])
        return self.dialog(settings = setting, struct = structure)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        self.colNameSelect= values[0]
        
        if len( self.colNameSelect ) == 0:
            print __("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            print __("you have to select at least %i column(s)")%self.requiredcols
            return
        
        columns= self._convertColName2Values( self.colNameSelect )
        return columns
        
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col, *args, **params ) for col in columns]
        
    def object(self):
        return _stats.itemfreq
    
    def evaluate(self, *args, **params):
        return _stats.itemfreq(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(values)
        self._report(result)
        
    def _report( self, result):
        for pos, (varName, res) in enumerate( zip( self.colNameSelect,result)):
            if pos == 0:
                self.outputGrid.addColData( varName, self.name)
            else:
                self.outputGrid.addColData( varName)
            self.outputGrid.addColData( res[:,0])
            self.outputGrid.addColData( res[:,1])
        self.outputGrid.addRowData(['var Name','item','frequency']*len(result) ,currRow= 0)
        print self.statName+ ' '+_('successfull')

class scoreatpercentile(_genericFunc):
    ''''''
    name=      __(u'score at percentile')
    statName=  'scoreatpercentile'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __('score at percentile')
        self.statName=  'scoreatpercentile'
        self._scritpEquivalenString='stats.'+self.statName
        self.nameStaticText= '%'
        self.minRequiredCols= 1
        self.spindata= [0,100,1]
        self.colNameSelect= ''
        self._percent= None
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(220,300)}
        self._updateColsInfo() # update self.columnames and self.colnums
        if len( self.columnNames) == 0:
            return
        bt1=  ['StaticText',   ['Select the column to analyse']]
        bt2=  ['CheckListBox', [self.columnNames]]
        btn3= ['SpinCtrl',     [0,100,3]]
        btn4= ['StaticText',   [self.nameStaticText] ]
        structure = list()
        structure.append([bt1,])
        structure.append([bt2,])
        structure.append([btn3, btn4 ])
        return self.dialog(settings = setting, struct = structure)
        
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # changing value strings to numbers
        (self.colNameSelect, self._percent) = values
        if len( self.colNameSelect ) == 0:
            print __("You haven't selected any items!")
            return
        
        if not isinstance(self.colNameSelect, (list, tuple)):
            self.colNameSelect = [self.colNameSelect]
            self._percent = [self._percent]

        columns= list()
        for selectedCol in self.colNameSelect:
            col= numpy.array( self.grid.GetColNumeric( selectedCol))
            col= numpy.ravel( col)
            columns.append( col)
        return (columns, self._percent)
    
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col, *args, **params ) for col in columns]
        
    def object(self):
        return _stats.scoreatpercentile
    
    def evaluate(self, *args, **params):
        return _stats.scoreatpercentile(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(result)
        
        # inserting information about the input data
        self.outputGrid.addRowData( ['Input Data'] , currRow= 0)
        self.outputGrid.addRowData( [self.nameStaticText+'=',  self._percent], currRow= 1)
        self.outputGrid.addRowData( ['Output Data'] , currRow= 2)
        
        print self.name + ' '+ __('successful')

class percentileofscore(scoreatpercentile):
    name=      __(u'percentile of score')
    statName=  'percentileofscore'
    def __init__(self):
        # getting all required methods
        scoreatpercentile.__init__(self)
        self.name=      __('percentile of score')
        self.statName=  'percentileofscore'
        self._scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
        self.score=   None
        self.histbin= None
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(260,250)}
        self._updateColsInfo() # update self.columnames and self.colnums
        btn1= ['StaticText',   ['Columns to analyse',] ]
        btn2= ['CheckListBox', [self.columnNames]]
        btn3= ['SpinCtrl',     [0,100,1]]
        btn4= ['StaticText',   ['score',] ]
        btn5= ['SpinCtrl',     [1,1000,1]]
        btn6= ['StaticText',   ['histbins'] ]
        structure = list()
        structure.append([btn2, btn1])
        structure.append([btn3, btn4])
        structure.append([btn5, btn6])
        return self.dialog(settings = setting, struct= structure)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # changing value strings to numbers
        (self.colNameSelect, self.score, self.histbin) = values
        if len( self.colNameSelect ) == 0:
            print __("You haven't selected any items!")
            return
        
        if not isinstance(self.colNameSelect, (list, tuple)):
            self.colNameSelect= [self.colNameSelect]
            self.histbin=       [self.histbin]
            self.score=         [self.score]

        columns= list()
        for selectedCol in self.colNameSelect:
            col= numpy.array( self.grid.GetColNumeric( selectedCol))
            col= numpy.ravel( col)
            columns.append( col)
        return (columns, self.score, self.histbin)
    
    def object(self):
        return _stats.percentileofscore
    
    def evaluate(self, *args, **params):
        return _stats.percentileofscore(*args, **params)
    
    def _report(self, result):
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(result)
        
        # inserting information about the input data
        self.outputGrid.addRowData(['Input Data'] , currRow= 0)
        self.outputGrid.addRowData(['score=',  self.score], currRow= 1)
        self.outputGrid.addRowData(['histbins=',  self.histbin], currRow= 2)
        self.outputGrid.addRowData(['Output Data'] , currRow= 3)
        
        print  self.name + ' '+ __('successful')
            
class histogram(scoreatpercentile):
    name=      __(u'histogram')
    statName=  'histogram'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __('histogram')
        self.statName=  'histogram'
        self.nameStaticText= __('Number of Bins')
        self._scritpEquivalenString='stats.'+self.statName
        self.spindata= [1,1000,1]
        self.minRequiredCols= 1
        self.colNameSelect= ''
        self._percent=   None  # self._percent == self.histbins
        
    def object(self):
        return _stats.histogram
    
    def evaluate(self, *args, **params):
        return _stats.histogram(*args, **params)
    
    def _report(self, result):
        for pos,(res, name) in enumerate( zip( result, self.colNameSelect)):
            if pos == 0:
                self.outputGrid.addColData( name, self.name)
            else:
                self.outputGrid.addColData( name)    
            self.outputGrid.addColData(map(None,res[0]))
            self.outputGrid.addColData(res[1])
            self.outputGrid.addColData(res[2])
            self.outputGrid.addColData(res[3])
        
        # inserting information about the input data
        self.outputGrid.addRowData(['Input Data'] , currRow= 0)
        self.outputGrid.addRowData(['histbins=',  self._percent], currRow= 1)
        self.outputGrid.addRowData(['Output Data'] , currRow= 2)
        self.outputGrid.addRowData(['var name','bin values', 'lowerreallimit',
                                     'binsize', 'extrapoints']*len(result),
                                    currRow= 3)
        
        print self.name + ' '+ __('successful')

class cumfreq(histogram):
    name=      __(u'cumulative frequency')
    statName=  'cumfreq'
    def __init__(self):
        # getting all required methods
        histogram.__init__(self)
        self.name=      __('cumulatyve frequency')
        self.statName=  'cumfreq'
        self.nameStaticText= 'histbins'
        self._scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
        self._percent=   None  # self._percent == self.histbins
    
    def object(self):
        return _stats.cumfreq
    
    def evaluate(self, *args, **params):
        return _stats.cumfreq(*args, **params)
    
    def _report(self, result):
        for pos,(res, name) in enumerate( zip( result, self.colNameSelect)):
            if pos == 0:
                self.outputGrid.addColData( name, self.name)
            else:
                self.outputGrid.addColData( name)    
            self.outputGrid.addColData( map(None,res[0]))
            self.outputGrid.addColData( res[1])
            self.outputGrid.addColData( res[2])
            self.outputGrid.addColData( res[3])
        
        # inserting information about the input data
        self.outputGrid.addRowData( ['Input Data'] , currRow= 0)
        self.outputGrid.addRowData( [self.nameStaticText+'=',  self._percent], currRow= 1)
        self.outputGrid.addRowData( ['Output Data'] , currRow= 2)
        self.outputGrid.addRowData( ['var name','cumfreq bin values', 'lowerreallimit',
                                     'binsize', 'extrapoints']*len(result),
                                    currRow= 3)
        
        print self.name + ' '+ __('successful')

class relfreq(histogram):
    name=      __(u'relative frequency histogram')
    statName=  'relfreq'
    def __init__(self):
        # getting all required methods
        histogram.__init__(self)
        self.name=      __('relative frequency histogram')
        self.statName=  'relfreq'
        self._scritpEquivalenString='stats.'+self.statName
        
    def object(self):
        return _stats.relfreq
    
    def evaluate(self, *args, **params):
        return _stats.relfreq(*args, **params)
    
    