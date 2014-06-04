
import numpy as np

short_description = "Build a 3 layer slab model"
def add_arguments(parser):

    parser.add_argument('interface_depth', default=80,
                        type=int, help="The time in milliseconds " +
                        "above and below the wedge")
    parser.add_argument('x_samples', default=350, type=int,
                        help="Number of samples in the " +
                        "x-direction. Will correspond to the number "+
                        "of traces in a seismogram")

    parser.add_argument("margin", default=50, type=int,
                        help="X location of zero thickness")
    parser.add_argument("left", default='0,40', type=int,
                         action='list',
                         help="Thickness on the left-hand side")
    parser.add_argument("right", default='30,130', type=int,
                        action='list',
                        help="Thickness on the right-hand side")
    parser.add_argument("layers", default=3, type=int,
                        help="The number of layers in the model")

    

def run_script(args):
    from modelr.modelbuilder import body_svg, svg2png
    
    l1 = (150,110,110)
    l2 = (110,150,110)
    l3 = (110,110,150)
    
    layers = [l1,l2]
    
    if args.layers == 3:
        layers.append(l3)
        
    body = body_svg(args.interface_depth, args.margin,
                    args.left, args.right, args.x_samples,
                    layers)

    tmpfile = svg2png(body, layers)
    with open(tmpfile.name, 'rb') as f:
        data = f.read()
    

    return data



                        
                        
