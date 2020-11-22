#Simple script to compare images to find duplicates (even with resizing)
#Caveat: Images with many white pixels/transparency may be misclassified
#Written by Jonathon Teague 11/21/2020
import argparse
import os
from os.path import isfile, join
from os import listdir
from PIL import Image

# Algorithm to find similar images even if diff resolution
# A. Hash a list of all images based on their width / height
# B. Resize all images to min size within resolution for list
# C. Break image into x number of sections and calculate delta between RGB for both images based on sampling
def compare_all_images(path, significance, tolerance):
	print('Begin comparing all images in ' + path)
	filelist = [path + f for f in listdir(path) if isfile(join(path, f))]
	res_map = {}
	size_tuple_map = {}
	dupeset = []
	dupes = 0
	#A. Hash based on resolution
	for i in range (len(filelist)):
		thisfile = filelist[i]
		try:
			image = Image.open(thisfile, "r")
		except:
			print("Unable to read into image: " + filelist[i])
			filelist[i] = ""
			continue
		size = image.size
		# Dupe image resolution might differ slightly when shrunk
		res = round(size[0] / size[1], 3)
		if res in res_map: l = res_map[res]
		else: l = []
		l.append(thisfile)
		res_map[res] = l
		if res in size_tuple_map:
			if size_tuple_map[res][0] > size[0]:
				size_tuple_map[res] = size
		else: 
			size_tuple_map[res] = size
	for k in res_map.keys():
		flist = res_map[k]
		min_size = size_tuple_map[k]
		imgs = []
		#B. Resize to min res
		for f in flist:
			img = Image.open(f, "r")
			s = img.size
			if s > min_size:
				img = img.resize(min_size)
			# To avoid exceptions when comparing .jpg with .png
			if img.mode in ("RGBA", "P"): img = img.convert("RGB")
			imgs.append(img)
		for i in range(len(flist)):
			thisimg = imgs[i]
			comp_imgs = imgs[i+1:]
			for k in range(len(comp_imgs)):
				p = compare_one_image(thisimg, comp_imgs[k], min_size[0], min_size[1], tolerance)
				if p > significance:
					f1 = flist[i]
					f2 = flist[i+k+1]
					print(str(p) + '% similar: ' + f1 + ' and ' + f2)
					if f1 in dupeset:
						if f2 in dupeset: continue
						dupeset.append(f2)
					else:
						dupeset.append(f1)
						if f2 not in dupeset: dupeset.append(f2)
					dupes +=1
	print('Found {0} possible duplicate images.'.format(dupes))
	
#C. Check num_chk pixels for similarity between both images
def compare_one_image(img1, img2, width, height, tolerance): 
	data1 = img1.getdata()
	data2 = img2.getdata()
	size = width * height
	num_chk = min(size, 5000)
	offset = (int)(size / num_chk)
	failures = 0
	for i in range(num_chk):
		if compare_one_pixel(data1[offset * i], data2[offset * i], tolerance):
			failures += 1
	return round(failures / num_chk * 100, 2)
	
#Check RGB comparison within tolerance
def compare_one_pixel(pix1, pix2, tolerance):
	similar = ( abs(pix1[0] - pix2[0]) <= tolerance
	and abs(pix1[1] - pix2[1]) <= tolerance
	and abs(pix1[2] - pix2[2]) <= tolerance)
	return similar
	
# Example invocation: imagecomparer.py -fp path\to\images\
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-fp", "--filepath", help="Path to directory containing images")
	parser.add_argument("-sig", "--significance", type=float, default=80, help="Level of significance 1-100 where images are considered similar")
	parser.add_argument("-tol", "--tolerance", type=int, default=25, help="Tolerance 0-255 for pixel comparison")
	args = parser.parse_args()
	path = args.filepath
	significance = args.significance
	tolerance = args.tolerance
	compare_all_images(path, significance, tolerance)