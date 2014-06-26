from modelr.web.urlargparse import reflectivity_type
from modelr.constants import REFLECTION_MODELS
from modelr.reflectivity import get_reflectivity


short_description = ('Define the physical limits, domain, and reflectivity model of the earth')
def add_arguments(parser):

    
    parser.add_argument('units', type=str, default='depth',
                        help="z-axis domain",
                        choices=['time', 'depth'])

    parser.add_argument('depth', type=float, default=1000.0,
                       help="z-range of model")

    parser.add_argument('hor_domains', type=str, default='spatial only',
                        help="horizontal domain(s)",
                        choices=['spatial only', 
                                 'spatial, angle, and frequency', 
                                 #'spatial, and frequency',# not implemented yet
                                 #'spatial, and angle'   # not implemented yet
                                 ]
                                 )    
    
    parser.add_argument('reflectivity_method',
                        type=reflectivity_type,
                        help='Reflectivity model',
                        default='akirichards',
                        choices=REFLECTION_MODELS.keys()) 
 
    return parser

def run_script():
    pass
