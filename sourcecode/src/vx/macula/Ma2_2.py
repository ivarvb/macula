4
import time
#import png
import cv2
import os
from pathlib import Path
import numpy as np
import pydicom
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.fileset import FileSet
import gdcm
from os import listdir
from os.path import isfile, join
from pydicom.datadict import tag_for_keyword
from skimage import exposure
#from scipy.ndimage.filters import uniform_filter
#from scipy.ndimage.measurements import variance
from skimage import morphology
import collections
import math
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import d2_absolute_error_score
from sklearn.metrics import mean_squared_log_error
from sklearn.metrics import mean_absolute_percentage_error

import matplotlib.pyplot as plt
import warnings
import SimpleITK as sitk
from skimage.restoration import denoise_nl_means, estimate_sigma
from sklearn.metrics import jaccard_score

# Dice similarity function
def dice(im, contours_true, contours_pred, k=1):
    
    im_true = np.zeros([im.shape[0],im.shape[1]], dtype=np.uint8)
    im_true = cv2.fillPoly(im_true, pts = [contours_true], color=1)

    im_pred = np.zeros([im.shape[0],im.shape[1]], dtype=np.uint8)
    im_pred = cv2.fillPoly(im_pred, pts = [contours_pred], color=1)

    intersection = np.sum(im_pred[im_true==k]) * 2.0
    dice = intersection / (np.sum(im_pred) + np.sum(im_true))

    im_true=np.array(im_true).ravel()
    im_pred=np.array(im_pred).ravel()
    jacc = jaccard_score(im_true, im_pred)

    return dice, jacc


#dice_score = dice(y_pred, y_true, k = 255) #255 in my case, can be 1 
#print ("Dice Similarity: {}".format(dice_score))

def draw_poly(im, poly_true, poly_pred, color1, color2):
    # bottom
    b_true = poly_true[0]
    # top
    t_true = poly_true[1]
    # middle
    m_true = poly_true[2]

    # bottom
    b_pred = poly_pred[0]
    # top
    t_pred = poly_pred[1]
    # middle
    m_pred = poly_pred[2]

    
    p_true = [b_true[1], m_true[1], t_true[1], t_true[0], m_true[0], b_true[0]]
    p_pred = [b_pred[1], m_pred[1], t_pred[1], t_pred[0], m_pred[0], b_pred[0]]
    
    p_true = np.array( p_true, np.int32)
    p_pred = np.array( p_pred, np.int32)
    for p in p_true:
        p[0], p[1] = p[1],p[0]
    for p in p_pred:
        p[0], p[1] = p[1],p[0]

    #print("pts", pts)
    p_true = p_true.reshape((-1, 1, 2))
    p_pred = p_pred.reshape((-1, 1, 2))
        
    im_res = np.zeros([im.shape[0],im.shape[1], 3], dtype=np.uint8)
    im_res = cv2.merge([im, im, im])
    
    #color = (0, 255, 0)
    thickness = 2
    im_res = cv2.polylines(im_res, [p_true], True, color1, thickness, lineType=cv2.LINE_AA)
    im_res = cv2.polylines(im_res, [p_pred], True, color2, thickness, lineType=cv2.LINE_AA)
    im_res = cv2.cvtColor(im_res, cv2.COLOR_BGR2RGB)
    
    dic = dice(im, p_true, p_pred, k=1)

    print("dic jacc",dic)
    return im_res 
    
    

def slope(x1,y1,x2,y2):
    ###finding slope
    if x2!=x1:
        return((y2-y1)/(x2-x1))
    else:
        return 'NA'
def distance_point_line(p1i, p2i, p3i):
    p1, p2, p3 = np.array(p1i), np.array(p2i), np.array(p3i)
    d = np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1)
    return d

def distance(v1, v2):
    #print("v1, v2", v1, v2)
    return np.sqrt(np.sum((np.array(v1) - np.array(v2)) ** 2))  


def max_distance_point_line(pts, pline):
    p1, p2 = pline[0], pline[1]
    p_max = []
    d_max = -1.0
    for p3 in pts:
        d = distance_point_line(p1, p2, p3)
        if d>d_max:
            p_max = p3
            d_max = d
    return p_max
    
def max_distance(ps, pr):
    p_max = []
    d_max = -1.0

    for pi in ps:
        d = distance(pi, pr)
        if d>d_max:
            p_max = pi
            d_max = d
    return p_max

""" def lee_filter(img, size):
    img_mean = uniform_filter(img, (size, size))
    img_sqr_mean = uniform_filter(img**2, (size, size))
    img_variance = img_sqr_mean - img_mean**2

    overall_variance = variance(img)

    img_weights = img_variance / (img_variance + overall_variance)
    img_output = img_mean + img_weights * (img - img_mean)
    return img_output """
    
def fill_holes(imgp, areav):
    img = np.copy(imgp)
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area <= areav:
            cv_contours.append(contour)
        else:
            continue
    cv2.fillPoly(img, cv_contours, (255))
    return img

def contours(im):
    imx= np.zeros([im.shape[0],im.shape[1]], dtype=np.uint8)
    contours, hierarchy = cv2.findContours(im, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(imx, contours, -1, (255), 1)
    return imx

def meanfilter(im):
    h, w = im.shape[0], im.shape[1]

    m = 2
    md = float(m*m)
    new_image = np.zeros((h+(2*m),w+(2*m)), dtype=np.int8 )
    for r in range(m, h):
        for c in range(m, w):
            px = im[r-m:r+m+1, c-m:c+m+1]
            
            pxm = np.average(px)
            #print(pxm)
            pxs = pxm
            #pxs = int(np.sum(px)/md)
            #print("px", pxs, "s")
            #px = 2/len(px)
            new_image[r,c] = pxs

    new_image = new_image[m:h+m, m:w+m]
    print("XX", im.shape, new_image.shape)
    return new_image

def segmentation(imgp, urow, ucol, T):
    rs = {}

    im = np.copy(imgp)
    append_img(rs, "original", np.copy(im)) 

    # SI FUNCIONA!!!!!!!!!!!
    # siiiiiiiiii uncio 0.97
    #im_mean = cv2.fastNlMeansDenoising(im, 16, 12, 16)

    im_mean = cv2.fastNlMeansDenoising(im, 16, 12, 16)

    
    """ # SI FUNCIONA!!!!!!!!!!!
    im_mean = cv2.bilateralFilter(im,0,30,5) """
    

    """
    # SI FUNCIONA!!!!!!!!!!!
    sigma = 0.08
    sigma_est = sigma
    patch_kw = dict(patch_size=3,      # 5x5 patches
                    patch_distance=5,  # 13x13 search area
                    )
    im_mean = denoise_nl_means(im, h=sigma_est*sigma_est, sigma=sigma_est,
                                fast_mode=True, **patch_kw) """


    """ im_mean = cv2.fastNlMeansDenoising(im, 15, 12, 16)
    append_img(rs, "filter_fastmean", np.copy(im_mean)) """

    append_img(rs, "filter_fastmean", np.copy(im_mean))
    im = im_mean
    

    im_norm = (((im - im.min()) / (im.max())) * 255.0).astype(np.uint8)
    append_img(rs, "normalization_max", np.copy(im_norm))
    im = im_norm 


    
    hh, rr = np.histogram(im, bins=256, range=(0,256)) 
    hmaxv, hmaxi = maxhistogram(hh, rr)
    bT = bestTheshold(hh, hmaxv, hmaxi)
    #bT += 4
    print("bT", bT) 

    """ print("hmaxv, hmaxi", hmaxv, hmaxi)
    plt.figure()
    plt.title("Grayscale Histogram")
    plt.xlabel("grayscale value")
    plt.ylabel("pixel count")
    plt.plot(rr[0:-1], hh)  # <- or here    
    plt.savefig(outputdir+"/histogram_"+id+".png", dpi=300, bbox_inches='tight')
    plt.close('all') """

    """ 
    sbT = str(bT)
    if int(sbT[1])<5:
        bT = bT+(10-int(sbT[1]))
        print("bT",bT, sbT, sbT[1] ) """


    ret, im_w_holes = cv2.threshold(im, bT,255,cv2.THRESH_BINARY)
    append_img(rs, "binary_w_holes", np.copy(im_w_holes))
    im = im_w_holes 

    """ #im = cv2.dilate(im)
    im = cv2.morphologyEx(im, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
    rs["dilate"] = np.copy(im) """

    """ im = cv2.adaptiveThreshold(im,50,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,5,5) 
    rs["adaptative"] = np.copy(im) """


    #im_wo_holes = np.copy(im)
    im_wo_holes = fill_holes(im, 50000)
    append_img(rs, "binary_wo_holes", np.copy(im_wo_holes))
    im = im_wo_holes

    # suavisa a morfologia
    # si funcionaªªªª 20,20 0.97
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (18, 18))
    im_morphology = cv2.morphologyEx(im, cv2.MORPH_OPEN, kernel)
    
    #kernel = np.ones((5, 5), np.uint8)
    #img_erosion = cv2.erode(im, kernel)
    #im_morphology = cv2.dilate(img_erosion, kernel)
    append_img(rs, "morphology", np.copy(im_morphology))
    im = im_morphology

    """ im_remove_small = morphology.remove_small_objects(im_morphology, min_size=50000, connectivity=2)
    append_img(rs, "morphology", np.copy(im_remove_small))
    im_morphology = im_remove_small """
    return im_morphology, im_wo_holes, im_w_holes, im_norm, im_mean, rs


def distnacet2mm(p1, p2, rowPixelSpacing, colPixelSpacing):
    """ rowPixelSpacing = 0.25
    colPixelSpacing = 9 """
    #rowPixelSpacing = 0.25
    #colPixelSpacing = 9

    """ r1, c1 = rowPixelSpacing*p1[0], colPixelSpacing*p1[1]
    r2, c2 = rowPixelSpacing*p2[0], colPixelSpacing*p2[1] """

    r1, c1 = p1[0], p1[1]
    r2, c2 = p2[0], p2[1]
    
    d = math.sqrt( ( (r1-r2) )**2 + ( (c1-c2) )**2)
    d = math.sqrt( ( (r1-r2) * rowPixelSpacing)**2 + ((c1-c2) * colPixelSpacing)**2)
    return d

def measures(rs_measures, im, urow, ucol, mm, srow, scol):

    measures_v = rs_measures["measures_v"]
    measures_p = rs_measures["measures_p"]
    for i in range(len(measures_v)):
        pst = measures_p[i]
        d = distnacet2mm(pst[0], pst[1], srow, scol)
        d = d*1000.0
        d = float("{:.2f}".format(d))
        rs_measures["measures_v"][i] = d



def read_dir_dicom():
    from pydicom import dcmread 
    from pydicom.fileset import FileSet

    inputdir = "/home/ivar/Downloads/macular2/dcm"
    onlyfiles = [f for f in listdir(inputdir) if isfile(join(inputdir, f))]
    print(onlyfiles)

    #ds = dcmread(os.path.join(inputdir,'DICOMDIR'))

    #print("ds", ds)
    for file in onlyfiles:
        #tag = tag_for_keyword("PixelSpacing")
        if file.endswith('dcm'):
            pathf = os.path.join(inputdir, file)
            dcm = pydicom.dcmread(pathf)
            try:
                #print("dcm.get_item(tag)", dcm.get_item(tag))
                #dcm[tag] = dcm.get_item(tag)._replace(VR="DS")
                #print(dcm)
                if 'PixelData' in dcm:
                    #print("xxxx", dcm.ImageType, dcm.SOPClassUID)
                    #img = np.array(dcm.pixel_array, dtype=int)
                    img = dcm.pixel_array.astype(float)

                    shape = img.shape
                    #shape2d = (0,0)
                    #print("shape", shape)
                    img2d = []
                    if len(shape)==3:
                        #print("shape 3", shape)
                        dss = dcm.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0]
                        rowPixelSpacing = dss.PixelSpacing[0]
                        colPixelSpacing = dss.PixelSpacing[1]
                        ix = int(shape[0]/2.0)
                        #print("ix3", ix)
                        img2d = img[ix,:,:]
                        #shape2d = 

                    elif len(shape)==2:
                        #print("shape 2", shape)
                        #pass
                        #dss = dcm.SharedFunctionalGroupsSequence.PixelMeasuresSequence[0]
                        
                        rowPixelSpacing = dcm.PixelSpacing[0]
                        colPixelSpacing = dcm.PixelSpacing[1]
                        #print("img22", file, rowPixelSpacing, colPixelSpacing)
                        #print("ok1")
                        img2d = img[:,:]
                        #print("ok2")
                    
                    print("img2d.shape", img2d.shape)
                    image_p = (np.maximum(img2d,0) / img2d.max()) * 255.0
                    image_p = np.uint8(image_p)

                    with open(os.path.join(inputdir, dcm.SOPInstanceUID+'.png'), 'wb') as png_file:
                        w = png.Writer(img2d.shape[1], img2d.shape[0], greyscale=True)
                        w.write(png_file, image_p)

                    print("imgXX", dcm.PatientID, shape, rowPixelSpacing, colPixelSpacing, image_p.max(), image_p.min())
            except:
                print("An exception occurred")


def get_image(pfile):
    split_tup = os.path.splitext(pfile)
    ex = split_tup[1].strip().lower()
    img = []
    
    if ex == ".dcm":
        pass
    elif ex == ".tiff":
        img = cv2.imread(pfile, cv2.IMREAD_GRAYSCALE)
    elif ex==".jpg" or ex==".jpeg":
        img = cv2.imread(pfile, cv2.IMREAD_GRAYSCALE)

    return img

def append_img(d, k, im):
    n = len(d)
    d[str(n+1)+"_"+k] = im

def draw_point(im, pv, color, z):
    h, w = im.shape[0], im.shape[1]
    for p in pv:
        urow, ucol = p[0], p[1]
        #im[urow, ucol] = [255,255,255]
        im[urow, ucol] = color
        for i in range(1,z+1):
            if urow+i<h and urow+i>=0:
                im[urow+i, ucol] = color
            if urow-i<h and urow-i>=0:
                im[urow-i, ucol] = color

            if ucol+i<w and urow+i>=0:
                im[urow, ucol+i] = color
            if ucol-i<w and urow-i>=0:
                im[urow, ucol-i] = color

def get_contour(im, pl, top, ptop, op):
    rws, cls = im.shape[0], im.shape[1]
    im_vis = np.zeros([im.shape[0],im.shape[1]], dtype=np.uint8)
    r1 = [0, 1, 1, 1, 0,-1,-1,-1]
    c1 = [1, 1, 0,-1,-1,-1, 0, 1]
    
    r2l = [-2,-2,-1, 0, 1, 2, 2]
    c2l = [-1,-2,-2,-2,-2,-2,-1]
    
    r2r = [-2,-2,-1, 0, 1, 2, 2]
    c2r = [ 1, 2, 2, 2, 2, 2, 1]

    for i, (ri, ci) in enumerate(zip(r1, c1)):
        jr, jc = pl[0]+ri, pl[1]+ci
        im_vis[jr, jc] = 1

    q = collections.deque()
    if op=="left":
        for i, (ri, ci) in enumerate(zip(r2l, c2l)):
            jr, jc = pl[0]+ri, pl[1]+ci
            if jr>=0 and jr<rws and jc>=0 and jc<cls:
                if im[jr, jc]==255 and im_vis[jr, jc]==0:
                    im_vis[jr, jc] = 1
                    q.appendleft([jr, jc])
    elif op=="right":
        for i, (ri, ci) in enumerate(zip(r2r, c2r)):
            jr, jc = pl[0]+ri, pl[1]+ci
            if jr>=0 and jr<rws and jc>=0 and jc<cls:
                if im[jr, jc]==255 and im_vis[jr, jc]==0:
                    im_vis[jr, jc] = 1
                    q.appendleft([jr, jc])
    
    #q = collections.deque()
    #q.appendleft(pl)
    vlf = []
    c = 0
    while q:
        p = q.pop()

        vlf.append(p)
        im_vis[p[0], p[1]] = 1
        for i, (ri, ci) in enumerate(zip(r1, c1)):
            jr, jc = p[0]+ri, p[1]+ci
            if jr>=0 and jr<rws and jc>=0 and jc<cls:
                if im[jr, jc]==255 and im_vis[jr, jc]==0:
                    q.appendleft([jr, jc])
        if op=="left":
            if p[1]<=top:
                break
        elif op=="right":
            if p[1]>=top:
                break
        if p[0]==ptop[0] and p[1]==ptop[1]:
            c = len(vlf)

    del q
    del im_vis

    return vlf, c

def min_distance_points_list(v_tl_m, v_tr_m):
    xm = np.inf
    xp = [[],[]]
    for pi in v_tl_m:
        for pj in v_tr_m:
            d = distance(pi, pj)
            if d<xm:
                xm = d
                xp = [pi, pj]          
    return xp

def middle_points(v_l, v_r, p_top_1, p_top_2, p1, p2):
    
    dl = distance_point_line(p1, p2, p_top_1)/2.0
    dr = distance_point_line(p1, p2, p_top_2)/2.0
    dv = (dl+dr)/2.0

    pl, pr = [], []
    for p3 in v_l:
        d = distance_point_line(p1, p2, p3)
        if d>=dv:
            pl = p3
            break
    
    for p3 in v_r:
        d = distance_point_line(p1, p2, p3)
        if d>=dv:
            pr = p3
            break
    return [pl, pr]

    
def draw_line(im, p1, p2, c, z):
    return cv2.line(im, (p1[1], p1[0]), (p2[1], p2[0]), c, z, lineType=cv2.LINE_AA)

def perpendicular_point(e_p1, e_p2, m, pref):
    x1, y1, x2, y2 = e_p1[1], e_p1[0], e_p2[1], e_p2[0]
    x3, y3= pref[1], pref[0]

    k = ((y2-y1) * (x3-x1) - (x2-x1) * (y3-y1)) / ((y2-y1)**2 + (x2-x1)**2)
    x4 = x3 - k * (y2-y1)
    y4 = y3 + k * (x2-x1)
    
    return [int(y4), int(x4)]

def pushText(im, text, p1, p2, fs=0.5, rowoff=0, coloff=0, color=(255,0,0)):
    position = ( int((p1[1] + p2[1])/2-(5*fs)+coloff), int((p1[0] + p2[0])/2+(5*fs)+rowoff) )
    #print("position", position)
    cv2.putText(
        im, #numpy array on which text is written
        text, #text
        position, #position at which writing has to start
        cv2.FONT_HERSHEY_COMPLEX_SMALL, #font family
        fs, #font size
        color,
        0, #font stroke
        cv2.LINE_AA) 

def draw_results(im_res, rs):
    #im_res = np.zeros([im.shape[0],im.shape[1], 3], dtype=np.uint8)
    #im_res = cv2.merge([im, im, im])
    ln_bottom = rs["measures_p"][0]
    ln_top = rs["measures_p"][1]
    ln_middle = rs["measures_p"][2]
    ln_hleft = rs["measures_p"][3]
    ln_hright = rs["measures_p"][4]
    ct_left = rs["ct_left"]
    ct_right = rs["ct_right"]

    ln_botton_pj = rs["ln_botton_pj"]
    pt_user_i = rs["pt_user_i"]
    pt_user_c = rs["pt_user_c"]
    pt_user_l = rs["pt_user_l"]
    pt_user_r = rs["pt_user_r"]
    
    #draw_results([p_bottom_1, p_bottom_2],)
    # draw curver contours left, rightt
    draw_point(im_res, ct_left, [0,170,0],1)
    draw_point(im_res, ct_right, [255,0,255],1)  
    
    # draw bottom line and point projection equation
    im_res = draw_line(im_res, ln_botton_pj[0], ln_botton_pj[1], (255,0,0), 1)
    im_res = draw_line(im_res, ln_bottom[0], ln_bottom[1], (0,0,255), 2)
    draw_point(im_res, ln_botton_pj, [0,255,0],3)
    # draw points base left and right
    draw_point(im_res, [ln_bottom[0], ln_bottom[1]], [255,255,255],7)

    
    # draw line - top line two curves
    im_res = draw_line(im_res, ln_top[0], ln_top[1], (0,0,255), 2)
    
    # draw middle line
    im_res = draw_line(im_res, ln_middle[0], ln_middle[1], (0,0,255), 2)
    draw_point(im_res, ln_middle, [255,255,255],7)

    # draw h left and h right lines
    im_res = draw_line(im_res, ln_hleft[0], ln_hleft[1], (0,0,255), 2)
    im_res = draw_line(im_res, ln_hright[0], ln_hright[1], (0,0,255), 2)
    draw_point(im_res, ln_hleft, [255,255,255],7)
    draw_point(im_res, ln_hright, [255,255,255],7)
    
    # draw user point (i), projection base (c), left (l) and right (r)
    draw_point(im_res, [pt_user_i, pt_user_c, pt_user_l, pt_user_r], [255,0,0],3)
    """ # draw two poins - top line  
    draw_point(im_res, [p_top_1, p_top_2], [255,255,255],7) """

    # draw labels
    pushText(im_res, "a", ln_bottom[0], ln_bottom[1], fs=1.5, rowoff=25, coloff=0)
    pushText(im_res, "b", ln_top[0], ln_top[1], fs=1.5, rowoff=-10, coloff=0)
    pushText(im_res, "e", ln_middle[0], ln_middle[1], fs=1.5, rowoff=-20, coloff=0)
    pushText(im_res, "c", ln_hleft[0], ln_hleft[1], fs=1.5, rowoff=0, coloff=-20)
    pushText(im_res, "d", ln_hright[0], ln_hright[1], fs=1.5, rowoff=0, coloff=15)

    im_res = cv2.cvtColor(im_res, cv2.COLOR_BGR2RGB)
    return im_res 

def pointsdetection(im, imo, urow, ucol):
    h, w = im.shape[0], im.shape[1]

    pu = [urow, ucol]
    #im_vis = np.zeros([im.shape[0],im.shape[1]], dtype=np.uint8)
    im_res = np.zeros([im.shape[0],im.shape[1], 3], dtype=np.uint8)
    im_res = cv2.merge([im, im, im])
    
    imo_res = np.zeros([imo.shape[0],imo.shape[1], 3], dtype=np.uint8)
    imo_res = cv2.merge([imo, imo, imo])
    #im_res = cv2.cvtColor(im_res, cv2.COLOR_BGR2RGB) 

    # compute 2 points auxiliar
    pc = [0,ucol]
    for r in range(urow,im.shape[1],1):
        if im[r, ucol]==255:
            pc[0] = r
            break

    pl = [urow,0]
    for c in range(ucol,0,-1):
        if im[urow, c]==255:
            pl[1] = c
            break
    
    pr = [urow,0]
    for c in range(ucol,im.shape[1],1):
        if im[urow, c]==255:
            pr[1] = c
            break
    
    # compute space points contour
    dlru = int(distance(pl, pr))
    ct_left, c_v_bf = get_contour(im, pc, pl[1]-dlru, pl, "left")
    ct_right, c_v_br = get_contour(im, pc, pr[1]+dlru, pr, "right")
    
    # compute points bottom
    p_bottom_1 = max_distance(ct_left[:c_v_bf], pu)
    p_bottom_2 = max_distance(ct_right[:c_v_br], pu)

    # line equation 
    m = slope(p_bottom_1[1],p_bottom_1[0], p_bottom_2[1],p_bottom_2[0])
    e_p1 = [int(-(p_bottom_1[1]-7)*m+p_bottom_1[0]),7]
    e_p2 = [int(-(p_bottom_2[1]-(w-7))*m+p_bottom_2[0]), w-7]

    # compute points top
    p_top_1 = max_distance_point_line(ct_left, [e_p1, e_p2])
    p_top_2 = max_distance_point_line(ct_right, [e_p1, e_p2])


    # compute points middle
    #p_middle = min_distance_points_list(v_bf[c_v_bf:], v_br[c_v_br:])
    p_middle = middle_points(ct_left, ct_right, p_top_1, p_top_2, p_bottom_1, p_bottom_2)

    # compute points h (altura) left right
    p_hleft = perpendicular_point(e_p1, e_p2, m, p_top_1)
    p_hright = perpendicular_point(e_p1, e_p2, m, p_top_2)

    # polygon
    
    ln_bottom = [p_bottom_1, p_bottom_2]
    ln_top = [p_top_1, p_top_2]
    ln_middle = p_middle
    ln_hleft = [p_top_1, p_hleft]
    ln_right = [p_top_2, p_hright]

    ###########
    rs = {
        "measures_k":["bottom", "top", "middle", "hleft", "hright"],
        "measures_v":[0.0, 0.0, 0.0, 0.0, 0.0],
        "measures_p":[
                ln_bottom,
                ln_top,
                ln_middle,
                ln_hleft,
                ln_right
            ],
        "ct_left":ct_left,
        "ct_right":ct_right,
        "ln_botton_pj":[e_p1, e_p2],
        "pt_user_i":pu,
        "pt_user_c":pc,
        "pt_user_l":pl,
        "pt_user_r":pr,
        }

    im_res = draw_results(im_res, rs)
    imo_res = draw_results(imo_res, rs)

    """ ddmaxv = -1.0 
    for p in rs["measures_p"]:
        d =  distance(p[0], p[1])
        if d>ddmaxv:
            ddmaxv = d """

    """
    #draw_results([p_bottom_1, p_bottom_2],)
    # draw curver contours left, rightt
    draw_point(im_res, ct_left, [0,170,0],1)
    draw_point(im_res, ct_right, [255,0,255],1)  
    
    # draw bottom line and point projection equation
    im_res = draw_line(im_res, e_p1, e_p2, (255,0,0), 1)
    im_res = draw_line(im_res, p_bottom_1, p_bottom_2, (0,0,255), 2)
    draw_point(im_res, [e_p1, e_p2], [0,255,0],3)
    # draw points base left and right
    draw_point(im_res, [p_bottom_1, p_bottom_2], [255,255,255],7)

    
    # draw middle line
    im_res = draw_line(im_res, p_middle[0], p_middle[1], (0,0,255), 2)
    draw_point(im_res, p_middle, [255,255,255],7)
    
    # draw line - top line two curves
    im_res = draw_line(im_res, p_top_1, p_top_2, (0,0,255), 2)

    # draw h left and h right lines
    im_res = draw_line(im_res, p_top_1, p_hleft, (0,0,255), 2)
    im_res = draw_line(im_res, p_top_2, p_hright, (0,0,255), 2)
    draw_point(im_res, [p_hleft], [255,255,255],7)
    draw_point(im_res, [p_hright], [255,255,255],7)
    
    # draw user point
    draw_point(im_res, [[urow, ucol]], [255,0,0],3)
    # draw projection base, left and right  user points
    draw_point(im_res, [pc, pl, pr], [255,0,0],3)
    # draw two poins - top line  
    draw_point(im_res, [p_top_1, p_top_2], [255,255,255],7)

    # draw labels
    pushText(im_res, "a", p_bottom_1, p_bottom_2, fs=1.6, rowoff=25, coloff=0)
    pushText(im_res, "b", p_top_1, p_top_2, fs=1.6, rowoff=-10, coloff=0)
    pushText(im_res, "c", p_middle[0], p_middle[1], fs=1.65, rowoff=-20, coloff=0)
    pushText(im_res, "d", p_top_1, p_hleft, fs=1.6, rowoff=0, coloff=-20)
    pushText(im_res, "e", p_top_2, p_hright, fs=1.6, rowoff=0, coloff=15)

    """
    

    return im_res, imo_res, rs

def polygon(im_con):
    return im_con, []

def crop_img(im_res, pu):
    h, w = im_res.shape[0], im_res.shape[1]
    ddmaxv = np.minimum(pu[0], h-pu[0]) 
    if ddmaxv>200:
        ddmaxv=200
    return im_res[pu[0]-ddmaxv:pu[0]+ddmaxv, pu[1]-ddmaxv:pu[1]+ddmaxv]

def maxhistogram(hh, rr):
    #print(len(hh))
    mx = -np.inf
    mi = -1
    for i in range(len(hh)):
        if hh[i]>mx:
            mx = hh[i]
            mi = int(rr[i])
    return mx, mi

def bestTheshold(hh, mx, mi):
    
    tx = -np.inf
    ti = -1
    p1 = [mx, mi]
    p2 = [0, 256.0]
    for i in range(mi+1, len(hh)):
        p3 = [hh[i], i]
        d = distance_point_line(p1, p2, p3)
        if d>tx:
            tx=d
            ti=i
    return ti

def plot_regression(outputdir, oy_true, oy_pred, y_cate):
    fig, ax = plt.subplots(figsize = (5, 5))
    rsc = {}
    labelg = ["a", "b", "c", "d", "e", "identy"]
    cate = ["bottom", "top", "middle", "hleft", "hright"]
    for mms in cate:
        rsc[mms] = {"ytrue":[],"ypred":[]}
        for i,x in enumerate(y_cate):
            if mms==x:
                rsc[mms]["ytrue"].append(oy_true[i])
                rsc[mms]["ypred"].append(oy_pred[i])

        ax.scatter(rsc[mms]["ytrue"], rsc[mms]["ypred"], s=60, alpha=0.7, edgecolors="k", label=mms) 
    
    ax.plot(oy_true, oy_true, color='#ff0000', linestyle='solid', linewidth=0.5)

    plt.legend(labelg)
    plt.xlabel("y")
    plt.ylabel("ŷ")
    plt.grid()
    plt.savefig(outputdir+"/plot.png", dpi=300, bbox_inches='tight')
    plt.close('all')

def plot_time(outputdir, rs):
    fig, ax = plt.subplots(figsize = (5, 5))
    idx, x, y = ["01","02","03","04","05","06","07","08"], [], []
    for i in range(len(rs)):
        id = rs[i]["id"]
        timep = rs[i]["timep"]
        #idx.append(id+1)
        x.append(i)
        y.append(timep)
    
    ax.plot(x, y, color='#0000ff', linestyle='solid', linewidth=0.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(idx)
    #plt.legend(labelg)
    plt.xlabel("Imagem (ID)")
    plt.ylabel("Tempo (s)")
    plt.grid()
    plt.savefig(outputdir+"/time.png", dpi=300, bbox_inches='tight')
    plt.close('all')


def execute(files):
    y_true = []
    y_pred = []
    y_cate = []
    res = []
    for fi in files:
        # BEGIN END
        start_time = time.time()

        outputdir = fi["outputdir"]
        id = fi["id"]
        im = get_image(fi["pfile_o"])


        im_m = cv2.imread(fi["pfile_m"])
        m_measures_v = fi["measures_v"]
        y_cate += fi["measures_k"]

        h, w = im.shape[0], im.shape[1]
        T, mm, urow, ucol, srow, scol = fi["T"], fi["mm"], fi["urow"], fi["ucol"], fi["srow"], fi["scol"]
        
        im_seg, im_wo_holes, im_w_holes, im_mean_norm, im_mean, rs = segmentation(im, urow, ucol, T)

        im_con = contours(im_seg)
        
        im_det, imo_det, rs_measures = pointsdetection(im_con, im, urow, ucol)
        measures(rs_measures, im_con,  urow, ucol, mm, srow/h, scol/w)
        
        # END
        t_time = (time.time() - start_time)







        print(id)
        print("t_time", "{:.2f}".format(t_time))
        print(m_measures_v)
        print(rs_measures["measures_v"])
        print(np.array(m_measures_v)/1000.0)
        print(np.array(rs_measures["measures_v"])/1000.0)
        print()

        append_img(rs, "edges", im_con)

        append_img(rs, "detection_black", im_det)
        append_img(rs, "detection_original", imo_det)

        im_det_crop = crop_img(im_det, [urow, ucol])
        append_img(rs, "crop_detection_black", im_det_crop)

        imo_det_crop = crop_img(imo_det, [urow, ucol])
        append_img(rs, "crop_detection_original", imo_det_crop)

        imo_crop_contour = crop_img(im_con, [urow, ucol])
        append_img(rs, "crop_contour", imo_crop_contour)



        imo_crop = crop_img(im, [urow, ucol])
        append_img(rs, "crop_original", imo_crop)

        imo_crop_mean = crop_img(im_mean, [urow, ucol])
        append_img(rs, "crop_original_mean", imo_crop_mean)

        im_crop_mean_norm = crop_img(im_mean_norm, [urow, ucol])
        append_img(rs, "crop_original_mean_norm", im_crop_mean_norm)

        im_crop_w_holes = crop_img(im_w_holes, [urow, ucol])
        append_img(rs, "crop_original_binary_w_holes", im_crop_w_holes)

        im_crop_wo_holes = crop_img(im_wo_holes, [urow, ucol])
        append_img(rs, "crop_original_binary_wo_holes", im_crop_wo_holes)

        imo_crop_im_wo_holes = crop_img(im_seg, [urow, ucol])
        append_img(rs, "crop_original_binary_morphology", imo_crop_im_wo_holes)

        imo_crop_manual = crop_img(im_m, [urow, ucol])
        append_img(rs, "crop_original_manual", imo_crop_manual)


        im_pol, rs_polygon = polygon(im_mean_norm)
        append_img(rs, "polygon", im_pol)

        equ = cv2.equalizeHist(im)
        append_img(rs, "equ", equ)

        poly = draw_poly(im, fi["measures_p"], rs_measures["measures_p"], (0,255,0), (0,0,255))
        #poly = draw_poly(poly, rs_measures["measures_p"], (0,0,255))

        append_img(rs, "draw_poly_original", poly)

        

        

        
        iy_true, iy_pred = m_measures_v, rs_measures["measures_v"]
        
        y_true += iy_true
        y_pred += iy_pred

        for sk, sim in rs.items():
            cv2.imwrite(os.path.join(outputdir, id+"_"+sk+".png"), sim)

        res.append({
            "id":id,
            "centroid":[urow, ucol],
            "measures":rs_measures,
            "polygon":rs_polygon,
            "timep":t_time
            }) 


    oy_true, oy_pred = np.array(y_true), np.array(y_pred)
    #normalized in milimetros....
    vmax = 1000.0
    y_true, y_pred = oy_true/vmax, oy_pred/vmax

    r2 = r2_score(y_true, y_pred)
    mae = np.sqrt(mean_absolute_error(y_true, y_pred))
    mse = mean_squared_error(y_true, y_pred)
        
    print(":", mae, mse, np.sqrt(mse), r2)
    print()

    
    plot_regression(outputdir, oy_true, oy_pred, y_cate)
    plot_time(outputdir, res)

    return res

outputdir = "/mnt/sda6/software/frameworks/data/macula/experiments"
srow = 2.0
scol = 2.0

files = [
    {"id":"01",
    "pfile_o":"/home/ivar/Downloads/macular3/01/DEMO RWP_Macular Hole__51561aaaa_19510601_Female_HD 5 Line Raster_20150925111843_OD_20220813134600B.tiff",
    "pfile_m":"/home/ivar/Downloads/macular3/01/DEMO RWP_Macular Hole__51561aaaa_19510601_Female_HD 5 Line Raster_20150925111843_OD_20220813134358.tiff",
    "T":57, "mm":9.0, "srow":2.0, "scol":9.0, "ucol":405, "urow":280, "outputdir":outputdir,
    "measures_p":[[[316,382],[315,426]], [[220,370],[211,410]], [[269,388],[270,424]], [[220,365],[318,363]], [[211,410],[316,409]]],
    "measures_k":["bottom", "top", "middle", "hleft", "hright"],
    "measures_v":[506.0, 406.0, 403.0, 391.0, 366.0]
    },

    {"id":"02",
    "pfile_o":"/home/ivar/Downloads/macular3/02/DEMO RWP_Macular Hole__51561aaaa_19510601_Female_HD 5 Line Raster_20150522113006_OS_20220813152221.tiff",
    "pfile_m":"/home/ivar/Downloads/macular3/02/DEMO RWP_Macular Hole__51561aaaa_19510601_Female_HD 5 Line Raster_20150522113006_OS_20220813135218.tiff",
    "T":43, "mm":9.0, "srow":2.0, "scol":9.0, "ucol":725, "urow":510, "outputdir":outputdir,
    "measures_p":[[[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]]],
    "measures_k":["bottom", "top", "middle", "hleft", "hright"],
    "measures_v":[873.0, 862.0, 336.0, 508.0, 485.0]
    },
    
    {"id":"04",
    "pfile_o":"/home/ivar/Downloads/macular3/04/04_FTMH__281552_19621023_Female_HD Radial_20220201175312_OD_20220813140233.tiff",
    "pfile_m":"/home/ivar/Downloads/macular3/04/04_FTMH__281552_19621023_Female_HD Radial_20220201175312_OD_20220813140631M.tiff",
    "T":23, "mm":6.0, "srow":2.0, "scol":6.0, "ucol":400, "urow":280, "outputdir":outputdir,
    "measures_p":[[[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]]],    
    "measures_k":["bottom", "top", "middle", "hleft", "hright"],
    "measures_v":[1164.0, 1224.0, 478.0, 471.0, 515.0]
    },
    
    {"id":"06a",
    "pfile_o":"/home/ivar/Downloads/macular3/06/06_09112021/06_FTMH__311987_19561221_Female_HD Cross_20211109180542_OD_20220813142216B.tiff",
    "pfile_m":"/home/ivar/Downloads/macular3/06/06_09112021/06_FTMH__311987_19561221_Female_HD Cross_20211109180542_OD_20220813142131M.tiff",
    "T":34, "mm":6.0, "srow":2.0, "scol":6.0, "ucol":540, "urow":180, "outputdir":outputdir,
    "measures_p":[[[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]]],    
    "measures_k":["bottom", "top", "middle", "hleft", "hright"],
    "measures_v":[1014.0, 1170.0, 487.0, 417.0, 388.0]
    },

    {"id":"06b",
    "pfile_o":"/home/ivar/Downloads/macular3/06/06_18012021/06_FTMH__311987_19561221_Female_HD Radial_20220118155610_OD_20220813142413B.jpeg",
    "pfile_m":"/home/ivar/Downloads/macular3/06/06_18012021/06_FTMH__311987_19561221_Female_HD Radial_20220118155610_OD_20220813142814M.jpeg",
    "T":33, "mm":6.0, "srow":2.0, "scol":6.0, "ucol":540, "urow":290, "outputdir":outputdir,
    "measures_p":[[[175,405],[146,663]], [[333,411],[352,675]], [[244,471],[248,599]], [[175,403],[335,404]], [[145,675],[352,675]]],    
    "measures_k":["bottom", "top", "middle", "hleft", "hright"],
    "measures_v":[1486.0, 1442.0, 702.0, 455.0, 582.0]
    },

    {"id":"07",
    "pfile_o":"/home/ivar/Downloads/macular3/07/07_FTMH__246792_19510205_Female_HD Radial_20220325145001_OS_20220813143652.tiff",
    "pfile_m":"/home/ivar/Downloads/macular3/07/07_FTMH__246792_19510205_Female_HD Radial_20220325145001_OS_20220813143536.tiff",
    "T":31, "mm":6.0, "srow":2.0, "scol":6.0, "ucol":540, "urow":290, "outputdir":outputdir,
    "measures_p":[[[349,425],[324,646]], [[219,414],[195,661]], [[261,477],[249,604]], [[219,414],[353,419]], [[195,661],[321,669]]],
    "measures_k":["bottom", "top", "middle", "hleft", "hright"],
    "measures_v":[1241.0, 1337.0, 710.0, 379.0, 357.0]
    },

    {"id":"08",
    "pfile_o":"/home/ivar/Downloads/macular3/08/08_FTMH__173000_19370202_Male_HD Radial_20220503163102_OS_20220813143830.jpeg",
    "pfile_m":"/home/ivar/Downloads/macular3/08/08_FTMH__173000_19370202_Male_HD Radial_20220503163102_OS_20220813144153M.tiff",
    "T":33, "mm":6.0, "srow":2.0, "scol":6.0, "ucol":530, "urow":350, "outputdir":outputdir,
    "measures_p":[[[427,424],[394,650]], [[261,465],[246,627]], [[338,482],[328,581]], [[260,458],[424,469]], [[246,637],[397,649]]],
    "measures_k":["bottom", "top", "middle", "hleft", "hright"],
    "measures_v":[1272.0, 911.0, 553.0, 467.0, 427.0]
    },

    {"id":"09",
    "pfile_o":"/home/ivar/Downloads/macular3/09/09_507005_19510106_Female_HD 1 Line 100x_20220714115102_OD_20220813144933B.tiff",
    "pfile_m":"/home/ivar/Downloads/macular3/09/9_507005_19510106_Female_HD 1 Line 100x_20220714115102_OD_20220813145214M.tiff",
    "T":27, "mm":9.0, "srow":2.0, "scol":9.0, "ucol":610, "urow":220, "outputdir":outputdir,
    "measures_p":[[[268,552],[274,661]], [[144,531],[145,692]], [[195,570],[198,647]], [[174,532],[266,522]], [[145,692],[279,689]]],
    "measures_k":["bottom", "top", "middle", "hleft", "hright"],
    "measures_v":[916.0, 1354.0, 649.0, 345.0, 380.0]
    },

    ]

rs = execute(files)

