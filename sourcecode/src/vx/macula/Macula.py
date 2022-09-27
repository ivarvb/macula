import numpy as np
import png, os, pydicom

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
import copy


def make_contours(image_p):
    img = np.zeros([image_p.shape[0],image_p.shape[1]], dtype=np.uint8)
    #print("img", img)
    contours, hierarchy = cv2.findContours(image_p, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (255), 1)
    """ 
    # make polygons
    hierarchy = hierarchy[0]
    aupp = []
    for roww, hier in zip(contours, hierarchy):
        pauxpp = np.array([ [r[0][0], r[0][1]] for r in roww ], dtype=int)
        pauxpp = pauxpp.tolist()
        for p in pauxpp:
            img[p[1], p[0]] = 255

    # make interiors contours
    #auhier = [[] for e in hierarchy]
    for i in range(len(aupp)):
        i1d = hierarchy[i][3]
        if i1d != -1:
            #auhier[i1d].append(aupp[i])
            print("aupp[i]", aupp[i])
            for p in aupp[i]:
                img[p[1], p[0]] = 255
    """
    print("img", img)
    
    return img

def fill_holes(img, areav):
    #mask = np.zeros_like(img)
    print(np.shape(img))
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #n = len(contours) # Number of contours 
    cv_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area <= areav:
            cv_contours.append(contour)
            # x, y, w, h = cv2.boundingRect(contour)
            # img[y:y + h, x:x + w] = 255
        else:
            continue
    cv2.fillPoly(img, cv_contours, (255))
    #cv2.imwrite(path_processed, img)


inputdir = '/mnt/sda6/software/frameworks/data/macula/1_case_FTMH/MACULA_FORUM/'
outdir = '/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/one/'

f = "DEMO_RWP_Macular_Hole_19510601_20150522_1130_HD_5_LINE_RASTER_OS_1.2.276.0.75.2.2.42.114374075667668.20150522113006086.33087220.2.dcm"
#os.mkdir(outdir)

test_list = [ f for f in  os.listdir(inputdir)]

#for f in test_list:   # remove "[:10]" to convert all images 
if True:
    fil = os.path.join(inputdir, f)

    ds = pydicom.read_file(fil) # read dicom image

    print("ds",  ds)
    #continue
    #if 'Image Storage' not in ds.SOPClassUID.name:
    #    continue
    
    #*****
    #if not f.endswith(".dcm"):
    #    continue
    #*****
    
    imagerow = []
    if 'PixelData' in ds:
    #if True:
        #rows = int(ds.Rows)
        #cols = int(ds.Columns)
        #print("rows, cols", rows, cols)
        #print("ds.PixelData", ds.PixelData)

        #print("ds.ImageType", ds.ImageType, ds.SOPClassUID)
        

    #if 'PixelSpacing' in ds:
    #    print("Pixel spacing....:", ds.PixelSpacing)        
    
    

        #ds.file_meta = FileMetaDataset()
        #ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

        shape = ds.pixel_array.shape
        #print("shape",shape)
        #*****
        # if ds.ImageType[3] != "HD 5 LINE RASTER" or len(shape)!=3:
        #    continue
        #*****

        print("xxxx", ds.ImageType, ds.SOPClassUID, shape)
        dss = ds.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0]
        SliceThickness = dss.SliceThickness
        rowPixelSpacing = dss.PixelSpacing[0]
        colPixelSpacing = dss.PixelSpacing[1]
        print("QQQQQQQQQ123", SliceThickness, rowPixelSpacing, colPixelSpacing)
        
        rows = int(ds.Rows)
        cols = int(ds.Columns)        
        ccc = 50
        rowsx, colsx = int(ccc*(rows*rowPixelSpacing)), int(ccc*(cols*colPixelSpacing))
        #print("XQQQQQQQQQ123", SliceThickness, ccc*(rows*rowPixelSpacing), ccc*(cols*colPixelSpacing))
        

        
        #for k,v in ds.items():
        #   print(k,v)
        image_2dx = ds.pixel_array.astype(float)
        #image_2dx = apply_modality_lut(image_2dx, ds)
        #print("huxx", image_2dx.shape)
        
        for ii in range(shape[0]):
            imagesv = []

            image_2d = image_2dx[ii,:,:]
            #print("SSS",image_2d.shape)
            shapex = image_2d.shape
            #if len(shape)==3:
            #    print(len(image_2d))
            
            # Rescaling grey scale between 0-255
            image_p = (np.maximum(image_2d,0) / image_2d.max()) * 255.0


            # Convert to uint
            image_p = np.uint8(image_p)
            imagesv.append(("original", image_p))


            #image_p_res = cv2.resize(image_p, dsize=(rowsx, colsx), interpolation=cv2.INTER_CUBIC)
            image_p_res = resize(image_p, (rowsx, colsx))
            #print("image_p_res", image_p_res)
            imagesv.append(("original_huge", image_p_res))

            #image_p = cv2.fastNlMeansDenoising(image_p, 10,10,7,21)
            #imagesv.append(("mean", image_p))

            image_p = cv2.medianBlur(image_p, 17)
            imagesv.append(("mean", image_p))


            #image_2d_scaled_b = cv2.GaussianBlur(image_2d_scaled,(15,15),0)
            #imagesv.append(("blur", image_2d_scaled_b))


            #image_p = image_p

            #ret,image_2d_scaled = cv2.threshold(image_2d_scaled,50,255,cv2.THRESH_BINARY)
            ret,image_p = cv2.threshold(image_p,50,255,cv2.THRESH_BINARY)
            imagesv.append(("binary_with_holes", copy.deepcopy(image_p)))


            fill_holes(image_p, 50000)
            imagesv.append(("binary", image_p))

            #image_p = ndimage.morphology.binary_fill_holes(image_p)


            #edges = cv2.Canny(image_p,100,200)

            edges = make_contours(image_p)
            imagesv.append(("edges", edges))

            image_p = cv2.morphologyEx(image_p, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
            imagesv.append(("morphology", image_p))

            image_p = cv2.erode(image_p, np.ones((2,2),np.uint8), iterations = 1)
            imagesv.append(("erode", image_p))

            #print(image_2d_scaled)

            # segmentation v2
            #ret,image_2d_scaled = cv2.threshold(image_2d_scaled,50,255,cv2.THRESH_BINARY)
            # segmentation v1
            #image_2d_scaled[np.where(image_2d_scaled<50)] = 0 
            #print("min",image_2d_scaled.min())



            num_labels, labels = cv2.connectedComponents(image_p)
            label_hue = np.uint8(179*labels/np.max(labels))
            blank_ch = 255*np.ones_like(label_hue)
            labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

            labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

            labeled_img[label_hue==0] = 0
            #print("labeled_img", labeled_img)
            imagesv.append(("components", labeled_img))
            
            """ 
            # Write the PNG file
            with open(os.path.join(outdir, str(ii)+'.png'), 'wb') as png_file:
                w = png.Writer(shapex[1], shapex[0], greyscale=True)
                w.write(png_file, image_2d_scaled) """
            imagerow.append(imagesv)

    for i in range(len(imagerow)):
        for j in range(len(imagerow[i])):
            name, img = imagerow[i][j]
            shape = img.shape
            
            isgray = True
            if len(shape)==3:
                isgray = False

            
            print("shape", len(shape), name)
            if isgray:
                with open(os.path.join(outdir, str(i)+'_'+str(j)+'_'+name+'.png'), 'wb') as png_file:
                    w = png.Writer(shape[1], shape[0], greyscale=isgray)
                    w.write(png_file, img)
            else:
                cv2.imwrite(os.path.join(outdir, str(i)+'_'+str(j)+'_'+name+'.png'), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))    

    #print(ds.Modality, f,image_2d.shape)
    #img = ds.pixel_array # get image array
    #img = cv2.equalizeHist(img)

    #cv2.imwrite(os.path.join(outdir, f.replace('.dcm','.png')),img) # write png image
    

    #plt.imshow(ds)
    #plt.show()


    #print(ds, f)







#### denoise
# https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_Image_Non-local_Means_Denoising_Algorithm_Noise_Reduction.php

