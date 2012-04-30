#!/usr/bin/env python
#
#   Python application for calculating angle-dependent p-wave reflectivity
#   using Zoeppritz equations & various approximations.
#
#   Originally written to give insight into limitations of the Zoeppritz
#   approximations and to get more familiar with GUI programming using wxPython
#   and Matplotlib.
#
#   Requires:   Python (2.6 or 2.7)
#               wxPython
#               Numpy & Matplotlib
#
#       Written by: Wes Hamlyn
#       Last Mod:   May 14, 2011
#
#   Use for whatever you like but at your own risk...
#



import wx
import math
import numpy as np

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas



class ZoepFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Zoeppritz Calculator', 
            size=(1015,625))
        self.do_layout()

    def do_layout(self):
        '''Create main panel with controls on it'''
        
        self.panel = wx.Panel(self)
        
        wx.StaticText(self.panel, -1, "Model Parameters", pos=(45, 25))
        
        wx.StaticText(self.panel, -1, "Vp1:", pos=(50, 55))
        self.tcVp1 = wx.TextCtrl(self.panel, -1, "", pos=(80, 50),
            style=wx.TE_PROCESS_ENTER)
        self.tcVp1.SetValue('2500')
        self.Bind(wx.EVT_TEXT_ENTER, self.DrawFigure, self.tcVp1)

        wx.StaticText(self.panel, -1, "Vs1:", pos=(50, 85))
        self.tcVs1 = wx.TextCtrl(self.panel, -1, "", pos=(80, 80),
            style=wx.TE_PROCESS_ENTER)
        self.tcVs1.SetValue('1500')
        self.Bind(wx.EVT_TEXT_ENTER, self.DrawFigure, self.tcVs1)

        wx.StaticText(self.panel, -1, "Rho1:", pos=(42, 115))
        self.tcRho1 = wx.TextCtrl(self.panel, -1, "", pos=(80, 110),
            style=wx.TE_PROCESS_ENTER)
        self.tcRho1.SetValue('2.35')
        self.Bind(wx.EVT_TEXT_ENTER, self.DrawFigure, self.tcRho1)
       
        wx.StaticText(self.panel, -1, "Vp2:", pos=(50, 155))
        self.tcVp2 = wx.TextCtrl(self.panel, -1, "", pos=(80, 150),
            style=wx.TE_PROCESS_ENTER)
        self.tcVp2.SetValue('2300')
        self.Bind(wx.EVT_TEXT_ENTER, self.DrawFigure, self.tcVp2)

        wx.StaticText(self.panel, -1, "Vs2:", pos=(50, 185))
        self.tcVs2 = wx.TextCtrl(self.panel, -1, "", pos=(80, 180),
            style=wx.TE_PROCESS_ENTER)
        self.tcVs2.SetValue('1400')
        self.Bind(wx.EVT_TEXT_ENTER, self.DrawFigure, self.tcVs2)

        wx.StaticText(self.panel, -1, "Rho2:", pos=(42, 215))
        self.tcRho2 = wx.TextCtrl(self.panel, -1, "", pos=(80, 210),
            style=wx.TE_PROCESS_ENTER)
        self.tcRho2.SetValue('2.20')
        self.Bind(wx.EVT_TEXT_ENTER, self.DrawFigure, self.tcRho2)
        
        wx.StaticText(self.panel, -1, "Max Angle:", pos=(10, 245))
        self.tcAngle = wx.TextCtrl(self.panel, -1, "", pos=(80, 240),
            style=wx.TE_PROCESS_ENTER)
        self.tcAngle.SetValue('40')
        self.Bind(wx.EVT_TEXT_ENTER, self.DrawFigure, self.tcAngle)
        
        self.butDraw = wx.Button(self.panel, -1, "Draw", pos=(75, 290))
        self.Bind(wx.EVT_BUTTON, self.DrawFigure, self.butDraw)
        
       
        self.dpi = 72
        self.fig = Figure((11.0, 8.0), dpi=self.dpi)
        self.canvas = FigCanvas(self.panel, -1, self.fig)
        self.canvas.Position = (200, 25)
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.grid()
        self.ax1.title.set_text('Reflection Coefficient vs Angle of Incidence')
        
        
        
        
    def DrawFigure(self, event):
        '''Method that calculates & draws various reflectivity curves'''
        
        # Get the input data from the text controls tc*
        vp1 = float( self.tcVp1.GetValue() )
        vs1 = float( self.tcVs1.GetValue() )
        rho1 = float( self.tcRho1.GetValue() )
        vp2 = float( self.tcVp2.GetValue() )
        vs2 = float( self.tcVs2.GetValue() )
        rho2 = float( self.tcRho2.GetValue() )
        theta_max = int( self.tcAngle.GetValue() )
        
        # Initialize lists for storing calculated reflectivities
        Rpp_ar = []
        Rpp_shuey2 = []
        Rpp_shuey3 = []
        Rpp_bort = []
        Rpp_zoep = []
        Angle = []
        
        # Start the calculations over a range of angles
        for theta1 in range(0, theta_max+1):
            
            # Save the angles...
            Angle.append(theta1)
            
            # Calculate some constants for the approximations
            theta1 = float(theta1)
            p = math.sin( math.radians(float(theta1)) ) / vp1 # ray parameter
            theta2 = math.degrees(math.asin(vp2/vp1*math.sin(math.radians(theta1))))
            drho = rho2-rho1
            dvp = vp2-vp1
            dvs = vs2-vs1
            theta = (theta1+theta2)/2.0
            rho = (rho1+rho2)/2.0
            vp = (vp1+vp2)/2.0
            vs = (vs1+vs2)/2.0

            
            # Calculate Aki & Richards reflectivity...
            term1 = 0.5*(dvp/vp + drho/rho)
            term2 = (0.5*dvp/vp-2*(vs/vp)**2*(drho/rho+2*dvs/vs))*math.sin(math.radians(theta))**2
            term3 = 0.5*dvp/vp*(math.tan(math.radians(theta))**2 - math.sin(math.radians(theta))**2)
            Rpp_ar.append(term1 + term2 + term3)
            
            
            # Calculate some constants for Shuey's approximation
            pr1 = ( (vp1/vs1)**2-2 )/( 2*((vp1/vs1)**2-1) )  #poisson's ratio
            pr2 = ( (vp2/vs2)**2-2 )/( 2*((vp2/vs2)**2-1) )  #poisson's ratio
            dpr = pr2-pr1
            pr = (pr1+pr2)/2
            F = (dvp/vp)/(dvp/vp+drho/rho)
            E = F - 2.0*(1.0+F)*(1.0-2.0*pr)/(1.0-pr)
            
            # Calculate Shuey's 2 & 3-term reflectivity
            NI = 0.5*(dvp/vp + drho/rho)
            GRAD = (E*NI + dpr/((1.0-pr)**2))
            CURV = 0.5*dvp/vp
            Rpp_shuey2.append(NI + GRAD*math.sin(math.radians(theta1))**2)
            Rpp_shuey3.append(NI + GRAD*math.sin(math.radians(theta1))**2 + \
                CURV*(math.tan(math.radians(theta1))**2 - math.sin(math.radians(theta1))**2))
            
            
            # Calculate Bortfelds P-wave reflection coefficient
            term1_bf = 0.5*math.log( (vp2*rho2*math.cos(math.radians(theta1)))/(vp1*rho1*math.cos(math.radians(theta2))) )
            term2_bf = (math.sin(math.radians(theta1))/vp1)**2*(vs1**2-vs2**2)*(2+math.log(rho2/rho1)/math.log(vs2/vs1))
            Rpp_bort.append(term1_bf + term2_bf)
            
            
            # Calculate reflection & transmission angles for Zoeppritz
            theta1 = math.radians(theta1)   # Convert theta1 to radians
            theta2 = math.asin(p*vp2);      # Trans. angle of P-wave
            phi1   = math.asin(p*vs1);      # Refl. angle of converted S-wave
            phi2   = math.asin(p*vs2);      # Trans. angle of converted S-wave
            
            # Matrix form of Zoeppritz Equations... M & N are matricies
            M = np.array([ \
                [-math.sin(theta1), -math.cos(phi1), math.sin(theta2), math.cos(phi2)],\
                [math.cos(theta1), -math.sin(phi1), math.cos(theta2), -math.sin(phi2)],\
                [2*rho1*vs1*math.sin(phi1)*math.cos(theta1), rho1*vs1*(1-2*math.sin(phi1)**2), \
                    2*rho2*vs2*math.sin(phi2)*math.cos(theta2), \
                    rho2*vs2*(1-2*math.sin(phi2)**2)],\
                [-rho1*vp1*(1-2*math.sin(phi1)**2), rho1*vs1*math.sin(2*phi1), \
                    rho2*vp2*(1-2*math.sin(phi2)**2), -rho2*vs2*math.sin(2*phi2)]
                ], dtype='float')
            
            N = np.array([ \
                [math.sin(theta1), math.cos(phi1), -math.sin(theta2), -math.cos(phi2)],\
                [math.cos(theta1), -math.sin(phi1), math.cos(theta2), -math.sin(phi2)],\
                [2*rho1*vs1*math.sin(phi1)*math.cos(theta1), rho1*vs1*(1-2*math.sin(phi1)**2),\
                    2*rho2*vs2*math.sin(phi2)*math.cos(theta2), rho2*vs2*(1-2*math.sin(phi2)**2)],\
                [rho1*vp1*(1-2*math.sin(phi1)**2), -rho1*vs1*math.sin(2*phi1),\
                    -rho2*vp2*(1-2*math.sin(phi2)**2), rho2*vs2*math.sin(2*phi2)]\
                ], dtype='float')
            
            # This is the important step, calculating coefficients for all modes
            # and rays result is a 4x4 matrix, we want the R[0][0] element for
            # Rpp reflectivity only
            Rpp_zoep.append(np.dot(np.linalg.inv(M), N)[0][0])
            
            
            
        # Now we actually do the drawing in the graphics canvas...
        self.ax1.clear()
        self.ax1.plot(Angle, Rpp_zoep, label='Zoeppritz')
        self.ax1.plot(Angle, Rpp_bort, '*', label='Bortfeld')
        self.ax1.plot(Angle, Rpp_ar, label='A & R')
        self.ax1.plot(Angle, Rpp_shuey2, label='Shuey (2-term)')
        self.ax1.plot(Angle, Rpp_shuey3, '--', label='Shuey (3-term)')
        self.ax1.legend(loc='best')
        self.ax1.grid()
        self.ax1.title.set_text('Reflection Coefficient vs Angle of Incidence')
        self.canvas.draw()



if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = ZoepFrame()
    frame.Show(True)
    app.MainLoop()
