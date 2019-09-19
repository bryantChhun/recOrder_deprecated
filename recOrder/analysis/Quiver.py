# bchhun, {2019-09-18}

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PyQt5.QtWidgets import QApplication
import cv2


def plotVectorField(img,
                    orientation,
                    anisotropy=1,
                    spacing=20,
                    window=20,
                    linelength=20,
                    linewidth=3,
                    linecolor='g',
                    colorOrient=True,
                    cmapOrient='hsv',
                    threshold=None,
                    alpha=1,
                    clim=[None, None],
                    cmapImage='gray'):
    """Overlays orientation field on the image. Returns matplotlib image axes.

    Options:
        threshold:
        colorOrient: if it is True, then color the lines by their orientation.
        linelength : can be a scalar or an image the same size as the orientation.
    Parameters
    ----------
    img: nparray
        image to overlay orientation lines on
    orientation: nparray
        orientation in radian
    anisotropy: nparray
    spacing: int

    window: int
    linelength: int
        can be a scalar or an image the same size as the orientation
    linewidth: int
        width of the orientation line
    linecolor: str
    colorOrient: bool
        if it is True, then color the lines by their orientation.
    cmapOrient:
    threshold: nparray
        a binary numpy array, wherever the map is 0, ignore the plotting of the line
    alpha: int
        line transparency. [0,1]. lower is more transparent
    clim: list
        [min, max], min and max intensities for displaying img
    cmapImage:
        colormap for displaying the image
    Returns
    -------
    im_ax: obj
        matplotlib image axes
    """

    # plot vector field representaiton of the orientation map

    # Compute U, V such that they are as long as line-length when anisotropy = 1.
    U, V = anisotropy * linelength * np.cos(2 * orientation), anisotropy * linelength * np.sin(2 * orientation)
    USmooth = nanRobustBlur(U, (window, window))  # plot smoothed vector field
    VSmooth = nanRobustBlur(V, (window, window))  # plot smoothed vector field
    azimuthSmooth = 0.5 * np.arctan2(VSmooth, USmooth)
    RSmooth = np.sqrt(USmooth ** 2 + VSmooth ** 2)
    USmooth, VSmooth = RSmooth * np.cos(azimuthSmooth), RSmooth * np.sin(azimuthSmooth)

    nY, nX = img.shape
    Y, X = np.mgrid[0:nY, 0:nX]  # notice the reversed order of X and Y

    # Plot sparsely sampled vector lines
    Plotting_X = X[::spacing, ::spacing]
    Plotting_Y = Y[::spacing, ::spacing]
    Plotting_U = linelength * USmooth[::spacing, ::spacing]
    Plotting_V = linelength * VSmooth[::spacing, ::spacing]
    Plotting_R = RSmooth[::spacing, ::spacing]

    if threshold is None:
        threshold = np.ones_like(X)  # no threshold
    Plotting_thres = threshold[::spacing, ::spacing]
    Plotting_orien = ((azimuthSmooth[::spacing, ::spacing]) % np.pi) * 180 / np.pi

    if colorOrient:
        im_ax = plt.imshow(img, cmap=cmapImage, vmin=clim[0], vmax=clim[1])
        # plt.title('Orientation map')
        plt.quiver(Plotting_X[Plotting_thres == 1], Plotting_Y[Plotting_thres == 1],
                   Plotting_U[Plotting_thres == 1], Plotting_V[Plotting_thres == 1],
                   Plotting_orien[Plotting_thres == 1],
                   cmap=cmapOrient,
                   edgecolor=linecolor, facecolor=linecolor, units='xy', alpha=alpha, width=linewidth,
                   headwidth=0, headlength=0, headaxislength=0,
                   scale_units='xy', scale=1, angles='uv', pivot='mid')
    else:
        im_ax = plt.imshow(img, cmap=cmapImage, vmin=clim[0], vmax=clim[1])
        # plt.title('Orientation map')
        plt.quiver(Plotting_X[Plotting_thres == 1], Plotting_Y[Plotting_thres == 1],
                   Plotting_U[Plotting_thres == 1], Plotting_V[Plotting_thres == 1],
                   edgecolor=linecolor, facecolor=linecolor, units='xy', alpha=alpha, width=linewidth,
                   headwidth=0, headlength=0, headaxislength=0,
                   scale_units='xy', scale=1, angles='uv', pivot='mid')

    return im_ax


def nanRobustBlur(I, dim):
    """Blur image with mean filter that is robust to NaN in the image

    Parameters
    ----------
    I : array
        image to blur
    dim: tuple
        size of the filter (n, n)

    Returns
    Z : array
        filtered image
    -------

    """
    V=I.copy()
    V[I!=I]=0
    VV=cv2.blur(V,dim)
    W=0*I.copy()+1
    W[I!=I]=0
    WW=cv2.blur(W,dim)
    Z=VV/WW
    return Z


def build_quiver_image(image, orientation):

    # Find this computer's display DPI using the current PyQt5 QApplication instance.
    # this should already be set up by napari's context manager
    app = QApplication.instance()
    screen = app.screens()[0]
    dpi = screen.physicalDotsPerInch()
    print("dpi = "+str(dpi))

    fig = plt.figure(figsize=(2048/dpi, 2048/dpi), dpi=dpi)
    ax = fig.gca()
    plotVectorField(image, orientation, spacing=1, window=1, colorOrient=True, linewidth=0.1,
                             linelength=1, clim=[-1, 1])
    ax.axis('off')
    fig.tight_layout(pad=0)
    canvas = FigureCanvasAgg(fig)
    canvas.draw()

    image_from_plot = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
    print("image from buffer size rgb = %s " % len(image_from_plot))

    cols, rows = fig.canvas.get_width_height()
    print("number of colums, rows = (%s, %s)" % (cols, rows))

    image_from_plot = image_from_plot.reshape(rows, cols, 3)

    return image_from_plot
