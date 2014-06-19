from modelr.web.urlargparse import reflectivity_type
from modelr.constants import REFLECTION_MODELS
from modelr.reflectivity import get_reflectivity


short_description = ('Define the physical limits, domain, and reflectivity model of the earth')
def add_arguments(parser):

    
    parser.add_argument('depth', type=float, default=1000.0,
                       help="Z range of the model")
    
    parser.add_argument('units', type=str, default='depth',
                        help="Model domain",
                        choices=['time', 'depth'])

    parser.add_argument('reflectivity_method',
                        type=reflectivity_type,
                        help='Reflectivity model',
                        default='akirichards',
                        choices=REFLECTION_MODELS.keys()) 
 
    return parser

def run_script():
    pass
