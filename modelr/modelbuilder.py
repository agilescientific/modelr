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
from svgwrite import rgb
import subprocess
import tempfile
import urllib
import time
from cStringIO import StringIO
import os
import requests

# Try cairosvg again on EC2 server
#import cairosvg

# TODO
# Add os.path for files
# fix cairosvg
# make 'body' generic
# make adding fluids easy, by intersecting with body?

def check_file(path_to_file, attempts=0, timeout=5, sleep_int=5):
    if attempts < timeout and os.path.exists(path_to_file) and \
      os.path.isfile(path_to_file): 
        try:
            f = open(path_to_file)
            f.close()
            return path_to_file
        except:
            time.sleep(sleep_int)
            check_file(path_to_file, attempts + 1)
            
###########################################
# Image converters

def png2array(infile, colours=0, minimum=None, maximum=None):
    """
    Turns a PNG into a numpy array.
    
    Give it a PNG file name.
    Returns a NumPy array.
    """
    
    if colours == 0: colours = 1024

    img = Image.open(infile.name)
    im = np.array(img.getdata(),
                  np.uint8).reshape(img.size[1], img.size[0], 3)
    
    ar = np.array(im,dtype=np.uint16)
    
    if minimum and maximum and (maximum > minimum):
        amin = ar.min()
        amax = ar.max()
        ar -= amin
        ar *= maximum - minimum
        ar /= amax - amin
        ar += minimum
        
    return ar
    
def svg2png(infile, colours=3):
    """
    Convert SVG file to PNG file.
    Give it the file object.
    Get back a file path to a PNG.
    """

    # Write the PNG output
    outfile = tempfile.NamedTemporaryFile( suffix='.png' )

    command = ['convert', '-antialias', '-interpolate',
               'nearest-neighbor', '-colors', str(colours),
               infile.name,
               outfile.name]
    subprocess.call(command)
    
    outfile.seek(0)
    return outfile
    
def svg2array(infile, colours=2):
    return png2array(svg2png(infile, colours),colours)
    
def web2array(url,colours=0, minimum=None, maximum=None):
    '''
    Given a URL string, make an SVG or PNG on the web into a
    NumPy array.
    Returns an array.
    '''
    # Get the file type from the URL
    suffix = '.' + url.split('.')[-1]
    
    # Make a tempfile with the correct extension
    outfile = tempfile.NamedTemporaryFile(suffix=suffix)

    # Get the file from the web and save into the new temp file name
    urllib.urlretrieve(url,outfile.name)
            
    # Call the correct converter
    if suffix == '.png':
        return png2array(outfile,colours, minimum, maximum)
    elif suffix == '.svg':
        return svg2array(outfile,colours, minimum, maximum)
    else:
        pass # Throw an error
        
        
###########################################
# Code to generate geometries

def channel_svg(pad, thickness, traces, layers, fluid):
    """
    Makes a wedge.
    Give it pad, thickness, traces, and an iterable of layers.
    Returns an SVG file.
    """    
    
    outfile = tempfile.NamedTemporaryFile(suffix='.svg')
    
    top_colour = 'white'
    body_colour = 'red'
    bottom_colour = 'blue'
    
    width = traces
    height = 2.5*pad + thickness
    
    dwg = svgwrite.Drawing(outfile.name, size=(width,height),
                           profile='tiny')
    #dwg = svgwrite.Drawing('not_used.svg', size=(width,height),
    # profile='tiny')
    
    # Draw the bottom layer
    bottom_layer = \
      svgwrite.shapes.Rect(insert=(0,0),
                            size=(width,height)).fill(bottom_colour)
    dwg.add(bottom_layer)
    
    # Draw the body
    body = \
      svgwrite.shapes.Ellipse(center=(width/2,pad/2),
                        r=(0.3*width,pad+thickness)).fill(body_colour)
    dwg.add(body)

    # Draw the top layer
    top_layer = \
      svgwrite.shapes.Rect(insert=(0,0),
                           size=(width,pad)).fill(top_colour)
    dwg.add(top_layer)

    # Do this for a string
    #svg_code = dwg.tostring()
    #outfile = StringIO(svg_code)
    
    # Do this for a file
    dwg.save()
    
    return outfile
     
def body_svg(pad, margin, left, right, traces, layers):
    """
    Makes a body. Used for tilted slabs and wedges.
    Give it pad, left and right thickness, traces, and an iterable of
    layers.
    Returns an SVG file name.
    """    
    
    outfile = tempfile.NamedTemporaryFile(suffix='.svg')
    
    width = traces
    height = 2 * pad + max(left[1],right[1])
    
    dwg = svgwrite.Drawing(outfile.name, size=(width,height),
                           profile='tiny')
    
    # Draw the first layer
    p1 = (0,0)
    p2 = (width, 0)
    p3 = (width, pad+right[0] )
    p4 = (0, pad+right[0] )
    points = (p1,p2,p3,p4)
    dwg.add( svgwrite.shapes.Polygon(points).fill(
        rgb(layers[0][0],layers[0][1], layers[0][2])))
    
    p1 = (0, pad + left[0])
    p2 = (margin, pad + left[0])
    p3 = (width - margin, pad + right[0])
    p4 = (width, pad + right[0])
    p5 = (width, pad + right[1])
    p6 = (width - margin, pad + right[1])
    p7 = (margin, pad + left[1])
    p8 = (0, pad + left[1])
    
    # If we have 3 layers, draw the bottom layer
    if (len(layers)) > 2:
        points = [p8, p7, p6, p5, (width, height), (0,height)]
        subwedge = \
          svgwrite.shapes.Polygon(points).fill(
              rgb(layers[2][0],layers[2][1], layers[2][2]))
        dwg.add(subwedge)
    
    # Draw the body
    points = [p1, p2, p3, p4, p5, p6, p7, p8]
              
    wedge = svgwrite.shapes.Polygon(points).fill(
        rgb(layers[1][0],layers[1][1], layers[1][2]))
    dwg.add(wedge)
    
    # Do this for a string
    #svg_code = dwg.tostring()
    
    # Do this for a file
    dwg.save()
    
    return outfile

###########################################
# Wrappers

def body(pad, margin, left, right, traces, layers, fluid=None):
    colours = len(layers)
    if fluid:
        colours += 1
    return svg2array(body_svg(pad, margin, left, right, traces,
                              layers, fluid),colours)
    
def channel(pad, thickness, traces, layers, fluid=None):
    colours = len(layers)
    if fluid:
        colours += 1
    return svg2array(channel_svg(pad,thickness,traces,layers,fluid),
                     colours)

# No scripts call these, but we'll leave them here for now;
# they are both just special cases of body.   
def wedge(pad, margin, thickness, traces, layers, fluid=None):
    colours = len(layers)
    if fluid:
        colours += 1
    #We are just usin body_svg for everything
    return svg2array(body_svg(pad, margin, (0,0), (0,thickness),
                              traces, layers, fluid),colours)
    
def tilted(pad, thickness, traces, layers, fluid=None):
    colours = len(layers)
    if fluid:
        colours += 1
    return svg2array(body_svg(pad, 0, (0,thickness),
                              (1.5*thickness,2.5*thickness), traces,
                              layers, fluid),colours)
    
    
###########################################
# Test suite

if __name__ == '__main__':
    # This does not work when run in Canopy, I don't know why
    wparray =  web2array('http://www.subsurfwiki.org/mediawiki/images/8/84/Modelr_test_ellipse.svg',colours=3)
    print wparray
    print np.unique(wparray)
