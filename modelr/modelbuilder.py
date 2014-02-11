'''
=====================
modelr.modelbuilder
=====================
'''

# Import what we need
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
import png
import itertools
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

def png2array(infile):
    """
    Turns a PNG into a numpy array.

    :param infile: Path to PNG file
    :returns: a NumPy array.
    """
    
    png_reader = png.Reader(filename=infile.name)
    img = png_reader.asDirect()

    im = np.hstack(itertools.imap(np.uint8, img[2]))
    im = np.reshape(im, (img[1], img[0], 3) )
        
    return im
    
def svg2png(infile, layers):
    """
    Convert an SVG file to PNG file. Uses calls to Imagemagick for the
    conversion.
    
    :param infile: File object output from tempfile.NamedTemporaryFile
                   containing the path to the SVG file.
    :param layers: An array or tuple of RGB values allowed in the
                   output PNG. Should correspond to the number of
                   rocks used in the SVG earth model.
                   ((R,G,B),(R,G,B,))
                   
    :returns: a tempfile.NamedTemporaryFile containing the png of the
             of the model.
    """

    # Map the allowed colourmap for the output PNG
    cmapfile = tempfile.NamedTemporaryFile( suffix='.png',
                                            delete=True )
    cmap = png.from_array( layers,mode='RGB' )
    cmap.save( cmapfile.name )

    # Make the intermediate and output tempfiles
    tmpfile = tempfile.NamedTemporaryFile( suffix='.png',
                                           delete=True )
    outfile = tempfile.NamedTemporaryFile( suffix='.png',
                                           delete=True )

    # Convert to PNG
    command = ['convert',
               '+antialias',
               '-interpolate', 'integer',
                infile.name,
                tmpfile.name]
    subprocess.call(command)

    # Make sure no new colours were added(ie colour interpolation)
    command = ['convert', tmpfile.name,
               '+dither','-remap', cmapfile.name,
                outfile.name]
    subprocess.call(command)

    outfile.seek(0)

    # Cleanup
    tmpfile.close()
    cmapfile.close()
    
    return outfile
    
def svg2array(infile, layers):
    """
    Wrapper for svg2png and png2array.

    :param infile: File object output from tempfile.NamedTemporaryFile
                   containing the path to the SVG file.
    :param layers: An array or tuple of RGB values allowed in the
                   output PNG. Should correspond to the number of
                   rocks used in the SVG earth model.
                   ((R,G,B),(R,G,B,))

    :returns: a numpy array of the RGB levels from the svg.
    """

    pngfile = svg2png(infile, layers)
    arr = png2array(pngfile)
    pngfile.close()

    return arr
    
    
def web2array(url,colours):
    '''
    Given a URL string, make an SVG or PNG on the web into a
    NumPy array.

    :param url: The url path to the SVG or PNG image.
    :param colours: An array or tuple of RGB values allowed in the
                    image ((R,G,B),(R,G,B), ....). Should map to the
                    rocks in the model.
                    
    Returns an array of RGB values.
    '''
    
    # Get the file type from the URL
    suffix = '.' + url.split('.')[-1]
    
    # Make a tempfile with the correct extension
    outfile = tempfile.NamedTemporaryFile(suffix=suffix,
                                          delete=True)

    # Get the file from the web and save into the new temp file name
    urllib.urlretrieve(url,outfile.name)

    
    #
    if suffix == '.png':
        
        # Write the PNG cmap to remove interpolated colours.
        cmapfile = tempfile.NamedTemporaryFile( suffix='.png',
                                                delete=True)
        cmap = png.from_array( colours,mode='RGB' )
        tmpfile = tempfile.NamedTemporaryFile( suffix='.png',
                                               delete=True)
        cmap.save( cmapfile.name )

        command = ['convert', outfile.name,
                   '+dither','-remap', cmapfile.name,
                   tmpfile.name]
        subprocess.call(command)
        arr = png2array(tmpfile)
        # Cleanup temps
        tmpfile.close()
        cmapfile.close()
      
    elif suffix == '.svg':
        arr = svg2array(outfile,colours)
    else:
        pass # Throw an error
    outfile.close()
    return arr
        
        
###########################################
# Code to generate geometries

def channel_svg(pad, thickness, traces, layers):
    """
    Makes a rounded channel.
    Give it pad, thickness, traces, and an iterable of layers.
    Returns an SVG file.

    :param pad: The number (n) of points on top of the channel.
    :param: thickness: The radius of the channel (npoints).
    :param traces: The number of traces in the channel model.
    :param layers: An 3X3 array or tuple of RGB values corresponding
                   to each rock layer. ((R,G,B),(R,G,B),(R,G,B)).
                   Indexed as (top, channel, bottom ).

    :returns: a tempfile object pointed to the model svg file.
    """    
    
    outfile = tempfile.NamedTemporaryFile(suffix='.svg', delete=True )
    
    top_colour = rgb( layers[0][0],layers[0][1], layers[0][2] )
    body_colour = rgb( layers[1][0],layers[1][1], layers[1][2] )
    bottom_colour = rgb( layers[2][0],layers[2][1], layers[2][2] )

    
    width = traces
    height = 2.5*pad + thickness
    
    dwg = svgwrite.Drawing(outfile.name, size=(width,height),
                           profile='tiny')
    
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
    
    # Do this for a file
    dwg.save()
    
    return outfile
     
def body_svg(pad, margin, left, right, traces, layers):
    """
    Makes a body. Used for tilted slabs and wedges.
    Give it pad, left and right thickness, traces, and an iterable of
    layers.
    Returns an SVG file name.

    :param pad: The amount of samples before the first interface.
                Essentially the thickness of the first layer.
    :param margin: The symmetric bottom vertices for the slab. For
                   example, a value of zero would be vertices at the
                   first and last trace, a value of traces/2 would
                   put a vertex in the center, making a triangular
                   shape. Anything in between is trapezoidal.
    :param left: The depths of the wedge interface at the left edge of
                 the plot. A two element tuple(d1,d2) whose difference
                 defines the thickness of the wedge at the left edge.
    :param right: The depths of the wedge interface at the right edge
                  of the plot. A two element tuple(d1,d2) whose
                  difference defines the thickness of the wedge at the
                  right edge.
    :param traces: The number of traces to use in the model.
    :param layers: An array/list/tuple of RGB values that will be
                   mapped to each layer. Indexed as
                   (top, slab, bottom) as RGB values
                   ((R,G,B),(R,G,B), (R,G,B) ).

    :returns: a tempfile object holding the output svg filename.
    """    
    
    outfile = tempfile.NamedTemporaryFile(suffix='.svg',
                                          delete=True)
    
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
    
    # Do this for a file
    dwg.save()

    
    return outfile

###########################################
# Wrappers

def body(pad, margin, left, right, traces, layers):
    """
    Makes a 3 layer earth model with the slabs defined by the user
    parameters.
    
    :param pad: The amount of samples before the first interface.
                Essentially the thickness of the first layer.
    :param margin: The symmetric bottom vertices for the slab. For
                   example, a value of zero would be vertices at the
                   first and last trace, a value of traces/2 would
                   put a vertex in the center, making a triangular
                   shape. Anything in between is trapezoidal.
    :param left: The depths of the wedge interface at the left edge of
                 the plot. A two element tuple(d1,d2) whose difference
                 defines the thickness of the wedge at the left edge.
    :param right: The depths of the wedge interface at the right edge
                  of the plot. A two element tuple(d1,d2) whose
                  difference defines the thickness of the wedge at the
                  right edge.
    :param traces: The number of traces to use in the model.
    :param layers: An array/list/tuple of RGB values that will be
                   mapped to each layer. Indexed as
                   (top, slab, bottom) as RGB values
                   ((R,G,B),(R,G,B), (R,G,B) ).
                   
    :returns: A numpy array of RGB values for the earth model.
    """

    infile = body_svg( pad, margin, left, right, traces, layers )
    arr = svg2array(infile, layers)
    infile.close()
    return arr
    
def channel(pad, thickness, traces, layers):
    """
    Makes a rounded channel.
    Give it pad, thickness, traces, and an iterable of layers.
    Returns an SVG file.
    
    :param pad: The number (n) of points on top of the channel.
    :param: thickness: The radius of the channel (npoints).
    :param traces: The number of traces in the channel model.
    :param layers: An 3X3 array or tuple of RGB values corresponding
                   to each rock layer. ((R,G,B),(R,G,B),(R,G,B)).
                   Indexed as (top, channel, bottom ).

    :returns: a numpy array of the RGB values for the data model.
    """

    infile = channel_svg( pad, thickness, traces, layers )
    arr = svg2array( infile, layers )
    infile.close()

    return arr

# No scripts call these, but we'll leave them here for now;
# they are both just special cases of body. Note, they have not been
# updated and are likely broken.  
def wedge(pad, margin, thickness, traces, layers):
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
    
