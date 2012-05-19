# -*- coding: utf-8 -*-
'''
Created on 25/10/2010

@author: Sebastian Lopez
'''

import wx
from NewGrid import NewGrid # grid with context menu
from imagenes import imageEmbed

import wx.aui

def numPage():
    i = 1
    while True:
        yield i
        i+= 1

class MyGridPanel ( wx.Panel ):
    def __init__( self, parent , id= wx.ID_ANY, size=(5,5)):
        # bigParent: id del parent para llamar la funcion OnrangeChange
        wx.Panel.__init__ ( self, parent, id , pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.m_grid = NewGrid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        # Grid
        self.m_grid.CreateGrid( size[0], size[1] )
        self.m_grid.EnableEditing( True )
        self.m_grid.EnableGridLines( True )
        self.m_grid.EnableDragGridSize( False )
        self.m_grid.SetMargins( 0, 0 )
        # Columns
        self.m_grid.EnableDragColMove( False )
        self.m_grid.EnableDragColSize( True )
        self.m_grid.SetColLabelSize( 30 )
        self.m_grid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        # Rows
        self.m_grid.EnableDragRowSize( True )
        self.m_grid.SetRowLabelSize( 80 )
        self.m_grid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        # Label Appearance
        self.m_grid.SetLabelBackgroundColour( wx.Colour( 254, 226, 188 ) )
        # Cell Defaults
        self.m_grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        bSizer1.Add( self.m_grid, 1, wx.ALL|wx.EXPAND, 5 )
        self.SetSizer( bSizer1 )
        self.Layout()

    def setRowNames(self,names):
        self.m_grid.setRowNames(names)

    def setColNames(self,names):
        self.m_grid.setColNames(names)

    def updateGridbyCol(self,values):
        self.m_grid.updateGridbyCol(values)

    def getByRows(self):
        return self.m_grid.getByRows()

    def getValue(self):
        return self.m_grid.getValue()

    def getHeader(self):
        return self.m_grid.getHeader()

    def getByColumns(self):
        return self.m_grid.getByColumns()

    def __del__( self ):
        pass

class NoteBookSheet(wx.Panel):
    def __init__( self, parent, *args, **params):
        # se almacenan las paginas en un diccionario con llave el numero de pagina
        wx.Panel.__init__ ( self, parent, *args, **params)
        bSizer = wx.BoxSizer( wx.VERTICAL )
        self.m_notebook = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
        ## wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_BOTTOM )
        # self.m_notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnNotebookPageChange)
        bSizer.Add( self.m_notebook, 1, wx.EXPAND |wx.ALL, 5 )
        self.SetSizer( bSizer )
        # se inicia el generador para el numero de pagina
        self.npage = numPage()
        self.currentPage = None
        self.pageNames= dict()
        self.Layout()

    def getGridAllValueByCols(self,pageName):
        if not (pageName in self.pageNames.keys()):
            raise StandardError('La pagina no existe')
        page= self.pageNames[pageName]
        return page.getByColumns()
        ## retorna el contenido de una pagina del notebooksheet
        #if pageName in self.getPageNames():
            #for index,value in enumerate(self.getPageNames()):
                #if value == pageName:
                    #numberpage = index
                    #break
            #obj = self.m_notebook.GetPage(numberpage)
            #return obj.getByColumns()
        #else:
            #raise StandardError('La pagina no existe')

    def getPageNames(self):
        return self.pageNames.keys()
        ## retorna los nombre de las paginas adicionadas, como una lista
        #numpages= self.m_notebook.GetPageCount()
        #if numpages > 0:
            #return tuple([self.m_notebook.GetPageText(page) for page in range(numpages)])
        #else:
            #return ()

    def getHeader(self,pageName):
        if not (pageName in self.pageNames.keys()):
            raise StandardError('La pagina no existe')
        page= self.pageNames[pageName]
        return page.getHeader()
        #if pageName in self.getPageNames():
            #numberpage= [index for index,value in enumerate(self.getPageNames()) if value == pageName]
            #obj = self.m_notebook.GetPage(numberpage[0]).getHeader()
            #return obj
        #else:
            #raise StandardError('La pagina no existe')

    def OnNotebookPageChange(self,evt):
        self.currentPage= evt.Selection

    def addPage(self, data):
        defaultData = {'name': u'',
                       'size': (0,0),
                       'nameCol': list(),
                       'nameRow': list()}
        
        for key, value in data.items():
            if defaultData.has_key(key):
                defaultData[key] = value
        # adiciona una pagina al notebook grid
        newName= data['name'] +'_'+ str(self.npage.next())
        self.pageNames[newName]= MyGridPanel(self.m_notebook,-1,size= defaultData['size'] )
        self.currentPage=  self.pageNames[newName]
        grid= self.pageNames[newName]
        self.m_notebook.AddPage(grid, newName, False )
        # se hace activo la pagina adicionada
        self.m_notebook.SetSelection(self.m_notebook.GetPageCount()-1)
        # se escriben los nombres de las columnas en el grid en caso de existir
        if 'nameCol' in defaultData.keys():
            for index, value in enumerate(defaultData['nameCol']):
                grid.m_grid.SetColLabelValue(index,value) # str(value)
        if 'nameRow' in defaultData.keys():
            for index, value in enumerate(defaultData['nameRow']):
                grid.m_grid.SetRowLabelValue(index,value)

        return grid # retorna el objeto MyGrid

    def __loadData__(self,selectedGrid,data, byRows = True):
        # gridId, nombre de la hoja en la que se adicionaran los datos
        # data: iterable con los datos puntuales a cargar ej:
        #       data= ((1,2,3,5),(7,8,9,4))
        #       corresponde a la matriz
        #
        #         1 ! 2 ! 3 ! 5
        #         7 ! 8 ! 9 ! 4
        # byRows : bool, indica si los datos se ingresan por filas o por columnas
        if byRows:
            for rowNumber,fil in enumerate(data):
                for colNumber,cellContent in enumerate(fil):
                    if cellContent != None:
                        if type(cellContent) == type(u''):
                            selectedGrid.SetCellValue(rowNumber,colNumber, cellContent) ##unicode(str(cellContent))
                        else:
                            selectedGrid.SetCellValue(rowNumber,colNumber, unicode(str(cellContent)))
        else:
            for colNumber, col in enumerate(data):
                for rowNumber, cellContent in enumerate(col):
                    if type(cellContent) == type(u''):
                        selectedGrid.SetCellValue(rowNumber, colNumber, cellContent)
                    else:
                        selectedGrid.SetCellValue(rowNumber, colNumber, unicode(str(cellContent))) ## unicode(str(cellContent))
        # implementar cargar los datos

    def GetPageCount(self):
        # 21/04/2011
        # retorna el numero de paginas que hay en el notebook
        return self.m_notebook.PageCount

    def delPage(self, page= None):
        # si no se ingresa un numero de pagina se
        #     considera que se va a borrar la pagina actual
        # las paginas se numeran mediante numeros desde el cero
        if page == None:
            # se considera que la pagina a borrar es la pagina actual
            #self.m_notebook.GetCurrentPage().Destroy() # borra el contenido de la pagina
            self.m_notebook.DeletePage(self.m_notebook.GetSelection())
            # se borra la pagina

            return
        page = int(page)
        if page <0:
            return
        if page > self.GetPageCount():
            raise IndexError("Page doesn't exist")
        parent = self.pages[page].GetParent()
        parent.DeletePage(page)

    def upData(self,  data):
        # It's used to upload data into a grid
        # where the grid it's an int number
        # that gives the page number into the NotebookSheet
        # data: dict information with ...
        #       name: string name of the page
        #       size: data size (#rows, #ncols)
        #       data: matrix data
        #       nameCol: objeto iterable con el nombre de las columnas
        #              Si no se escribe aparece por defecto a, b,.. la
        #              nomenclatura comun
        if type(data) != type(dict()):
            raise TypeError('Data must be a dictionary')
        if not('byRows' in data.keys()):
            byRows = True
        else:
            byRows = data['byRows']
        # se adiciona la pagina grid
        grid01= self.addPage(data)
        # se cargan los datos dentro del grid
        self.__loadData__(grid01.m_grid,data['data'],byRows)
        return grid01
    
    def addColData(self, colData, pageName= None):
        '''adiciona una columna con el contenido de un iterable'''
        if pageName == None:
            if len(self.getPageNames()) == 0:
                'se procede a adicionar una hoja nueva'
                page = self.addPage()
            else:
                page = self.currentPage
        elif pageName in self.pageNames.keys():
            page = self.pageNames[pageName]
        else:
            page = self.addPage({'name': pageName})
        # se procede a verificar las dimensiones de la pagina actual
        size = (page.m_grid.GetNumberRows(), page.m_grid.GetNumberCols())
        # se adiciona una columna
        page.m_grid.AppendCols(1)
        currCol = size[1]
        if isinstance(colData,(str,)):
            colData = [colData]
        # compare de row numbres
        if size[0] >= len(colData):
            pass
        else:
            diffColNumber= len(colData) - size[0]
            # adding the required rows
            page.m_grid.AppendRows(diffColNumber)
        # populate with data
        for colPos, colValue in enumerate(colData):
            if isinstance(colValue,(str,unicode)):
                pass
            else:
                colValue = str(colValue)
            page.m_grid.SetCellValue(colPos, currCol, colValue)
            
        
class Test(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(480, 520))
        customPanel = NoteBookSheet(self,-1)
        # se adicionan 4 paginas al sheet
        for i in range(4):
            customPanel.addPage()
        #customPanel.delPage(2)
        self.Centre()
        self.Show(True)

if __name__ == '__main__':
    app = wx.App()
    Test(None, -1, 'Custom Grid Cell')
    app.MainLoop()