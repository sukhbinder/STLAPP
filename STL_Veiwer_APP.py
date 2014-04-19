# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 11:11:58 2014

@author: Sukhbinder Singh

STL Viewer APP

Uses Wx Python and VTK

#Features:
Load an STL file.
Rotate, pan, zoom the model.

See it in wireframe, surface.
Take a screenshot.


"""

import wx
import vtk
import sys
import os
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor



class EventsHandler(object):

    def __init__(self, parent):
        self.parent = parent

    # Exit Menu
    def onExit(self, event):
        self.parent.Destroy()
    # Change Background
    def onBackgroundColor(self, event):
        dlg = wx.ColourDialog(self.parent)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            dlg.Destroy()
            self.SetColor(data.GetColour().Get())
            return
        dlg.Destroy()

    def SetColor(self, bkgColor):
        """
        @warning if the model is not loaded and the color is not "clicked"
        on, then rend will return None
        """
        rend = self.parent.vtkPanel.renderer
        if not rend:  # rend doesnt exist at first
            print 'Try again to change the color (you didnt "click" on the color; one time bug)'
            return
            rend = self.parent.vtkPanel.renderer
        ## bkgColor range from 0 to 255
        ## color ranges from 0 to 1
        color = [bkgColor[0] / 255., bkgColor[1] / 255., bkgColor[2] / 255.]
        rend.SetBackground(color)
        self.parent.vtkPanel.widget.Render()
    
	# StatusBar Toggle
    def onToggleStatusBar(self, e):
        if self.parent.isstatusbar:
                self.parent.statusbar.Hide()
                self.parent.isstatusbar = False
        else:
            self.parent.statusbar.Show()
            self.parent.isstatusbar = True

	# ToolBar Toggle
    def onToggleToolBar(self, e):
        if self.parent.istoolbar:
            self.parent.toolbar1.Hide()
            self.parent.istoolbar= False
        else:
            self.parent.toolbar1.Show()
            self.parent.istoolbar= True

    # Help Menu About
	# Change the list name
    def onAbout(self, event):
        about = [
            'VTK STL Viewer' ,
            'Copyright Sukhbinder Singh 2014 \n' ,
            'Developed in December 2013',
            '',
            'www.sukhbindersingh.com',
            '',
            'Keyboard Controls',
            '',
            'R   - Fit the model',
            'F   - Zoom the moDEL',
            'S   - surface',
            'W   - wireframe',
        ]

        dlg = wx.MessageDialog(None, '\n'.join(about), 'About',
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
		
#   Add your events HERE
#	def onSomething(self, event):
#		pass

 # End of EventsHandler
 
 
class vtkPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        
# To interact with the scene using the mouse use an instance of vtkRenderWindowInteractor. 
        self.widget = wxVTKRenderWindowInteractor(self, -1)
        self.widget.Enable(1)
        self.widget.AddObserver("ExitEvent", lambda o,e,f=self: f.Close())
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.widget, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.widget.GetRenderWindow().AddRenderer(self.renderer)
        self.Layout()
        self.widget.Render()
        self.filename=None
        self.isploted = False
    
            
    def onTakePicture(self, event):
        renderLarge = vtk.vtkRenderLargeImage()
        renderLarge.SetInput(self.renderer)
        renderLarge.SetMagnification(4)

        wildcard = "PNG (*.png)|*.png|" \
            "JPEG (*.jpeg; *.jpeg; *.jpg; *.jfif)|*.jpg;*.jpeg;*.jpg;*.jfif|" \
            "TIFF (*.tif; *.tiff)|*.tif;*.tiff|" \
            "BMP (*.bmp)|*.bmp|" \
            "PostScript (*.ps)|*.ps|" \
            "All files (*.*)|*.*"

        dlg = wx.FileDialog(None, "Choose a file", "",
                            "", wildcard, wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            fname = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            fname = os.path.join(self.dirname, fname)
            # We write out the image which causes the rendering to occur. If you
            # watch your screen you might see the pieces being rendered right
            # after one another.
            lfname = fname.lower()
            if lfname.endswith('.png'):
                writer = vtk.vtkPNGWriter()
            elif lfname.endswith('.jpeg'):
                writer = vtk.vtkJPEGWriter()
            elif lfname.endswith('.tiff'):
                writer = vtk.vtkTIFFWriter()
            elif lfname.endswith('.ps'):
                writer = vtk.vtkPostScriptWriter()
            else:
                writer = vtk.vtkPNGWriter()

            writer.SetInputConnection(renderLarge.GetOutputPort())
            writer.SetFileName(fname)
            writer.Write()
        dlg.Destroy()

# Write your VTK panel methods here
    def plot(self,event):
        self.renderthis()
          
    def renderthis(self):
            # open a window and create a renderer            
            self.widget.GetRenderWindow().AddRenderer(self.renderer)
  
           # open file             
            self.filename=""
            openFileDialog = wx.FileDialog(self, "Open STL file", "", self.filename,
                                       "*.stl", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.filename = openFileDialog.GetPath()
            # render the data
            reader = vtk.vtkSTLReader()
            reader.SetFileName(self.filename)
  
            # To take the polygonal data from the vtkConeSource and
            # create a rendering for the renderer.
            coneMapper = vtk.vtkPolyDataMapper()
            coneMapper.SetInput(reader.GetOutput())

            # create an actor for our scene
            if self.isploted:
                coneActor=self.renderer.GetActors().GetLastActor()
                self.renderer.RemoveActor(coneActor)
                
            coneActor = vtk.vtkActor()
            coneActor.SetMapper(coneMapper)
            # Add actor
            self.renderer.AddActor(coneActor)
           # print self.ren.GetActors().GetNumberOfItems()

            if not self.isploted:
                axes = vtk.vtkAxesActor()
                self.marker = vtk.vtkOrientationMarkerWidget()
                self.marker.SetInteractor( self.widget._Iren )
                self.marker.SetOrientationMarker( axes )
                self.marker.SetViewport(0.75,0,1,0.25)
                self.marker.SetEnabled(1)

            self.renderer.ResetCamera()
            self.renderer.ResetCameraClippingRange()
            cam = self.renderer.GetActiveCamera()
            cam.Elevation(10)
            cam.Azimuth(70)
            self.isploted = True
            self.renderer.Render()
# End of vtkPanel form

		
class AppFrame(wx.Frame):
    def __init__(self,parent,title,iconpath):
        wx.Frame.__init__(self,parent,title=title,size=(800,600))
        self.title=title
        self.iconPath=iconpath
        self.SetupFrame()        
  
    def settingTitle(self):
             self.SetTitle(self.title+self.vtkPanel.filename)
            
    def Createstatusbar(self):
            self.statusbar = self.CreateStatusBar()
            self.statusbar.SetStatusText("Ready")
            self.isstatusbar = True
            
    def buildToolBar(self):
            self.istoolbar = True            
            events = self.eventsHandler 
            toolbar1 = self.CreateToolBar()
            topen = os.path.join(self.iconPath, 'topen.png')
            assert os.path.exists(topen), 'topen=%r' % topen
            topen = wx.Image(topen, wx.BITMAP_TYPE_ANY)
            topen = toolbar1.AddLabelTool(1, '', wx.BitmapFromImage(topen), longHelp='Loads a Model')

            tcamera = wx.Image(os.path.join(self.iconPath, 'tcamera.png'), wx.BITMAP_TYPE_ANY)
            camera = toolbar1.AddLabelTool(4, '', wx.BitmapFromImage(tcamera), longHelp='Take a Screenshot')

            texit = wx.Image(os.path.join(self.iconPath, 'texit.png'), wx.BITMAP_TYPE_ANY)
            etool = toolbar1.AddLabelTool(wx.ID_EXIT, '', wx.BitmapFromImage(texit), longHelp='Exit App')
            toolbar1.Realize()

            self.toolbar1 = toolbar1

# Bind  Toolbar items
            self.Bind(wx.EVT_TOOL, events.onExit, id=wx.ID_EXIT)            
            self.Bind(wx.EVT_TOOL, self.vtkPanel.onTakePicture, id=camera.GetId())
            self.Bind(wx.EVT_TOOL, self.vtkPanel.plot, id=topen.GetId())
            
    def buildMenuBar(self):
            events = self.eventsHandler
            menubar = wx.MenuBar()
 # --------- File Menu -------------------------------------------------
            fileMenu = wx.Menu()
            loadModel = fileMenu.Append(wx.ID_NEW,'Load &Model','Loads a Model Input File')
            sys.stdout.flush()
   #         assert os.path.exists(os.path.join(self.iconPath, 'topen.png'))
            loadModel.SetBitmap(wx.Image(os.path.join(self.iconPath,
                                                'topen.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap())

            fileMenu.AppendSeparator()
# ---------     ------------------------------------------------------------
            exitButton = wx.MenuItem(fileMenu,wx.ID_EXIT, 'Exit', 'Exits App')
            exitButton.SetBitmap(wx.Image(os.path.join(self.iconPath, 'texit.png'),wx.BITMAP_TYPE_PNG).ConvertToBitmap())
            fileMenu.AppendItem(exitButton)

        # --------- View Menu -------------------------------------------------
# status bar at bottom - toggles
            viewMenu = wx.Menu()
            camera = viewMenu.Append(wx.ID_ANY,'Take a Screenshot','Take a Screenshot')
            camera.SetBitmap(wx.Image(os.path.join(self.iconPath, 'tcamera.png'),wx.BITMAP_TYPE_PNG).ConvertToBitmap())

#
            viewMenu.AppendSeparator()          
            self.showStatusBar = viewMenu.Append(wx.ID_ANY, 'Show/Hide Statusbar','Show Statusbar')
            self.showToolBar   = viewMenu.Append(wx.ID_ANY, 'Show/Hide Toolbar','Show Toolbar')
            viewMenu.AppendSeparator()                      
            self.bkgColorView = viewMenu.Append(wx.ID_ANY,'Change Background Color','Change Background Color')                                         

# --------- Help / About Menu -----------------------------------------
            helpMenu = wx.Menu()
            self.helpM = helpMenu.Append(wx.ID_ANY, '&About', 'About App')
# menu bar
            menubar.Append(fileMenu, '&File')
            menubar.Append(viewMenu, '&View')
            menubar.Append(helpMenu, '&Help')
            self.menubar = menubar
            self.SetMenuBar(menubar)
#
# Bind all menubar events
#
            self.Bind(wx.EVT_MENU, events.onExit, id=wx.ID_EXIT)
            self.Bind(wx.EVT_MENU, events.onBackgroundColor, id=self.bkgColorView.GetId())
            self.Bind(wx.EVT_MENU, events.onToggleStatusBar, id=self.showStatusBar.GetId())
            self.Bind(wx.EVT_MENU, events.onToggleToolBar, id=self.showToolBar.GetId())
            self.Bind(wx.EVT_MENU, events.onAbout, id=self.helpM.GetId())
            self.Bind(wx.EVT_MENU, self.vtkPanel.plot, id=loadModel.GetId())
            self.Bind(wx.EVT_MENU, self.vtkPanel.onTakePicture, id=camera.GetId())
            
            
    def SetupFrame(self):
            self.eventsHandler = EventsHandler(self)
            self.vtkPanel = vtkPanel(self)
            self.buildMenuBar()
            self.buildToolBar()
            self.Createstatusbar()
# End of Main APP

def Main():
	appPath = sys.path[0]   
	appFilename=sys.argv[0]
	iconPath=os.path.join(appPath,'icons')
	app = wx.App(redirect=False)
	frame = AppFrame(None,"VTK STL viewer : ",iconPath)
	frame.Show()
	app.MainLoop()
if __name__ == "__main__": 
     Main()
