# coding=utf-8

import os    
import cv2
import numpy as np
import argparse 
import shutil


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, 'videos'))

def extract_videoFrames(video):
	# Video path
	video = cv2.VideoCapture(os.path.join(DATA_DIR, video))
	
	if not os.path.exists('frames'):
	    os.makedirs('frames')
	else:
	    shutil.rmtree('frames')
	    os.mkdir('frames')


	if not video.isOpened():
	    print("--Wrong path or video not exist--")

	#for frame identity
	index = 0

	while(video.isOpened()):   
	    # Extraer frames
	    ret, frame = video.read()     
	    # Final de frames
	    if not ret: 
		break
	    # Guardar frames
	    else:
		name = './frames/frame_' + str(index) + '.jpg'
		print ('Creating...' + name)
		cv2.imwrite(name, frame)

	    # Siguiente frame
	    index += 1

	video.release()



if __name__=="__main__":

	#Inicializar el parser
	parser = argparse.ArgumentParser(
		description ="Descomponer video en frames"
	)

	#Parámetros posicional/opcional
	parser.add_argument('video', help="Proporcione un video")  


	#Parsear los argumentos
	args = parser.parse_args()
    	extract_videoFrames(args.video)
    
