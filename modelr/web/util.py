'''
Created on May 3, 2012

@author: sean
'''

import tempfile
from os import unlink
import matplotlib
import matplotlib.pyplot as plt
from agilegeo.wavelet import ricker
import numpy as np

def return_current_figure():
    '''
    Return the current plot as a binary blob. 
    '''
    fig_path = tempfile.mktemp('.png')
    plt.savefig(fig_path) 
    with open(fig_path, 'rb') as fd:
        data = fd.read()
        
    unlink(fig_path)
    
    return data

def wiggle(data, dt, line_colour='black', fill_colour='blue', opacity=0.5, skipt=0, gain=1, lwidth=.5):
    """
    Make a wiggle trace.
    
    param: data: as array      
    param: dt: sample rate in seconds
    param: skipt: number of traces to skip
    param: gain: scaling factor
    param: lwidth: width of line
    """  
    
    t = np.arange(data.shape[0])*dt
    
    for i in range(0,data.shape[1],skipt+1):
    #               trace=zeros(SH['ns']+2)
    #               dtrace=Data[:,i]
    #               trace[1:SH['ns']]=Data[:,i]
    #               trace[SH['ns']+1]=0
        #trace=np.roll(data[:,i], int(50*np.sin(12*np.pi*(i/180.))) )
        trace = data[:,i]
        
        trace[0]=0
        trace[-1]=0  
        new_trace = gain*(trace/np.amax(data))  
        plt.plot(i+new_trace, t, color=line_colour, linewidth=lwidth, alpha=opacity)
        #fill_index = np.greater(new_trace,np.zeros(trace.shape))
        plt.fill_betweenx(t,i+new_trace, i ,  new_trace > 0, color=fill_colour, alpha=opacity, lw=0)
        
        #plt.fill(i+(gain*fill_trace/np.amax(data)),t,'k',linewidth=0)
                
    #plt.grid(True)
    plt.axis('tight')
    plt.gca().invert_yaxis()
    #plt.show()

if __name__ == '__main__':
    dt =0.001
    gain = 1
    temp = ricker(0.256,dt,25)
    ntraces=50
    data =np.zeros((temp.shape[0],ntraces))

    for i in range(ntraces):
        temp = ricker(0.256,dt,25+10*i)
        data[:,i] = temp
    
    wiggle(data,dt,skipt=1,gain=gain)  