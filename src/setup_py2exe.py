from distutils.core import setup
import py2exe

opts = { "py2exe":
            { "unbuffered": True,
              "optimize": 0,
              "includes": ["wx",],
              "excludes":["pywin", "pywin.debugger", "pywin.debugger.dbgcon",
                          "pywin.dialogs", "pywin.dialogs.list","Tkconstants",
                          "Tkinter","tcl",
                          "PyQt4","matplotlib",],
              "dist_dir": u"F:\\proyecto salstat\\dist\\",
              "dll_excludes" : ["MSVCP90.DLL","API-MS-Win-Security-Base-L1-1-0.dll",
                                "API-MS-Win-Security-Base-L1-1-0.dll",
                                "API-MS-Win-Core-ProcessThreads-L1-1-0.dll",
                                "POWRPROF.dll","API-MS-Win-Core-LocalRegistry-L1-1-0.dll",
                                "OLEAUT32.dll","USER32.dll","COMCTL32.dll",
                                "SHELL32.dll","ole32.dll","WINMM.dll","WSOCK32.dll",
                                "COMDLG32.dll","ADVAPI32.dll","GDI32.dll","msvcrt.dll",
                                "WS2_32.dll","mfc90.dll","RPCRT4.dll","VERSION.dll",
                                "KERNEL32.dll","UxTheme.dll",
                                ]
              }
          }

setup(name= 'salstat',
      version='2.0',
      description='Statistics Package',
      author='Sebastian Lopez Buritica',
      windows=[
          {"script": 'salstat.py',
           "icon_resources": [(1, "F:\\proyecto salstat\\src\\salstat.ico")]
           }
          ],
      zipfile = None,
      options = opts,
      )
