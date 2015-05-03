import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from skimage import io, color, segmentation, exposure
from skimage.morphology import disk, opening, dilation, erosion, skeletonize
from skimage.measure import label


# import screen capture of a sketched geo model
def image_segment(img_location):
    im=io.imread(img_location)

    im = color.rgb2gray(im[0:-1:2, 0:-1:2])

    # compressor to enhance hard edges
    # square each item to obtain the power function
    sqr = im**2
    # Mild gaussian smooth of square -  not so much as to loose sensitivity to amplitude variations
    flt2 = sp.ndimage.filters.gaussian_filter(sqr,21)
    # Apply compressor -  divide the intensity of each original pixel by the square root of smoothed square
    cmprs= im/(np.sqrt(flt2))

    # contrast stretching
    p2, p98 = np.percentile(cmprs, (2, 98))
    rescale = exposure.rescale_intensity(cmprs, in_range=(p2, p98))

    # binarize image with scalar threshold
    cap = ~(color.rgb2gray(rescale) > 0.5)

    # erosion - eliminates small white speckles
    size=3
    selem= disk(size)
    eroded = erosion(cap, selem)

    # dilation - connects edge segments
    # erosion - thins dilated edges
    size1=10
    selem= disk(size1)
    dilated = dilation(eroded, selem)
    eroded1 = erosion(dilated, selem)

    # skeletonize and dilate to get final boundaries
    edges1 = skeleton_th=skeletonize(eroded1)
    s = disk(3)
    openedsk = ~dilation(edges1,s)

    # clear the objects connected to the image border (in this case just the outside white rim)
    clean_border = segmentation.clear_border(~openedsk)

    # label objects in the cleared image
    all_labels, n = label(clean_border, return_num=True)

    # autocrop by eliminating all empty rows and columns on the outside of the image
    non_empty_columns = np.where(all_labels.max(axis=0)>0)[0]
    non_empty_rows = np.where(all_labels.max(axis=1)>0)[0]
    cropBox = (min(non_empty_rows)+120, max(non_empty_rows)-120, min(non_empty_columns)+120, 
               max(non_empty_columns)-120)
    crop = all_labels[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 ]

    # use dilation to enlarges bodies and shrinks edges between bodies
    selem2=disk(15)
    dilated = dilation(crop, selem2)

    def closest(x,y, pixels, offset, best_colours):
        """
        Recursively finds the nearest colour in an image
        from a set of colours given a pixel.

        :param x: The x coordinate of the pixel.
        :param y: The y coordinate of the pixel
        :param offset: The offset to use to the search space.
        :param best_colours: List/Tuple of allowable colours

        :returns: the nearest colour from the best colours set
        """

        if pixels[x,y] in best_colours:
            return pixels[x,y]

        x_low = np.amax((0,x - offset))
        x_high = np.amin((x + offset, pixels.shape[0]-1))
        y_low = np.amax((0,y - offset))
        y_high = np.amin((y + offset, pixels.shape[1]-1))

        x_index = np.concatenate((np.ones(y_high-y_low) * x_low,
                                  np.arange(x_low, x_high),
                                  np.ones(y_high-y_low) * x_high,
                                  np.arange(x_low, x_high)))

        y_index =       np.concatenate((np.arange(y_low,y_high,dtype='int'),
                          np.ones(x_high-x_low,dtype='int')*y_high,
                          np.arange(y_low,y_high,dtype='int'),
                          np.ones(x_high-x_low, dtype='int')*y_low))


        data = pixels[x_index.astype('int'),
                      y_index.astype('int')].flatten()

        counts = np.empty_like(best_colours)
        for i, col in enumerate(best_colours):
            counts[i] = (data==col).sum()

        if (counts.sum()==0):
            return closest(x, y, pixels, offset + 1, best_colours)

        return best_colours[np.argmax(counts)]

    # find locations of borders between bodies - e.g. value is zero ~= color  black
    # replace those values with the value of the closest body
    newest=dilated
    index = np.array(np.where(dilated == 0))

    for x,y in zip(index[0], index[1]):
        newest[x,y] = closest(x,y, dilated, 50,[1,2,3])

    return newest
