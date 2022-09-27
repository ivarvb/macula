



import png
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

def segmenatation(img, c_r, c_u):
    seg = []
    return seg

def measures(seg, c_r, c_u):
    top = m_top()
    base = m_base()
    middle = m_middle()
    height = m_height()
    return {"top":top,"base":base,"middle":middle,"height":height}

def process_seg_measures(img, c_r, c_u):
    #c_r, c_u = 33, 33
    seg = segmenatation(img, c_r, c_u)
    mea = measures(seg, c_r, c_u)
    return {"centroid":[c_r, c_u], "measures":mea}

def read_tiff_image(path, mm):
    pass

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



process_seg_measures()


#inputdir = '/home/ivar/Downloads/ricardoDS/229074152892482-E-20220706225701/DataFiles/E362/'
#inputdir = '/home/ivar/Downloads/ricardoDS/229074152892482-E-20220706225614/DataFiles/E860/'
inputdir = '/home/ivar/Downloads/macular2/02/229074152892482-E-20220720120127/DataFiles/E638/'

outdir = "/mnt/sda6/software/frameworks/data/macula/2_case/"


#pixel_array
# fetch the path to the test data
#path = get_testdata_file('DICOMDIR')
ds = dcmread(inputdir+'DICOMDIR')
root_dir = Path(ds.filename).resolve().parent
print(f'Root directory: {root_dir}\n')

# Iterate through the PATIENT records
#print(ds)

#fs = FileSet(ds)  # or FileSet(path)

#fil = "6RQJBB89EQJ2B0613K8QDMBV9NLA26IC727IOLS4X2ZU.EX.DCM"
#fil = "6T1MA14ZTQR2B06E723H2EBV9NLA26IC727IOLS4X2ZU.EX.DCM"

#fil = "2HLIQZ354V7K95HH2HOTUBV99GA43E6J27IOLS4X2ZU.EX.DCM"
fil = "3UKGDQITEBH7K95HH2HOTSBV99GA43E6J27IOLS4X2ZU.EX.DCM" ### good 1024x1024
#fil = "3UIMUGXTF1E7K95HH2HOTSBV99GA43E6J27IOLS4X2ZU.EX.DCM"
#fil = "3UM2MV2D45N7K95HH2HOTSBV99GA43E6J27IOLS4X2ZU.EX.DCM" ### good
#fil = "3UP07WJGCHM7K95HH2HOTSBV99GA43E6J27IOLS4X2ZU.EX.DCM"
#fil = "3UQMH12VCKD7K95HH2HOTSBV99GA43E6J27IOLS4X2ZU.EX.DCM"
#fil = "3USG0ANO5LB7K95HH2HOTSBV99GA43E6J27IOLS4X2ZU.EX.DCM"


#fil = "output-jpeg.dcm"

filee = os.path.join(inputdir, fil)
fileo = os.path.join(outdir, "_out.jpg")
dsx = pydicom.read_file(os.path.join(inputdir, fil), force=True) # read dicom image
#dsx = dcmread(filee, force=True)
#dsx.decompress()
""" r = gdcm.Reader()
r.SetFileName( os.path.join(inputdir, fil) )
if r.Read():
    print("error")
    file = r.GetFile()
    print(file)
    dataSet = file.GetDataSet()

    # Retrieve header
    header = file.GetHeader()
    stf = gdcm.StringFilter()
    #print(stf)
    #print (r.GetImage()) # An abstract Image object has been filled """
#print(dsx)
#d = dsx.PixelData
#dsx.PixelData = pydicom.encaps.defragment_data(dsx.PixelData)
#print("d",d)
#with open(fileo, 'wb') as f:
#    f.write(d)

print(dsx)
#print(dsx.PixelData)

new_image = dsx.pixel_array
print("new_image", new_image.shape)
print("new_image", new_image)

""" for record in ds.DirectoryRecordSequence:
    #print("ff", ff)

    if record.DirectoryRecordType == "IMAGE":
        #print("ff", record.ReferencedFileID)
        path = os.path.join(inputdir, record.ReferencedFileID)
        dcm = pydicom.read_file(path)
        #from pydicom import dcmread
        #print("dcm", dcm)
        if 'PixelData' in dcm:
            y = np.array(dcm.pixel_array, dtype=int)

            print("dcm", Y) """
        



read_dir_dicom()
read_tiff_image(path, mm)
files = [   
            {"pfile":"asdfa", "mm":9.9, "srow":99, "scol":99},
            {"pfile":"asdfa", "mm":9.9, "srow":99, "scol":99},
            {"pfile":"asdfa", "mm":9.9, "srow":99, "scol":99},
            {"pfile":"asdfa", "mm":9.9, "srow":99, "scol":99},
        ]
#exit()

execute(files)

