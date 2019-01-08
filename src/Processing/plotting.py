#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :1/4/19
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import os
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
import cv2
from mpl_toolkits.axes_grid1 import make_axes_locatable
from utils.imgProcessing import nanRobustBlur, imadjust, imBitConvert, imClip
from utils.imgCrop import imcrop


def plot_birefringence(imgInput, imgs, outputChann, spacing=20, vectorScl=5, zoomin=False, dpi=300, norm=True,
                       plot=True):
    I_trans, retard, azimuth, polarization, ImgFluor = imgs
    scattering = 1 - polarization
    tIdx = imgInput.tIdx
    zIdx = imgInput.zIdx
    posIdx = imgInput.posIdx
    if zoomin:  # crop the images
        imList = [I_trans, retard, azimuth]
        imListCrop = imcrop(imList, I_trans)
        I_trans, retard, azimuth = imListCrop

    azimuth_degree = azimuth / np.pi * 180

    '''
    Call PolColor
        creates 3 ooverlays: Orientation + Retardance, +Scattering, +Transmission-Retardance
    '''
    I_azi_ret_trans, I_azi_ret, I_azi_scat = PolColor(I_trans, retard, azimuth_degree, scattering, norm=norm)

    '''
    Matplotlib 3x2 figure of images
    '''
    if plot:
        plot_recon_images(I_trans, retard, azimuth, scattering, I_azi_ret, I_azi_scat, zoomin=False, spacing=spacing,
                          vectorScl=vectorScl, dpi=dpi)
        if zoomin:
            figName = 'Transmission+Retardance+Orientation_Zoomin.png'
        else:
            figName = 'Transmission+Retardance+Orientation_t%03d_p%03d_z%03d.png' % (tIdx, posIdx, zIdx)

        plt.savefig(os.path.join(imgInput.ImgOutPath, figName), dpi=dpi, bbox_inches='tight')

    '''
    Calls composite Image
        these images are passed to multiDimProcess as 'imgs', then to 'exportImg' for writing to disk.
        
    '''
    IFluorRetard = CompositeImg([100 * retard, ImgFluor[3, :, :] * 1, ImgFluor[2, :, :] * 1], norm=norm)
    I_fluor_all_retard = CompositeImg([100 * retard, ImgFluor[3, :, :] * 1, ImgFluor[2, :, :] * 1,
                                       ImgFluor[1, :, :] * 1, ImgFluor[0, :, :] * 1], norm=norm)

    #==============
    I_trans = imBitConvert(I_trans * 10 ** 3, bit=16, norm=norm)  # AU, set norm to False for tiling images
    retard = imBitConvert(retard * 10 ** 3, bit=16)  # scale to pm
    scattering = imBitConvert(scattering * 10 ** 4, bit=16)
    azimuth_degree = imBitConvert(azimuth_degree * 100, bit=16)  # scale to [0, 18000], 100*degree
    #==============

    imagesTrans = [I_trans, retard, azimuth_degree, scattering, I_azi_ret, I_azi_scat,
                   I_azi_ret_trans]  # trasmission channels
    imagesFluor = [imBitConvert(ImgFluor[i, :, :] * 500, bit=16, norm=False) for i in range(ImgFluor.shape[0])] + [
        IFluorRetard, I_fluor_all_retard]

    # the images written to disk
    images = imagesTrans + imagesFluor
    chNames = ['Transmission', 'Retardance', 'Orientation', 'Scattering',
               'Retardance+Orientation', 'Scattering+Orientation',
               'Transmission+Retardance+Orientation',
               '405', '488', '568', '640', 'Retardance+Fluorescence', 'Retardance+Fluorescence_all']

    imgDict = dict(zip(chNames, images))
    imgInput.chNames = outputChann
    imgInput.nChann = len(outputChann)
    return imgInput, imgDict


def PolColor(I_trans, retard, azimuth, scattering, norm=True):
    if norm:
        retard = imadjust(retard, tol=1, bit=8)
        I_trans = imadjust(I_trans, tol=1, bit=8)
        scattering = imadjust(scattering, tol=1, bit=8)
        # retard = cv2.convertScaleAbs(retard, alpha=(2**8-1)/np.max(retard))
        # I_trans = cv2.convertScaleAbs(I_trans, alpha=(2**8-1)/np.max(I_trans))
    else:
        retard = cv2.convertScaleAbs(retard, alpha=100)
        I_trans = cv2.convertScaleAbs(I_trans, alpha=100)
        scattering = cv2.convertScaleAbs(scattering, alpha=2000)
    #    retard = histequal(retard)

    azimuth = cv2.convertScaleAbs(azimuth, alpha=1)
    #    retardAzi = np.stack([azimuth, retard, np.ones(retard.shape).astype(np.uint8)*255],axis=2)
    I_azi_ret_trans = np.stack([azimuth, retard, I_trans], axis=2)
    I_azi_ret = np.stack([azimuth, np.ones(retard.shape).astype(np.uint8) * 255, retard], axis=2)
    I_azi_scat = np.stack([azimuth, np.ones(retard.shape).astype(np.uint8) * 255, scattering], axis=2)
    I_azi_ret_trans = cv2.cvtColor(I_azi_ret_trans, cv2.COLOR_HSV2RGB)
    I_azi_ret = cv2.cvtColor(I_azi_ret, cv2.COLOR_HSV2RGB)
    I_azi_scat = cv2.cvtColor(I_azi_scat, cv2.COLOR_HSV2RGB)  #
    #    retardAzi = np.stack([azimuth, retard],axis=2)
    return I_azi_ret_trans, I_azi_ret, I_azi_scat

def plotVectorField(I, azimuth, R=40, spacing=40,
                    clim=[None, None]):  # plot vector field representaiton of the orientation map,
    # Currently only plot single pixel value when spacing >0.
    # To do: Use average pixel value to reduce noise
    #    retardSmooth = nanRobustBlur(retard, (spacing, spacing))
    #    retardSmooth/np.nanmean(retardSmooth)
    #    R = R/np.nanmean(R)
    U, V = R * spacing * np.cos(2 * azimuth), R * spacing * np.sin(2 * azimuth)
    USmooth = nanRobustBlur(U, (spacing, spacing))  # plot smoothed vector field
    VSmooth = nanRobustBlur(V, (spacing, spacing))  # plot smoothed vector field
    azimuthSmooth = 0.5 * np.arctan2(VSmooth, USmooth)
    RSmooth = np.sqrt(USmooth ** 2 + VSmooth ** 2)
    USmooth, VSmooth = RSmooth * np.cos(azimuthSmooth), RSmooth * np.sin(azimuthSmooth)

    #    azimuthSmooth  = azimuth
    nY, nX = I.shape
    Y, X = np.mgrid[0:nY, 0:nX]  # notice the inversed order of X and Y

    #    I = histequal(I)
    #    figSize = (10,10)
    #    fig = plt.figure(figsize = figSize)
    imAx = plt.imshow(I, cmap='gray', vmin=clim[0], vmax=clim[1])
    plt.title('Orientation map')
    plt.quiver(X[::spacing, ::spacing], Y[::spacing, ::spacing],
               USmooth[::spacing, ::spacing], VSmooth[::spacing, ::spacing],
               edgecolor='g', facecolor='g', units='xy', alpha=1, width=2,
               headwidth=0, headlength=0, headaxislength=0,
               scale_units='xy', scale=1)

    #    plt.show()
    return imAx

def CompositeImg(images, norm=True):
    img_num = len(images)
    hsv_cmap = cm.get_cmap('hsv', 256)
    color_idx = np.linspace(0, 1, img_num + 1)
    color_idx = color_idx[:-1]  # leave out 1, which corresponds color similar to 0

    ImgColor = []
    idx = 0
    for img in images:
        if norm:
            img_one_chann = imadjust(img, tol=1, bit=8)
        else:
            img_one_chann = imBitConvert(img, bit=8, norm=False)

        img_one_chann = img_one_chann.astype(np.float32,
                                             copy=False)  # convert to float32 without making a copy to save memory
        img_one_chann_rgb = [img_one_chann * hsv_cmap(color_idx[idx])[0], img_one_chann * hsv_cmap(color_idx[idx])[1],
                             img_one_chann * hsv_cmap(color_idx[idx])[2]]
        img_one_chann_rgb = np.stack(img_one_chann_rgb, axis=2)
        ImgColor += [img_one_chann_rgb]
        idx += 1
    ImgColor = np.stack(ImgColor)
    ImgColor = np.sum(ImgColor, axis=0)
    ImgColor = imBitConvert(ImgColor, bit=8, norm=False)

    return ImgColor


'''
uses matplotlib to construct a nice figure of 6 images
'''
def plot_recon_images(I_trans, retard, azimuth, scattering, I_azi_ret, I_azi_scat, zoomin=False, spacing=20,
                      vectorScl=1, dpi=300):
    R = retard
    R = R / np.nanmean(R)  # normalization
    R = vectorScl * R
    # %%
    figSize = (18, 12)
    fig = plt.figure(figsize=figSize)
    ax1 = plt.subplot(2, 3, 1)
    plt.tick_params(labelbottom=False, labelleft=False)  # labels along the bottom edge are off
    ax_trans = plt.imshow(imClip(I_trans, tol=1), cmap='gray')
    plt.title('Transmission')
    plt.xticks([]), plt.yticks([])
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    cbar = fig.colorbar(ax_trans, cax=cax, orientation='vertical')
    #    plt.show()

    ax2 = plt.subplot(2, 3, 2)
    plt.tick_params(labelbottom=False, labelleft=False)  # labels along the bottom edge are off
    ax_retard = plt.imshow(imClip(retard, tol=1), cmap='gray')
    plt.title('Retardance(nm)')
    plt.xticks([]), plt.yticks([])
    divider = make_axes_locatable(ax2)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    cbar = fig.colorbar(ax_retard, cax=cax, orientation='vertical')

    ax3 = plt.subplot(2, 3, 3)
    plt.tick_params(labelbottom=False, labelleft=False)  # labels along the bottom edge are off
    ax_pol = plt.imshow(imClip(scattering, tol=1), cmap='gray')
    plt.title('Scattering')
    plt.xticks([]), plt.yticks([])
    divider = make_axes_locatable(ax3)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    cbar = fig.colorbar(ax_pol, cax=cax, orientation='vertical')

    ax4 = plt.subplot(2, 3, 4)
    plt.tick_params(labelbottom=False, labelleft=False)  # labels along the bottom edge are off
    ax_hv = plt.imshow(imadjust(I_azi_ret, tol=1, bit=8), cmap='hsv')
    plt.title('Retardance+Orientation')
    plt.xticks([]), plt.yticks([])
    divider = make_axes_locatable(ax4)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    cbar = fig.colorbar(ax_hv, cax=cax, orientation='vertical', ticks=np.linspace(0, 255, 5))
    cbar.ax.set_yticklabels([r'$0^o$', r'$45^o$', r'$90^o$', r'$135^o$',
                             r'$180^o$'])  # vertically oriented colorbar
    #    plt.show()

    ax5 = plt.subplot(2, 3, 5)
    imAx = plotVectorField(imClip(retard / 1000, tol=1), azimuth, R=R, spacing=spacing)
    plt.tick_params(labelbottom=False, labelleft=False)  # labels along the bottom edge are off
    plt.title('Retardance(nm)+Orientation')
    plt.xticks([]), plt.yticks([])

    ax6 = plt.subplot(2, 3, 6)
    plt.tick_params(labelbottom=False, labelleft=False)  # labels along the bottom edge are off
    ax_hsv = plt.imshow(imadjust(I_azi_scat, tol=1, bit=8), cmap='hsv')
    # plt.title('Transmission+Retardance\n+Orientation')
    plt.title('Scattering+Orientation')
    plt.xticks([]), plt.yticks([])
    plt.show()
    divider = make_axes_locatable(ax6)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    cbar = fig.colorbar(ax_hsv, cax=cax, orientation='vertical', ticks=np.linspace(0, 255, 5))
    cbar.ax.set_yticklabels([r'$0^o$', r'$45^o$', r'$90^o$', r'$135^o$', r'$180^o$'])  # vertically oriented colorbar


def plot_sub_images(images, titles, ImgOutPath, figName):
    figSize = (12, 12)
    fig = plt.figure(figsize=figSize)
    for i in range(4):
        ax_p = plt.subplot(2, 2, i + 1)
        ax_i = plt.imshow(imadjust(images[i]), 'gray')
        plt.title(titles[i])
        plt.xticks([]), plt.yticks([])
        divider = make_axes_locatable(ax_p)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        cbar = fig.colorbar(ax_i, cax=cax, orientation='vertical')
    plt.show()
    plt.savefig(os.path.join(ImgOutPath, figName), dpi=300, bbox_inches='tight')



