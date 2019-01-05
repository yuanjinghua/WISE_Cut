import os
import math
import time
import tarfile
import shutil
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import montage_wrapper as mt
from astropy.io import ascii,fits
from astropy.table import Table, Column, vstack, join
from astropy import units as u
import astropy.coordinates as coords

tileDir = '/run/media/yuan/Yuan-8T/ALLWISE/allwiseTiles/'
wiseTileList = ascii.read('/run/media/yuan/Yuan-8T/ALLWISE/ALLWISE_atlasMeta.tbl')
wiseTileList.sort('coadd_id')

sour_name = 'M31'
c1 = 10.684583333333332 # ra or l in degree
c2 = 41.26916667 # dec or b in degree
im_size = 2.5 # in degree
wcsType = 'fk5' # galactic or fk5 

coor = coords.SkyCoord(c1, c2, frame = wcsType,
                        unit=(u.degree, u.degree))

coors = coords.SkyCoord(wiseTileList['ra'],wiseTileList['dec'],
                        frame = 'fk5', unit = (u.deg,u.deg))
sep = Column(coor.separation(coors).arcsec, 
             name = 'seps')
if 'seps' in wiseTileList.keys():
    wiseTileList.remove_column('seps')
    
wiseTileList.add_column(sep)
wiseTileList.sort('seps')
#print(wiseTileList)
if im_size < 1.5:
    subTiles = list(wiseTileList['coadd_id'][:4])
elif im_size < 3:
    subTiles = list(wiseTileList['coadd_id'][:9])
else :
    subTiles = list(wiseTileList['coadd_id'][:16])
# print(wiseTileList)
#tile = wiseTileList['coadd_id'][sep == min(sep)][0]

pix_size = 0.00038194443914113600
pix_num = int(im_size/pix_size)
center_pix = int(pix_num/2.0+0.5)
fakeData = np.ones((pix_num,pix_num))
hdu = fits.PrimaryHDU(fakeData)
if wcsType == 'galactic':
    ctype1 = 'GLON-TAN'
    ctype2 = 'GLAT-TAN'
elif wcsType == 'fk5':
    ctype1 = 'RA---TAN'
    ctype2 = 'DEC--TAN'
for bands in ['w1', 'w2', 'w3', 'w4']:
    hdr = hdu.header.copy()
    hdr['BUNIT']    = 'DN      '
    hdr['CRVAL1']   = c1
    hdr['CRVAL2']   = c2
    hdr['CTYPE1']   = ctype1
    hdr['CTYPE2']   = ctype2
    hdr['EQUINOX']  = 2000.0
    hdr['CRPIX1']   = center_pix
    hdr['CRPIX2']   = center_pix
    hdr['CDELT1']   =  -0.0003819444391411
    hdr['CDELT2']   =   0.0003819444391411
    hdr['TELESCOP'] = 'WISE'
    hdr['BAND']     = bands
    hdr.totextfile(bands+'.hdr', overwrite = True)

    os.mkdir(bands)
    os.mkdir(bands+'/raw')
    for tile in list(subTiles):
        shutil.copy(tileDir+tile+'-'+bands+'-int-3.fits',
                    bands+'/raw/'+tile+'-'+bands+'-int-3.fits')
    os.chdir(bands)
    os.mkdir('projected')
    os.mkdir('diffdir')
    os.mkdir('corrdir')
    mt.mImgtbl('raw','rimages.tbl')
    mt.mProjExec('rimages.tbl', '../'+bands+'.hdr', 'projected', 'stats.tbl',
        raw_dir='raw')
    mt.mImgtbl('projected', 'pimages.tbl')
    len_dir = len(os.listdir('projected'))
    if len_dir < 3 :
        mt.mAdd('pimages.tbl', '../'+bands+'.hdr', 
            '../'+sour_name+'_'+bands+'.fits', 
            img_dir='projected')
    else:
        mt.mOverlaps('pimages.tbl', 'diffs.tbl')
        mt.mDiffExec('diffs.tbl',  '../'+bands+'.hdr', 'diffdir', 
            proj_dir = 'projected')
        mt.mFitExec('diffs.tbl', 'fits.tbl', 'diffdir')
        if len(os.listdir('diffdir')) < 1 :
            listPro = os.listdir('projected')
            listPro.sort()
            if os.path.getsize('projected/'+listPro[0])>os.path.getsize('projected/'+listPro[2]):
                shutil.copy('projected/'+listPro[0],
                    '../'+sour_name+'_'+bands+'.fits')
                shutil.copy('projected/'+listPro[1],
                    '../'+sour_name+'_'+bands+'_area.fits')
            else:
                shutil.copy('projected/'+listPro[2],
                    '../'+sour_name+'_'+bands+'.fits')
                shutil.copy('projected/'+listPro[3],
                    '../'+sour_name+'_'+bands+'_area.fits')
        else:
            mt.mBgModel('pimages.tbl', 'fits.tbl', 'corrections.tbl')
            mt.mBgExec('pimages.tbl', 'corrections.tbl', 'corrdir',
                proj_dir = 'projected')
            mt.mAdd('pimages.tbl', '../'+bands+'.hdr', 
                '../'+sour_name+'_'+bands+'.fits', img_dir = 'corrdir')
    os.chdir('..')
    shutil.rmtree(bands)
    os.remove(bands+'.hdr')
    os.remove(sour_name+'_'+bands+'_area.fits')
os.chdir('..')
