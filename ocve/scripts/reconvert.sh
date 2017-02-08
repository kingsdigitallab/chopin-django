#!/bin/bash
#Fix some problem images by putting them on a white canvas
#EH 8/2/2017 (Based on Geoffroy's instructions)

#Args: inputfile outputfile new_width new_height
inputfile=$1
outputfile=$2
new_width=$3
new_height=$4

# convert original to plain BMP
convert ${inputfile} convert.bmp
# extended canvas
convert convert.bmp -gravity NorthWest -background white -extent ${new_width}x${new_height} xt.bmp
#Convert to jp2
kdu_compress -i xt.bmp -o ${outputfile} -rate -,4,2.34,1.36,0.797,0.466,0.272,0.159,0.0929,0.0543,0.0317,0.0185 Creversible=yes Clevels=5 Stiles={1024,1024} Cblk={64,64} Corder=RPCL
rm xt.bmp
rm convert.bmp