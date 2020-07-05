# coding=utf-8
import os    
import cv2
import numpy as np
import shutil
import argparse  	
import subprocess
from PIL import Image	
import flowiz as fz

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, 'frames'))
NOISY_FRAMES = os.path.abspath(os.path.join(CURRENT_DIR, 'noisy_frames'))
VIDEO_FOLDER = os.path.abspath(os.path.join(CURRENT_DIR, 'video'))
TMP_FOLDER = os.path.abspath(os.path.join(CURRENT_DIR, 'tmp'))
RESULTS_FOLDER = os.path.abspath(os.path.join(CURRENT_DIR, 'results'))

#create folder or remove folder's content
def create_folder(folder):
	try:
		if not os.path.exists(folder):
			os.makedirs(folder)
		else:
			shutil.rmtree(folder)    #deletes directory and all its contents
			os.mkdir(folder)
	except:
		pass
	


def get_frames(video):

	video = cv2.VideoCapture('{}{}{}'.format(VIDEO_FOLDER,'/',video))
	#Create folder to save the frames
	create_folder('frames')
	if not video.isOpened():
		print("--Wrong path or video not exist--")
	print('Extracting frames...')
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
			name = './frames/' + str(index) +'_10'+ '.png'
			cv2.imwrite(name, frame)
			flag = False
		else:
			name = './frames/' + str(index) +'_11'+ '.png'
			cv2.imwrite(name, frame)
			index += 1
			flag = True
		
		#Extracts only 40 frames 
		if index >= 40:
			break

	video.release()

def gaussian_noise(noise):
	print('Applying noise...')
	create_folder('noisy_frames')	
	for img in sorted(os.listdir(DATA_DIR)):
		#os.system('export SRAND=$RANDOM; path/to/imgutils-master/awgn {} {}{} {}{}'.format(noise, './frames/',img,'./noisy_frames/',img))
		os.system('export SRAND=$RANDOM; ~/imgutils-master/awgn {} {}{} {}{}'.format(noise, './frames/',img,'./noisy_frames/',img))
		

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
	os.system('python -m flowiz {}{} --outdir {}{}'.format(TMP_FOLDER, '/*.flo', CURRENT_DIR, '/PWC_Netflo_to_pgn/'))    #convert .flo files to .png


def exec_LiteFlowNet(method, images):
	
	with open('{}/10_LiteFlowNet.txt'.format(CURRENT_DIR), 'w') as f:
		for img in images:
			if '_10' == img[6:-4]:
				f.write('{}{} \n'.format('./noisy_frames/', img))

	with open('{}/11_LiteFlowNet.txt'.format(CURRENT_DIR), 'w') as f:
		for img in images:
			if '_11' == img[6:-4]:
				f.write('{}{} \n'.format('./noisy_frames/', img))
	#os.system('.path/to/test_iter 10_LiteFlowNet.txt 11_LiteFlowNet.txt results') 
	os.system('./test_iter 10_LiteFlowNet.txt 11_LiteFlowNet.txt results') #run LiteFlowNet & generate flow. test_iter is the generated binary
	os.system('python -m flowiz {}{} --outdir {}{}'.format(RESULTS_FOLDER, '/*.flo', CURRENT_DIR, '/LFNetflo_to_pgn/'))   #convert .flo files to .png	
	

def video_denoising(method, noise, frames):
	print('Denoising...')
	if method == 'LiteFlowNet':
		
		create_folder('LiteFlowNet_denoised')

		flo_img = [image for image in sorted(os.listdir(RESULTS_FOLDER), key=lambda x: int(x[21:-4]))]
		flag = True
		img = 0
		for frame in frames:
			if flag:
				#os.system('path/to/rbilf -i {}/{} -f 0 -l 13 -s {} -d {}'.format(NOISY_FRAMES,frame, noise, frame))
				os.system('~/rbilf/build/bin/rbilf -i {}/{} -f 0 -l 13 -s {} -d ./LiteFlowNet_denoised/{}'.format(NOISY_FRAMES,frame, noise, frame))
				flag = False
				#img +=1
			else:
				#os.system('path/to/rbilf -i {}/{} -f 0 -l 13 -s {} -d {}'.format(NOISY_FRAMES,frame, noise, frame))
				os.system('~/rbilf/build/bin/rbilf -i {}/{} -o {}/{} -f 0 -l 13 -s {} -d ./LiteFlowNet_denoised/{}'.format(NOISY_FRAMES,frame, RESULTS_FOLDER, flo_img[img], noise, frame))
				flag = True
				img +=1
	else:
		try:
			os.remove(TMP_FOLDER+"/img1.txt")
			os.remove(TMP_FOLDER+"/img2.txt")
			os.remove(TMP_FOLDER+"/deploy.prototxt")
		except:
			print("-----Nothing to remove-----") 

		create_folder('PWC_Net_denoised')
		flo_img = [image for image in sorted(os.listdir(TMP_FOLDER), key=lambda x: int(x[0:6])) if '_backward' in image]   
		flag = True
		img = 0
		for frame in frames:
			if flag:
				#os.system('path/to/rbilf -i {}/{} -f 0 -l 13 -s {} -d {}'.format(NOISY_FRAMES,frame, noise, frame))
				os.system('~/rbilf/build/bin/rbilf -i {}/{} -f 0 -l 13 -s {} -d ./PWC_Net_denoised/{}'.format(NOISY_FRAMES,frame, noise, frame))
				flag = False
				#img +=1
			else:
				#os.system('path/to/rbilf -i {}/{} -f 0 -l 13 -s {} -d {}'.format(NOISY_FRAMES,frame, noise, frame))
				os.system('~/rbilf/build/bin/rbilf -i {}/{} -o {}/{} -f 0 -l 13 -s {} -d ./PWC_Net_denoised/{}'.format(NOISY_FRAMES,frame, TMP_FOLDER, flo_img[img], noise, frame))
				flag = True
				img +=1

def get_difference(method, clean_frames):
	print('Computing difference....')
	noisy_frames = [image for image in sorted(os.listdir(NOISY_FRAMES))]
	if method == 'PWC_Net':

		#Create a folder to save the difference b/w
		create_folder('PWC_Net_difference')
		
		pwc_net_denoised = [image for image in sorted(os.listdir(CURRENT_DIR+'/PWC_Net_denoised/'))]
		
		img = 0
		for clean_frame, noisy_frame in zip(clean_frames, noisy_frames):
			os.system('~/imgutils-master/imdiff {}/{} {}{}{} ./PWC_Net_difference/{} & echo "Noisy: $(~/imgutils-master/psnr {}/{} {}/{} )dB" >> PWC_Net_out.txt "Denoising: $(~/imgutils-master/psnr {}/{} {}{}{})dB" >> PWC_Net_out.txt '.format(DATA_DIR, clean_frame, CURRENT_DIR, '/PWC_Net_denoised/', pwc_net_denoised[img], clean_frame, DATA_DIR, clean_frame, NOISY_FRAMES, noisy_frame, DATA_DIR, clean_frame, CURRENT_DIR, '/PWC_Net_denoised/', pwc_net_denoised[img])  )  #Añadir el out.txt
			img +=1
	else:
		create_folder('LiteFlowNet_difference')
		lft_net_denoised = [image for image in sorted(os.listdir(CURRENT_DIR+'/LiteFlowNet_denoised/'))]
		img = 0
		for clean_frame, noisy_frame in zip(clean_frames, noisy_frames):
			os.system('~/imgutils-master/imdiff {}/{} {}{}{} ./LiteFlowNet_difference/{} & echo "Noisy: $(~/imgutils-master/psnr {}/{} {}/{} )dB" >> LiteFlowNet_out.txt "Denoising: $(~/imgutils-master/psnr {}/{} {}{}{})dB" >> LiteFlowNet_out.txt '.format(DATA_DIR, clean_frame, CURRENT_DIR, '/LiteFlowNet_denoised/', lft_net_denoised[img], clean_frame, DATA_DIR, clean_frame, NOISY_FRAMES, noisy_frame, DATA_DIR, clean_frame, CURRENT_DIR, '/LiteFlowNet_denoised/', lft_net_denoised[img])  )  #Añadir el out.txt
			img +=1



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
	images10_ = [image for image in sorted(os.listdir(NOISY_FRAMES), key=lambda x: int(x[0:-7])) if '_10' in image]
	images11_ = [image for image in sorted(os.listdir(NOISY_FRAMES), key=lambda x: int(x[0:-7])) if '_11' in image]

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
	video_denoising(args.method, args.sigma_noise, list(list_img))

	#Difference b/w two images (normal and the denoised one)
	get_difference(args.method, list(list_img))
