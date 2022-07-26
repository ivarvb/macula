from ast import While
import random
import numpy as np
#import png, os, pydicom
import os

import cv2
import os
import pydicom
from pydicom import dcmread
#Ophthalmic Photography 
from pydicom.pixel_data_handlers.util import apply_voi_lut

import matplotlib.pyplot as plt

from pydicom import dcmread
from pydicom.dataset import FileMetaDataset
from pydicom.uid import ImplicitVRLittleEndian


from pydicom.pixel_data_handlers.util import apply_modality_lut
#from scipy import ndimage
from skimage.transform import resize
import random
from PIL import Image
import imageio
import collections


RR = [ 0,-1,-1,-1, 0, 1, 1, 1]
CC = [-1,-1, 0, 1, 1, 1, 0,-1]


def match(img_gray, template, ptout):    
    # Store width and height of template in w and h
    w, h = template.shape[::-1]
    
    # Perform match operations.
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    
    # Specify a threshold
    threshold = 0.8
    
    # Store the coordinates of matched area in a numpy array
    loc = np.where( res >= threshold)
    

    img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    # Draw a rectangle around the matched region.
    for pt in zip(*loc[::-1]):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        cv2.rectangle(img_color, pt, (pt[0] + w, pt[1] + h), (r,g,b), 2)
        print("holaaaa")

    # Show the final image with the matched area.
    #cv2.imshow('Detected',img_rgb)
    cv2.imwrite(os.path.join(ptout, "matchres.png"), img_color)


def mesuare(img_input, ptout, r, c, h, w):
    im = cv2.imread(img_input, cv2.IMREAD_GRAYSCALE)
    print(im)
    #im = np.array(im)

    cropped_image = im[r:r+h, c:c+w]
    print(cropped_image)
    #cv2.imshow("cropped", cropped_image)
    cv2.imwrite(os.path.join(ptout, "crop.png"), cropped_image)


    #match(im, cropped_image, ptout)
def distance(v1, v2):
    #print("v1, v2", v1, v2)
    return np.sqrt(np.sum((np.array(v1) - np.array(v2)) ** 2))  

def get_contour(img_vis, img_cont, p, limit):
    h, w = img_vis.shape[0], img_vis.shape[1]
    rr = [ 0,-1,-1,-1, 0, 1, 1, 1]
    cc = [-1,-1, 0, 1, 1, 1, 0,-1]
    
    co = []
    
    #of = pf[0],pf[0],

    de = collections.deque()
    de.append(p)
    img_vis[p[0], p[1]] = 1
    while de:
        of = de.popleft()
        #print("of", of)
        co.append(of)
        if len(co)>=limit:
            break
        for j in range(len(rr)):
            rj, cj = of[0]+rr[j], of[1]+cc[j]
            if rj < p[0]:
                if rj>=0 and rj<w and cj>=0 and cj<h:
                    if img_vis[rj, cj] == 0 and img_cont[rj, cj] == 255:
                        img_vis[rj, cj] = 1
                        de.append([rj, cj])
                        #img_rgb[rj, cj] = [255,0,0]
                        #img_rgb[rj+0, cj-1] = [0,255,255]
                        #print("dxx",p,of, img_vis[rj+0, cj-1])
        #d = distance(p, of)
        #print("d",d)
    #print(co)
    return co


def get_contour_cut(segs, img, pul, pur):
    #compute: contours
    img_aux = np.zeros([img.shape[0],img.shape[1]], dtype=np.uint8)
    for p in segs:
        img_aux[p[0], p[1]] = 1

    contours, hierarchy = cv2.findContours(img_aux, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    hierarchy = hierarchy[0]
    aupp = []
    for roww, hier in zip(contours, hierarchy):
        pauxpp = np.array([ [r[0][0], r[0][1]] for r in roww ], dtype=int)
        aupp.append(pauxpp.tolist())

    # append only outter contours
    results = []
    for i in range(len(aupp)):
        if hierarchy[i][3] == -1:
            results.append({"outters":aupp[i]})
    ###############################################3

    #compute: boundingbox
    minx, miny = np.inf, np.inf
    maxx, maxy = -np.inf, -np.inf
    for p in results[0]["outters"]:
        x, y = p[0], p[1]
        if x<minx:
            minx = x
        if y<miny:
            miny = y

        if x>maxx:
            maxx = x
        if y>maxy:
            maxy = y
    bb = {"x":minx, "y":miny, "width":(maxx-minx), "height":(maxy-miny)}
    ###############################################3

    #compute: line middle and line max
    linemin = []
    linemax = []
    linemind = np.inf
    linemaxd = -np.inf
    print("maxx-minx", maxx-minx)
    vets = []
    for rr in range(miny, maxy+1):
        vet = []
        for cc in range(minx, maxx+1):
            #if maior dos ups points
            #if rr>pul[1] and cc>pul[0] and rr>pur[1] and cc>pur[0]:
            if rr>pul[0] and rr>pur[0]:
                if img_aux[rr, cc] == 1:
                    vet.append([rr,cc])

        if len(vet)>2:
            #dd = len(vet)
            dd = distance(vet[0], vet[-1])
            vets.append((vet[0], vet[-1], dd))

            if dd>linemaxd:
                linemaxd = dd
                linemax = [vet[0], vet[-1]]
    
    rlinemax = linemax[0][0]
    print("linemax", rlinemax)
    #compute min line
    for p in vets:
        p1, p2, dd = p[0], p[1], p[2]
        print("rr, cc, dd", p1, p2, dd)
        #if min distance and min to maxline
        if dd<linemind and p1[0]<linemax[0][0]:
            linemind = dd
            linemin = [p1, p2]

    print("linemin, linemax", linemin, linemax)
    ###############################################3

    return results, bb, linemin, linemax


def get_top(curv, p):
    max_d = -1
    max_p = p
    o_min = 0 
    o_max = 0 
    for c in curv:
        d = c[0]-p[0]
        d = d*d
        if d > max_d:
            max_d = d
            max_p = c

            o_max += 1 
        else:
            o_min += 1 
        inc = o_max-o_min
        #print("o_max-o_min", inc)
        if inc<0:
        #if inc<0 or di > :
            break
        
    print("max_p", max_p)
    return max_p

# function for line generation
def bresenham(p1, p2):
    line = []
    x1,y1, x2, y2 = p1[1], p1[0], p2[1], p2[0]
    m_new = 2 * (y2 - y1)
    slope_error_new = m_new - (x2 - x1)
 
    y=y1
    for x in range(x1,x2+1):
        line.append([y,x])
        #print("cccccccc(",x ,",",y ,")\n")
 
        # Add slope to increment angle formed
        slope_error_new =slope_error_new + m_new
 
        # Slope error reached limit, time to
        # increment y and update slope error.
        if (slope_error_new >= 0):
            y=y+1
            slope_error_new =slope_error_new - 2 * (x2 - x1)
    
    return line

def getsegment(img, p):
    h, w = img.shape[0], img.shape[1]
    sc = img[p[0],p[1]]
    rs = []

    rr = [ 0,-1,-1,-1, 0, 1, 1, 1]
    cc = [-1,-1, 0, 1, 1, 1, 0,-1]

    de = collections.deque()
    de.append(p)
    img[p[0],p[1]] = 255
    while de:
        of = de.popleft()
        rs.append(of)
        for j in range(len(rr)):
            rj, cj = of[0]+rr[j], of[1]+cc[j]
            if rj>=0 and rj<w and cj>=0 and cj<h:
                if img[rj, cj] == sc:
                    de.append([rj, cj])
                    img[rj, cj] = 255
    return rs

 
def segment(fi_orig, fi_mean, img_input, img_b_w_h, ficontour, ptout, r, c):
    
    img_orig = cv2.imread(fi_orig, cv2.IMREAD_GRAYSCALE)
    img_mean = cv2.imread(fi_mean, cv2.IMREAD_GRAYSCALE)
    img_gray = cv2.imread(img_input, cv2.IMREAD_GRAYSCALE)
    img_binary_w_h = cv2.imread(img_b_w_h, cv2.IMREAD_GRAYSCALE)
    img_cont = cv2.imread(ficontour, cv2.IMREAD_GRAYSCALE)

    img_gray_c = img_gray.copy()

    h, w = img_gray.shape[0],img_gray.shape[1]
    num_labels, labels = cv2.connectedComponents(img_gray)
    img_vis = np.zeros([img_gray.shape[0],img_gray.shape[1]], dtype=np.uint8)

    img_rgb = np.zeros([img_gray.shape[0],img_gray.shape[1],3], dtype=np.uint8)


     
    for ri in range(h):
        for ci in range(w):
            sc = img_orig[ri,ci]
            #sc = img_gray[ri,ci]
            img_rgb[ri,ci] = [sc,sc,sc]

    img_rgb[np.where(img_cont == 255)] = [255,0,0] 
    #print(img_rgb)


    #left
    pf = [0,0]
    for i in range(1,w):
        img_rgb[r, c-i] = [0,255,0]
        if img_cont[r, c-i] == 255:
            pf = [r,c-i]
            break
    

    #right
    pr = [0,0]
    for i in range(1,w):
        img_rgb[r, c+i] = [0,0,255]
        if img_cont[r, c+i] == 255:
            pr = [r, c+i]
            break

    cf = get_contour(img_vis, img_cont, pf, 500)
    cr = get_contour(img_vis, img_cont, pr, 500)

    for ll in cf:
        img_rgb[ll[0], ll[1]] = [195, 0, 255]
    for ll in cr:
        img_rgb[ll[0], ll[1]] = [255, 217, 0]


    pxf = get_top(cf,pf)
    pxr = get_top(cr,pr)
       
    print("pxf,pxr",  pxf, pxr)

    line = bresenham(pxf, pxr)
    for ll in line:
        img_rgb[ll[0], ll[1]] = [19, 191, 68]
        img_rgb[ll[0]-1, ll[1]] = [19, 191, 68]
        
        img_gray[ll[0], ll[1]] = 255
        img_gray[ll[0]-1, ll[1]] = 255


    #seg azul
    segs = getsegment(img_gray, [r, c]) 
    area = len(segs)   
    #print("segs", segs)
    for ll in segs:
        img_rgb[ll[0], ll[1]] = [0, 34, 255]


    polyreg, bbox, linemin, linemax = get_contour_cut(segs, img_cont, pxf, pxr)


    img_rgb[pxf[0], pxf[1]] = [0,255,0]
    img_rgb[pxr[0], pxr[1]] = [0,255,0]

    img_rgb[r, c] = [255,0,0]
    img_rgb[r-1, c] = [255,0,0]
    img_rgb[r+1, c] = [255,0,0]
    img_rgb[r, c-1] = [255,0,0]
    img_rgb[r, c+1] = [255,0,0]

    print("labels xx",labels)
    print(labels.min())
    print(labels.max())
    #img_color = cv2.cvtColor(img_cont, cv2.COLOR_GRAY2RGB)

    """ label_hue = np.uint8(179*labels/np.max(labels))
    blank_ch = 255*np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

    labeled_img[label_hue==0] = 0
    imagesv.append(("components", labeled_img)) """

    #print(img_gray)
    #im = np.array(im)

    #cropped_image = im[r:r+10, c:c+10]
    #print(cropped_image)
    #cv2.imshow("cropped", cropped_image)
    #cv2.imwrite(os.path.join(ptout, "segment.png"), cropped_image)

    #img_color = cv2.cvtColor(img_cont, cv2.COLOR_GRAY2RGB)
    #cv2.rectangle(img_color, (c, r), (c+10, r+10), (0,0,255), 2)
    #cv2.imwrite(os.path.join(ptout, "segment.png"), img_color)
    
    imageio.imwrite(os.path.join(ptout, "crop_o.png"), img_orig[r-200:r+200, c-200:c+200])
    imageio.imwrite(os.path.join(ptout, "crop_m.png"), img_mean[r-200:r+200, c-200:c+200])
    imageio.imwrite(os.path.join(ptout, "crop_b.png"), img_gray_c[r-200:r+200, c-200:c+200])
    imageio.imwrite(os.path.join(ptout, "crop_b_w_h.png"), img_binary_w_h[r-200:r+200, c-200:c+200])
    imageio.imwrite(os.path.join(ptout, "crop_c.png"), img_cont[r-200:r+200, c-200:c+200])
    imageio.imwrite(os.path.join(ptout, "crop_r.png"), img_rgb[r-200:r+200, c-200:c+200])


    return polyreg, area, bbox, (pxf, pxr), linemin, linemax

if __name__ == "__main__":
    """ 
    fi = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/one/2_3_binary.png"
    out = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/two/"
    r1, c1, r2, c2 = 350, 390, 100, 250
    mesuare(fi, out, r1, c1, r2, c2) """

    fi_origin = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/one/2_0_original.png"
    fi_mean = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/one/2_2_mean.png"
    fi_binary_w_h = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/one/2_3_binary_with_holes.png"
    fi_binary = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/one/2_4_binary.png"
    fi_contour = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/one/2_5_edges.png"
    out = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/two/"
    r, c = 500, 505
    segment(fi_origin, fi_mean, fi_binary, fi_binary_w_h, fi_contour, out, r, c)

