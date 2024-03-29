__name__ ='Pivot'
__all__=  ['pivotTable',]

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size

class pivotTable(_genericFunc):
    ''''''
    name=      'Pivot Table'
    statName=  'pivotTable'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      'Pivot Table'
        self.statName=  'pivotTable'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(400,500)}
        self._updateColsInfo() # update self.columnames and self.colnums
        btn1= ['StaticText',   ['Select the columns to analyse']]
        btn2= ['makePairs', [['Xdata'],[self.columnNames], 4]]
        btn3= ['makePairs', [['Ydata','Names'],[self.columnNames, None], 4]]
        structure= list()
        structure.append([btn1,])
        structure.append([btn2,btn3])
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
            self.Logg.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.Logg.write("you have to select at least %i column(s)"%self.minRequiredCols)
            return
        
        columns= self._convertColName2Values( self.colNameSelect )
        return columns
        
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col ) for col in columns]
        
    def object(self):
        return _stats.geometricmean
    
    def evaluate(self, *args, **params):
        return _stats.geometricmean(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(values)
        self._report(result)
        
    def _report(self, result):
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(result)
        self.Logg.write(self.statName+ ' successfull')
        
