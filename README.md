# Making WISE Cutout/Mosaic Using Montage Wapper

The main script for cutting/mosaicing images is **WISE_cutout.py**. 

Runing this script needs a local pool of ALLWISE tiles which can be downloaded using the four ***bash*** scripts (this maybe very time consuming for building a local data pool). 

Please edit the WISE_cutout.py file before using it 
on your own computer.

1. Go to line 38, and replace the path to the directory 
   of allwiseTiles with the real absolute path.

2. Go to line 39, and replace the path to the 
   ALLWISE_altalsMeta.tbl with the real absolute path.

3. Copy the WISE_cutout.py to your working directory.


This script can be used for making small cutouts and large mosaics. A mosaic of 2.5 degree X 2.5 degree for the Andromeda Galaxy is shown bellow as an example.

![M31](M31_wiseRGB_small.jpg)


