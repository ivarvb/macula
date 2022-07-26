




import os
from pathlib import Path
import numpy as np
import pydicom
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.fileset import FileSet
import gdcm



#inputdir = '/home/ivar/Downloads/ricardoDS/229074152892482-E-20220706225701/DataFiles/E362/'
inputdir = '/home/ivar/Downloads/ricardoDS/229074152892482-E-20220706225614/DataFiles/E860/'

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

fil = "6T1MA14ZTQR2B06E723H2EBV9NLA26IC727IOLS4X2ZU.EX.DCM"
#fil = "output-jpeg.dcm"

dsx =  pydicom.read_file(os.path.join(inputdir, fil), force=True) # read dicom image

r = gdcm.Reader()
r.SetFileName( os.path.join(inputdir, fil) )
if r.Read():
    print("error")
    file = r.GetFile()
    print(file)
    dataSet = file.GetDataSet()

    # Retrieve header
    header = file.GetHeader()
    stf = gdcm.StringFilter()
    #print (r.GetImage()) # An abstract Image object has been filled
#print(dsx)
print(dsx.pixel_array)
print("dsx")


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
        