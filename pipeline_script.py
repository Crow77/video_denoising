#!/usr/bin/env python
# coding=utf-8
import os    
import cv2
import numpy as np
import shutil
import argparse  	
from os import walk
import sys
import subprocess

#create folder or remove folder's content
def create_folder(folder):
	try:
		if not os.path.exists(folder):
			os.makedirs(folder)
		else:
			shutil.rmtree(folder)
			os.mkdir(folder)
	except:
		pass

#Get only number of frames selected by user
def normalize_frames(nframes):
		
	frames = [image for image in sorted(os.listdir('input_0'), key=lambda x: int(x[6:-4])) if int(image[6:-4]) >= nframes]
	for frame in frames:
		try:
			os.remove('input_0/{}'.format(frame))
		except:
			pass

def get_opticalFlow_files(folder):
	flo_img = [image for image in sorted(os.listdir(folder), key=lambda x: int(x[6:-13])) if '_backward' in image]  
	return flo_img


def get_frames(folder):
	frames = [image for image in sorted(os.listdir(folder), key=lambda x: int(x[6:-4]))]
	return frames


def png_to_mp4():
	os.system('ffmpeg -framerate 25 -i "Denoised/frame_%5d.png" "output.mp4"; ffmpeg -framerate 25 -i "input_0/frame_%5d.png" "input_0_frames.mp4"; ffmpeg -framerate 25 -i "noisy_frames/frame_%5d.png" "noisy_video.mp4"; ffmpeg -framerate 25 -i "Difference/frame_%5d.png" "video_difference.mp4"; ffmpeg -framerate 25 -i "flow_to_png/frame_%5d.png" "opticalflow.mp4"')


def gaussian_noise(noise):
	print('Applying noise...')
	create_folder('noisy_frames')
	for img in sorted(os.listdir('input_0')):
		os.system('export SRAND=$RANDOM; awgn {} {}{} {}{}'.format(noise, 'input_0/',img,'noisy_frames/',img))
		

def compute_opticalFlow(method, images):
	create_folder('optic_flow')
	index = 0
	for previous, current in zip(images, images[1:]):
		
		if method in ['RDPOF', 'BROX_SPATIAL']:
			compute(previous, current, index, 'main')
			index +=1
			
		elif method == 'TV_L1':
			compute(previous, current, index, 'tvl1flow')
			index +=1
		elif method == 'OF_DIS':
			compute(previous, current, index, 'run_OF_INT')
			index +=1
		elif method == 'FALDOI': 
			compute(previous, current, index, 'sparse_flow')
			index +=1
		else:
			print('Provide a valid Optical flow Method')

def compute(previous, current, index, run):
	frame = cv2.imread('noisy_frames/'+current)
	if run == 'sparse_flow':
		with open ('faldoi{}.txt'.format(index), 'w') as f:
			f.write('noisy_frames/{}\nnoisy_frames/{} '.format(current, previous))

		width,height,layers = frame.shape
		os.system('{} {} {} {} {}/frame_{:05d}_backward.flo'.format(run, 'faldoi{index}.txt', width, height, 'optic_flow' , index))
	else:
		os.system('{} {}/{} {}/{} {}/frame_{:05d}_backward.flo'.format(run, 'noisy_frames', current, 'noisy_frames', previous,'optic_flow' , index))
		

def opticalflow_to_png():
	create_folder('flow_to_png')
	flo_img = get_opticalFlow_files('optic_flow')
	index = 0
	for image in flo_img:
		os.system('viewflow 0 optic_flow/{} flow_to_png/frame_{:05d}.png '.format(image, index))
		index +=1


#Apply Recursive Bilateral Filter denoising
def rbilf_denoising(method, noise, frames, numframes):
	print('Denoising...')
	create_folder('Denoised')
	flo_img = get_opticalFlow_files('optic_flow')
	flag = True
	img = 0
	for frame in frames:
		if flag:
			os.system('rbilf -i {}/{} -f 0 -l {} -s {} -d Denoised/{}'.format('noisy_frames',frame, numframes-1, noise, frame))
			flag = False		
		else:
			os.system('rbilf -i {}/{} -o {}/{} -f 0 -l {} -s {} -d Denoised/{}'.format('noisy_frames',frame, 'optic_flow', flo_img[img], numframes-1, noise, frame))
			img +=1
			

#Apply Non-Local Kalman denoising
def non_local_denoising(method, noise, frames, numframes):
	print('Denoising...')
	create_folder('Denoised')
	flo_img = get_opticalFlow_files('optic_flow')
	flag = True
	img = 0
	for frame in frames:
		if flag:
			os.system('nlkalman-flt -i {}/{} -s {} --flt11="Denoised/{}"'.format('noisy_frames',frame, noise, frame)) 
			flag = False					
		else:				
			os.system('nlkalman-flt -i {}/{} -o {}/{} -s {} --flt11="Denoised/{}"'.format('noisy_frames',frame, 'optic_flow', flo_img[img], noise, frame)) 
			img +=1

		
def compute_difference():
	print('Computing difference....')
	clean_frames = get_frames('input_0')
	
	#Create a folder to save the difference b/w
	create_folder('Difference')	
	img_denoised = get_frames('Denoised')	
	img = 0
	for clean_frame in clean_frames:
		os.system('imdiff {}/{} {}/{} Difference/{} & echo "{}: $(psnr {}/{} {}{})dB" >> Difference.txt '.format('input_0', clean_frame, 'Denoised', img_denoised[img], clean_frame, clean_frame, 'input_0', clean_frame, 'Denoised/', img_denoised[img])  )  
		img +=1

	value = 0
	nframes = 0
	with open ('Difference.txt', 'r') as f:
		for line in f:
			value += float(line[17:-3])
			nframes += 1
			
	with open ('Difference.txt', 'a') as f:
		f.write('\n\nAverage: {} '.format(value/float(nframes)))
		
	

if __name__ == '__main__':
	#Initialize the parser
	parser = argparse.ArgumentParser(
		description ="Online Demo for video denoising using optical flow"
	)

	#positional/optional parameter
	parser.add_argument('select_method', help="Optical Flow Method to be executed: TV-L1/RDPOF")  
	parser.add_argument('select_denoising', help="Denoisng Method to be executed: Non-Local-Kalman/Recursive-Bilateral-Filter")  
	parser.add_argument('frameslfn', help="Amount of frames (int)", type = int)
	parser.add_argument('sigmalfn', help="Provide noise (int)", type = int)

	#Parse the arguments
	args = parser.parse_args()

	#Use only number of frames selected by user
	normalize_frames(args.frameslfn)

	#Apply sigma noise
	gaussian_noise(args.sigmalfn)

	#get noisy frames clasified and sorted
	list_imgs = get_frames('noisy_frames')
	
	#Run the optical flow method requested
	compute_opticalFlow(args.select_method, list(list_imgs))
	
	opticalflow_to_png()

	#Run the denoising method selected
	if args.select_denoising == 'Recursive_Bilateral_Filter': 
		rbilf_denoising(args.select_method, args.sigmalfn, list(list_imgs), args.frameslfn)
	else:
		non_local_denoising(args.select_method, args.sigmalfn, list(list_imgs), args.frameslfn)


	#Difference b/w two images (normal and the denoised one)
	compute_difference()

	png_to_mp4()
	
