# coding=utf-8
import os    
import cv2
import numpy as np
import argparse  		

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, 'frames'))

def video_denoising():
	pass

def exec_PWC_Net(method, images):

	flag = True

	with open('{}/10_PWC_Net.txt'.format(CURRENT_DIR), 'w') as f:  
		for img in images:
			f.write('{}{} \n'.format('./frames/', img))

	with open('{}/11_PWC_Net.txt'.format(CURRENT_DIR), 'w') as f:
		for img in reversed(images):
			f.write('{}{} \n'.format('./frames/', img))

	with open('{}/out.txt'.format(CURRENT_DIR), 'w') as f:
		for img in images:
			if flag:
				f.write('{}{}{}\n'.format('./tmp/',img[:-4],'_forward.flo'))
				flag = False
			else:
				f.write('{}{}{}\n '.format('./tmp/',img[:-4],'_backward.flo'))
				flag = True

	os.system('./proc_images 10_PWC_Net.txt 11_PWC_Net.txt out.txt') #run PWC_Net & generate flow. proc_images is the generated binary



def exec_LiteFlowNet(method, images):

	with open('{}/10_LiteFlowNet.txt'.format(CURRENT_DIR), 'w') as f:
		for img in images:
			if '10_' == img[0:3]:
				f.write('{}{} \n'.format('./frames/', img))

	with open('{}/11_LiteFlowNet.txt'.format(CURRENT_DIR), 'w') as f:
		for img in images:
			if '11_' == img[0:3]:
				f.write('{}{} \n'.format('./frames/', img))
	
	os.system('./test_iter 10_LiteFlowNet.txt 11_LiteFlowNet.txt results') #run LiteFlowNet & generate flow. test_iter is the generated binary	
	



if __name__ == '__main__':
	#Initialize the parser
	parser = argparse.ArgumentParser(
		description ="Online Demo for video denoising using optical flow"
	)

	#positional/optional parameter
	parser.add_argument('method', help="Method to be executed: PWC_Net/LiteFlowNet")  
	parser.add_argument('total_img', help="Amount of images (int)", type = int)

	#Parse the arguments
	args = parser.parse_args()

	#Get images clasified by tag
	images10_ = [image for image in sorted(os.listdir(DATA_DIR)) if '10_' in image]
	images11_ = [image for image in sorted(os.listdir(DATA_DIR)) if '11_' in image]
	

	list_img = []
	count = 1
	#Creating a list with the amount of images passed by parameter 
	for x,y in zip(images10_, images11_):
		if count <= int(args.total_img):
			list_img.append(x)
			list_img.append(y)
			count += 1
		
	if args.method == 'PWC_Net':
		exec_PWC_Net(args.method, list(list_img))
	elif args.method == 'LiteFlowNet':
		exec_LiteFlowNet(args.method, list(list_img))
	else:
		print("Provide a valid method")
	
