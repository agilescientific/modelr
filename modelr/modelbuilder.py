'''
Model builder
Experimental routine to build models from functions of
depth and offset. Pass in one or more functions, in the
order they need to be created. 

Depends on svgwrite and PIL, both of which can be
installed with pip.
    
'''
# Import what we need
from PIL import Image
import numpy as np
import svgwrite
import subprocess

# Try cairosvg again on EC2 server
#import cairosvg

# TODO
# Add os.path for files
# fix cairosvg
# make 'body' generic
# make adding fluids easy, by intersecting with body?

###########################################
# Image converters

def png2array(png_file):
    """
    Turns a PNG into a numpy array.
    """
    
    infile = 'tmp/model.png'
    
    # Use RGB triplets... could encode as Vp, Vs, rho
    #im_color = np.array(Image.open(infile))

    im = np.array(Image.open(infile).convert('P',palette=Image.ADAPTIVE, colors=4),'f')
    return np.array(im,dtype=np.uint8)
   
def svg2png(svg_file, colours):
    """
    Convert SVG file to PNG file.
    Give it the file path.
    Get back a file path to a PNG.
    """

    # Write the PNG output
    # Testing: we will eventually just return the PNG
    infile_name = 'tmp/model.svg'
    outfile_name = 'tmp/model.png'
    
    # To read an SVG file from disk
    #infile = open(infile_name,'r')
    #svg_code = infile.read()
    #infile.close()
    
    # To write a PNG file out
    #outfile = open('model.png','w')
    #cairosvg.svg2png(bytestring=svg_code,write_to=fout)
    
    # Use ImageMagick to do the conversion
    convert = '/opt/local/bin/convert'
    command = [convert, '-colors', str(colours), infile_name, outfile_name]
    
    subprocess.call(command)
        
    # Only need to close file if we're writing with cairosvg
    #outfile.close()

    return outfile_name

###########################################
# Code to generate geometries

def channel_svg(pad, thickness, traces, layers,fluid):
    """
    Makes a wedge.
    Give it pad, thickness, traces, and an iterable of layers.
    Returns an array.
    """    
    
    outfile_name = 'tmp/model.svg'
    
    top_colour = 'white'
    body_colour = 'red'
    fluid_colour = 'green'
    bottom_colour = 'blue'
    
    width = traces
    height = 2*pad + thickness
    
    dwg = svgwrite.Drawing(outfile_name, size=(width,height), profile='tiny')
    
    # Draw the bottom layer
    bottom_layer = svgwrite.shapes.Rect(insert=(0,0), size=(width,height)).fill(bottom_colour)
    dwg.add(bottom_layer)
    
    # Draw the body
    body = svgwrite.shapes.Ellipse(center=(width/2,pad/2), r=(0.3*width,pad+thickness)).fill(body_colour)
    dwg.add(body)

    # Draw the top layer
    top_layer = svgwrite.shapes.Rect(insert=(0,0), size=(width,pad)).fill(top_colour)
    dwg.add(top_layer)

    # Do this for a string
    #svg_code = dwg.tostring()
    
    # Do this for a file
    dwg.save()
    
    return outfile_name
    
def wedge_svg(pad, thickness, traces, layers,fluid):
    """
    Makes a wedge.
    Give it pad, thickness, traces, and an iterable of layers.
    Returns an array.
    """    
    
    outfile_name = 'tmp/model.svg'
    
    width = traces
    height = 2 * pad + thickness
    
    dwg = svgwrite.Drawing(outfile_name, size=(width,height), profile='tiny')
    
    # If we have 3 layers, draw the background
    if len(layers) > 2:
        subwedge = svgwrite.shapes.Rect(insert=(0,pad), size=(width,height-pad)).fill('blue')
        dwg.add(subwedge)
    
    points = [(0, pad), (traces, pad), (traces, height - pad)]
    wedge = svgwrite.shapes.Polygon(points).fill('red')
    dwg.add(wedge)
    
    # Do this for a string
    #svg_code = dwg.tostring()
    
    # Do this for a file
    dwg.save()
    
    return outfile_name
    
def tilted_svg(pad, thickness, traces, layers, fluid):
    """
    Makes a tilted block.
    Give it pad, thickness, traces, and an iterable of layers.
    Returns an array.
    """    
    
    outfile_name = 'tmp/model.svg'
    
    background_colour = 'white'
    slab_colour = 'red'
    fluid_colour = 'green'
    bottom_colour = 'blue'
    
    width = traces
    height = 2 * pad + 2.5 * thickness
    
    dwg = svgwrite.Drawing(outfile_name, size=(width,height), profile='tiny')
    
    p1 = (0, pad)
    p2 = (width, height - pad - thickness)
    p3 = (width, height - pad)
    p4 = (0, pad + thickness)

    # Draw the background, will become the slab as we overlay the upper and lower layers
    slab = svgwrite.shapes.Rect(insert=(0,0), size=(width,height)).fill(slab_colour)
    dwg.add(slab)
    
    # Add fluid, if any
    if fluid:
        fluid = svgwrite.shapes.Rect(insert=(0,0), size=(width,height/2)).fill(fluid_colour)
        dwg.add(fluid)
    
    # Draw the top layer
    points = [(0,0), (width,0), p2, p1]
    toplayer = svgwrite.shapes.Polygon(points).fill(background_colour)
    dwg.add(toplayer)
        
    # Draw the bottom layer
    if len(filter(None,layers)) > 2:
        background_colour = bottom_colour
    points = [p4, p3, (width,height), (0,height)]
    bottomlayer = svgwrite.shapes.Polygon(points).fill(background_colour)
    dwg.add(bottomlayer)
    
    # Draw the slab
    # No longer need this, with new way to draw
    #points = [p1, p2, p3, p4]
    #slab = svgwrite.shapes.Polygon(points).fill('red')
    #dwg.add(slab)
    
    # Do this for a string
    #svg_code = dwg.tostring()
    
    # Do this for a file
    dwg.save()
    
    return outfile_name


###########################################
# Wrappers

def wedge(pad, thickness, traces, layers, fluid=None):
    colours = len(layers)
    if fluid:
        colours += 1
    return png2array(svg2png(wedge_svg(pad,thickness,traces,layers,fluid),colours))
    
def channel(pad, thickness, traces, layers, fluid=None):
    colours = len(layers)
    if fluid:
        colours += 1
    return png2array(svg2png(channel_svg(pad,thickness,traces,layers,fluid),colours))
    
def tilted(pad, thickness, traces, layers, fluid=None):
    colours = len(layers)
    if fluid:
        colours += 1
    return png2array(svg2png(tilted_svg(pad,thickness,traces,layers,fluid),colours))
    
    
###########################################
# Test suite

if __name__ == '__main__':
    wparray =  channel(20,50,300,['rock1','rock2', 'rock3'])
    print wparray
    print np.unique(wparray)