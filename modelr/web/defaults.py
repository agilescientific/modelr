'''
Created on November 2013

@author: Matt Hall
'''

from modelr.web.urlargparse import reflectivity_type, wavelet_type
from modelr.constants import WAVELETS
from modelr.constants import REFLECTION_MODELS as MODELS

def default_parsers(parser, list_of_parsers):
    
    if 'title' in list_of_parsers:        
        parser.add_argument('title', 
                            default='Plot',
                            type=str,
                            help='The title of the plot'
                            )
    
    if 'ntraces' in list_of_parsers:        
        parser.add_argument('ntraces',
                            default=300,
                            type=int,
                            help='Number of traces'
                            )
        
    if 'pad' in list_of_parsers:
        parser.add_argument('pad',
                            default=50,
                            type=int,
                            help='The time in milliseconds above' +
                            ' and below the wedge'
                            )
                            
    if 'reflectivity_method' in list_of_parsers:
        parser.add_argument('reflectivity_method',
                            type=reflectivity_type,
                            help='Reflectivity Algorithm',
                            default='zoeppritz',
                            choices=MODELS.keys()
                            ) 
                                
    if 'theta' in list_of_parsers:
        parser.add_argument('theta',
                            type=float,
                            action='list',
                            help='Angle of incidence',
                            default=0
                            )
                            
    if 'f' in list_of_parsers:
        parser.add_argument('f',
                            type=float,
                            action='list',
                            help='Frequency of wavelet',
                            default=25
                            )
                            
    if 'colourmap' in list_of_parsers:
        parser.add_argument('colourmap',
                            type=str,
                            help='Matplotlib colourmap, ' +
                            'ageo.co/modelrcolour',
                            choices = ['Greys','seismic','RdBu','BrBG','bwr',
                            'PuOr','RdGy'],
                            default='Greys'
                            )
        
    if 'wiggle_skips' in list_of_parsers:
        parser.add_argument('wiggle_skips',
                            type=int,
                            help='Wiggle traces to skip',
                            default=10
                            )
                                                    
    if 'base1' in list_of_parsers:
        parser.add_argument('base1',
                            type=str,
                            help='Plot 1, base layer',
                            choices=['wiggle', 'variable-density',
                                     'earth-model', 'reflectivity'
                                     #'RGB'    #uncomment for RGB display
                                     ],
                            default='variable-density'
                            )
        
    if 'overlay1' in list_of_parsers:
        parser.add_argument('overlay1',
                            type=str,
                            help='Plot 1, overlay',
                            choices=['none', 'wiggle',
                                     'variable-density',
                                     'earth-model', 'reflectivity', 
                                     #'RGB'  #uncomment for RGB display
                                     ],
                            default='none'
                            )
        
    if 'base2' in list_of_parsers:
        parser.add_argument('base2',
                            type=str,
                            help='Plot 2, base layer',
                            choices=['none', 'wiggle',
                                     'variable-density',
                                     'earth-model', 'reflectivity', 
                                     #'RGB'  #uncomment for RGB display
                                     ],
                            default='none'
                            )
        
    if 'overlay2' in list_of_parsers:
        parser.add_argument('overlay2',
                            type=str,
                            help='Plot 2, overlay',
                            choices=['none', 'wiggle',
                                     'variable-density',
                                     'earth-model', 'reflectivity', 
                                     # 'RGB'     #uncomment for RGB display
                                     ],
                            default='none'
                            )
        
    if 'opacity' in list_of_parsers:
        parser.add_argument('opacity',
                            type=float,
                            help='Opacity of overlays',
                            default=0.5
                            )
    
    if 'wavelet' in list_of_parsers:
        parser.add_argument('wavelet',
                            type=wavelet_type,
                            help='Wavelet type',
                            default='ricker',
                            choices=WAVELETS.keys()
                            )
                            
    if 'aspect_ratio' in list_of_parsers:
        parser.add_argument('aspect_ratio',
                            type=float,
                            help='stretches the dimensions of each plot (bigger with > 1, smaller < 1)',
                            default=1.0
                            )
    
    if 'extraction_twt' in list_of_parsers:
        parser.add_argument('extraction_twt',
                            type=float,
                            help='twt (s) for amplitude extraction or slice',
                            default=0.150
                            )
    
    if 'extract_along' in list_of_parsers:
        parser.add_argument('extract_along',
                            type=str,
                            help='added dimension(s) along which to extract data',
                            choices=[ 'none','spatial','angle','frequency'
                                     ],
                            default='none'
                            )
                                        
    return parser
