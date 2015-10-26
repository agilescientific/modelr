import h5py
from PIL import Image
from argparse import ArgumentParser
import numpy as np
import StringIO

from agilegeo.wavelet import ricker
from modelr.web.scripts.scenario.segment import image_segment
import matplotlib.pyplot as plt
from modelr.web.util import get_figure_data

short_description = ('Wireframe')



def add_arguments(parser):

    
                        
    parser.add_argument('wireframe',
                        type=str,
                        help='Wireframe image encoded in base64',
                        required=True)

    return parser



def run_script(args):

    # ## Make a new string buffer
    # in_buf = StringIO.StringIO()

    # ## Write the decoded string into the buffer
    # buf.write(base64.b64decode(args.wireframe))

    # ## Move to the start of the buffer
    # in_buf.seek(0)

    ## Open the image in PIL
    #image = Image.open(buf)
    processed_data = image_segment(args.wireframe)
    #plt.imshow(processed_data)
    #image = get_figure_data()
    
    dt = .01
    t = 1.0 
    f= 1.

    wave = ricker(t,dt,f)

    seismic = [np.convolve(wave, i, mode='same') for i in np.transpose(processed_data)]
    plt.imshow(seismic)
    image = get_figure_data()
    return (image,)

def main():
    parser = ArgumentParser(usage=short_description,
                            description=__doc__
                            )
                        
    args = parser.parse_args()
    run_script(args)
    
if __name__ == '__main__':
    main()

