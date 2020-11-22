#Simple script to resize and convert images to .jpg (Intended for mobile pictures)
#Written by Jonathon Teague 11/21/2020
import argparse
import os
from os.path import isfile, join
from os import listdir
from PIL import Image

# Resize and convert all images to .jpg (ignore alpha channel)
def resize_all(inpath, outpath, maxwidth, maxheight):
	if not os.path.isdir(inpath) :
		print("Unable to find input directory: " + inpath)
		return
	if not os.path.isdir(outpath) :
		yesno = input('Begin resizing all images in:\n' + inpath + '\nAnd save to:\n' + outpath + '\nType yes/no:')
		if yesno.lower() != 'yes': return
		os.makedirs(outpath)
	else:
		yesno = input('Begin resizing all images in:\n' + inpath + '\nAnd overwrite images of the same name in:\n' + outpath + '\nType yes/no:')
		if yesno.lower() != 'yes': return
	print("Starting to resize all images..")
	filelist = [inpath + f for f in listdir(inpath) if isfile(join(inpath, f))]
	for i in range (len(filelist)):
		thisfile = filelist[i]
		try:
			image = Image.open(thisfile, "r")
		except:
			print("Unable to read into image: " + filelist[i])
			continue
		image_path = thisfile.split('\\')
		image_name = image_path[len(image_path)-1]
		image_name = "".join(image_name.split('.')[:-1]) + '.jpg'
		out_image = outpath + image_name
		size = image.size
		new_size = size
		while new_size[0] > maxwidth: new_size = tuple((int)(s / 2) for s in new_size)
		while new_size[1] > maxheight: new_size = tuple((int)(s / 2) for s in new_size)
		if size != new_size: image = image.resize(new_size)
		if image.mode in ("RGBA", "P"): image = image.convert("RGB")
		image.save(out_image)
	print("Job's done!")

# Example invocation: imageresizer.py -input path\to\input\  -output path\to\output\
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-input", "--infile", help="Input directory to read images from")
	parser.add_argument("-output", "--outfile", help= "Output file to write resized images to")
	args = parser.parse_args()
	inpath = args.infile
	outpath = args.outfile
	resize_all(inpath, outpath, 1200, 1200)