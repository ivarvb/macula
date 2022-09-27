from vx.macula.Measure import *
import numpy as np
import math

""" def bbox(pol):
    minx, miny = np.inf, np.inf
    maxx, maxy = -np.inf, -np.inf
    
    for p in pol[0]["outters"]:
        x, y = p[0], p[1]
        if x<minx:
            minx = x
        if y<miny:
            miny = y

        if x>maxx:
            maxx = x
        if y>maxy:
            maxy = y
            
    return {"x":minx, "y":miny, "width":(maxx-minx), "height":(maxy-miny)} """

def distnacet2mm(p1,p2):
    rowPixelSpacing = 0.001955034
    colPixelSpacing = 0.008797654

    r1, r2 = p1[0], p2[0]
    c1, c2 = p1[1], p2[1]
    
    d = math.sqrt( ( (r1-r2) * rowPixelSpacing)**2 + ((c1-c2) * colPixelSpacing)**2)
    return d


def convet2um(mm):
    return mm * 1000.0

def convet2um2(mm):
    return mm * 1000000.0

def area2mm(area):
    rowPixelSpacing = 0.001955034
    colPixelSpacing = 0.008797654
    return area * rowPixelSpacing * colPixelSpacing 


class Segmentation:

    @staticmethod
    def sem_pro(cx, cy):
        pint = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/one/"
        pout = "/mnt/sda6/software/frameworks/data/macula/1_case_FTMH_PP/two/"
        fi_origin = pint+"2_0_original.png"
        fi_mean = pint+"2_2_mean.png"
        fi_binary_w_h = pint+"2_3_binary_with_holes.png"
        fi_binary = pint+"2_4_binary.png"
        fi_contour = pint+"2_5_edges.png"
        r, c = 500, 505
        return segment(fi_origin, fi_mean, fi_binary, fi_binary_w_h, fi_contour, pout, r, c)        

    @staticmethod
    def semi(cx, cy):
        poly, area, bbox, lineup, linemin, linemax = Segmentation.sem_pro(cx, cy)
        print("poly", poly)
        #bounding box
        #bb = bbox(poly)


        p1, p2 = lineup
        #pol = poly
        refs =  [
                    {
                        "label":"R",
                        "labeltext":"macular area",
                        "type":"area",
                        "unitlabel":"um2",
                        "unitvalue":convet2um2(area2mm(area)),
                        "data":bbox,
                        "padding":10
                    },


                    {
                        "label":"a",
                        "labeltext":"up line",
                        "type":"line",
                        "unitlabel":"um",
                        "unitvalue":convet2um(distnacet2mm(p1,p2)),
                        "data":{"r1":p1[0], "c1":p1[1], "r2":p2[0], "c2":p2[1]},
                        "padding":-10
                    },


                    {
                        "label":"b",
                        "labeltext":"middle line",
                        "type":"line",
                        "unitlabel":"um",
                        "unitvalue":convet2um(distnacet2mm(linemin[0],linemin[1])),
                        "data":{"r1":linemin[0][0], "c1":linemin[0][1], "r2":linemin[1][0], "c2":linemin[1][1]},
                        "padding":0
                    },


                    {
                        "label":"c",
                        "labeltext":"bottom line",
                        "type":"line",
                        "unitlabel":"um",
                        "unitvalue":convet2um(distnacet2mm(linemax[0],linemax[1])),
                        "data":{"r1":linemax[0][0], "c1":linemax[0][1], "r2":linemax[1][0], "c2":linemax[1][1]},
                        "padding":20
                    },

                ]

        rs = {
                "macula":poly,
                "targets":refs,
                "rowPixelSpacing":0.001955034,
                "colPixelSpacing":0.008797654,                 
            }
            
        return rs


    
# calcular distancia.... dicom mm
#https://groups.google.com/g/fo-dicom/c/axkk1VFQ50A