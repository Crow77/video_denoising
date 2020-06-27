# coding=utf-8
import os    
import cv2
import numpy as np
import shutil
import argparse  	
import subprocess
from PIL import Image	

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, 'frames'))
NOISY_FRAMES = os.path.abspath(os.path.join(CURRENT_DIR, 'noisy_frames'))
VIDEO_FOLDER = os.path.abspath(os.path.join(CURRENT_DIR, 'video'))

def get_frames(video):

	video = cv2.VideoCapture('{}{}{}'.format(VIDEO_FOLDER,'/',video))

	if not os.path.exists('frames'):
		os.makedirs('frames')
	else:
		shutil.rmtree('frames')
    	os.mkdir('frames')
	
	if not video.isOpened():
		print("--Wrong path or video not exist--")
	#for frame identity
	index = 0
	flag = True

	while(video.isOpened()):   
		# Extract images
		ret, frame = video.read()     
		# end of frames
		if not ret: 
			break
		# Saves images
		if flag:
			name = './frames/10_' + str(index) + '.png'
			print ('Creating...' + name)
			cv2.imwrite(name, frame)
			flag = False
		else:
			name = './frames/11_' + str(index) + '.png'
			print ('Creating...' + name)
			cv2.imwrite(name, frame)
			index += 1
			flag = True
		
		#Extract only 40 frames from video
		if index >= 40:
			break

		# next frame
		#index += 1

	video.release()

def gaussian_noise(noise):
	
	if not os.path.exists('noisy_frames'):
		os.makedirs('noisy_frames')
	else:
		shutil.rmtree('noisy_frames')
		os.mkdir('noisy_frames')
		
	#total_img = 1
	for img in sorted(os.listdir(DATA_DIR)):
		
		#os.system('export SRAND=$RANDOM; path/to/imgutils-master/awgn {} {}{} {}{}'.format(noise, './frames/',img,'./noisy_frames/',img))
		os.system('export SRAND=$RANDOM; ~/imgutils-master/awgn {} {}{} {}{}'.format(noise, './frames/',img,'./noisy_frames/',img))
		#break

def exec_PWC_Net(method, images):

	flag = True

	with open('{}/10_PWC_Net.txt'.format(CURRENT_DIR), 'w') as f:  
		for img in images:
			f.write('{}{} \n'.format('./noisy_frames/', img))

	with open('{}/11_PWC_Net.txt'.format(CURRENT_DIR), 'w') as f:
		for img in reversed(images):
			f.write('{}{} \n'.format('./noisy_frames/', img))

	with open('{}/out.txt'.format(CURRENT_DIR), 'w') as f:
		for img in images:
			if flag:
				f.write('{}{}{}\n'.format('./tmp/',img[:-4],'_forward.flo'))
				flag = False
			else:
				f.write('{}{}{}\n '.format('./tmp/',img[:-4],'_backward.flo'))
				flag = True
	#os.system('.path/to/proc_images 10_PWC_Net.txt 11_PWC_Net.txt out.txt') 
	os.system('./proc_images 10_PWC_Net.txt 11_PWC_Net.txt out.txt') #run PWC_Net & generate flow. proc_images is the generated binary

def video_denoising():
	pass

def exec_LiteFlowNet(method, images):

	with open('{}/10_LiteFlowNet.txt'.format(CURRENT_DIR), 'w') as f:
		for img in images:
			if '10_' == img[0:3]:
				f.write('{}{} \n'.format('./noisy_frames/', img))

	with open('{}/11_LiteFlowNet.txt'.format(CURRENT_DIR), 'w') as f:
		for img in images:
			if '11_' == img[0:3]:
				f.write('{}{} \n'.format('./noisy_frames/', img))
	#os.system('.path/to/test_iter 10_LiteFlowNet.txt 11_LiteFlowNet.txt results') 
	os.system('./test_iter 10_LiteFlowNet.txt 11_LiteFlowNet.txt results') #run LiteFlowNet & generate flow. test_iter is the generated binary	
	



if __name__ == '__main__':
	#Initialize the parser
	parser = argparse.ArgumentParser(
		description ="Online Demo for video denoising using optical flow"
	)

	#positional/optional parameter
	parser.add_argument('method', help="Method to be executed: PWC_Net/LiteFlowNet")  
	parser.add_argument('total_img', help="Amount of images (int)", type = int)
	parser.add_argument('sigma_noise', help="Provide noise (int)", type = int)
	parser.add_argument('video', help="Provide a valid video")

	#Parse the arguments
	args = parser.parse_args()

	#Get frames
	get_frames(args.video)

	#Apply sigma noise
	gaussian_noise(args.sigma_noise)

	#Get images clasified by tag
	images10_ = [image for image in sorted(os.listdir(NOISY_FRAMES), key=lambda x: int(x[3:-4])) if '10_' in image]
	images11_ = [image for image in sorted(os.listdir(NOISY_FRAMES), key=lambda x: int(x[3:-4])) if '11_' in image]

	list_img = []
	count = 1
	#Creating a list with the amount of images passed by parameter 
	for x,y in zip(images10_, images11_):
		if count <= int(args.total_img):
			list_img.append(x)
			list_img.append(y)
			count += 1

	#Run the optical flow method requested
	if args.method == 'PWC_Net':
		exec_PWC_Net(args.method, list(list_img))
	elif args.method == 'LiteFlowNet':
		exec_LiteFlowNet(args.method, list(list_img))
	else:
		print("Provide a valid method")
	

	#Apply denoising
	#video_denoising()
