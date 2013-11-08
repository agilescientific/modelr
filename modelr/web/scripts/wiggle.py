from agilegeo.wavelet import ricker
import matplotlib.pyplot as plt
import numpy as np

def wiggle(data,dt,skipt=1,gain=1,lwidth=.5):
    """
    param: data: as array      
    param: dt: sample rate in seconds
    param: skipt: number of traces to skip
    param: gain: scaling factor
    param: lwidth: width of line
    """  
    
    t = np.arange(data.shape[0])*dt
    
    for i in range(0,data.shape[1],skipt):
    #               trace=zeros(SH['ns']+2)
    #               dtrace=Data[:,i]
    #               trace[1:SH['ns']]=Data[:,i]
    #               trace[SH['ns']+1]=0
        #trace=np.roll(data[:,i], int(50*np.sin(12*np.pi*(i/180.))) )
        trace = data[:,i]
        
        trace[0]=0
        trace[-1]=0  
        new_trace = gain*(trace/np.amax(data))  
        plt.plot(i+new_trace, t,color='black',linewidth=lwidth, alpha=0.5)
        #fill_index = np.greater(new_trace,np.zeros(trace.shape))
        plt.fill_betweenx(t,i+new_trace, i, new_trace > 0, color='blue', alpha=.5)
        
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