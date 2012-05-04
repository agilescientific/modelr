'''
Created on May 3, 2012

@author: sean
'''

import tempfile
from os import unlink
import matplotlib.pyplot as plt

def return_current_figure():
    '''
    Return the current plot as a binary blob. 
    '''
    fig_path = tempfile.mktemp('.jpeg')
    plt.savefig(fig_path)
    
    with open(fig_path, 'rb') as fd:
        data = fd.read()
        
    unlink(fig_path)
        
    return data