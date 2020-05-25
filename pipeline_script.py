# coding=utf-8
import os    
import cv2
import numpy as np
import argparse  		

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, 'frames'))

def exec_PWC_Net(metodo, img1, img2):
	

	with open('{}/img1_PWC_Net.txt'.format(CURRENT_DIR), 'w') as f:
		f.write('{}{} \n'.format('./frames/', img1))
		f.write('{}{} '.format('./frames/', img2))

	with open('{}/img2_PWC_Net.txt'.format(CURRENT_DIR), 'w') as f:
		f.write('{}{} \n'.format('./frames/', img2))
		f.write('{}{} '.format('./frames/', img1))

	with open('{}/out.txt'.format(CURRENT_DIR), 'w') as f:
		f.write('{}{}{}\n'.format('./tmp/',img1[:-4],'_forward.flo'))
		f.write('{}{}{} '.format('./tmp/',img2[:-4],'_backward.flo'))

	os.system('./proc_images img1_PWC_Net.txt img2_PWC_Net.txt out.txt') #Ejecuta PWC_Net y genera flujo óptico



def exec_LiteFlowNet(metodo, img1, img2):


	with open('{}/img1_LiteFlowNet.txt'.format(CURRENT_DIR), 'w') as f:
		f.write('{}{} \n'.format('./frames/', img1))

	with open('{}/img2_LiteFlowNet.txt'.format(CURRENT_DIR), 'w') as f:
		f.write('{}{} \n'.format('./frames/', img2))
	
	os.system('./test_iter img1_LiteFlowNet.txt img2_LiteFlowNet.txt results') #Ejecuta LiteFlowNet y genera flujo óptico	
	



if __name__ == '__main__':
	#Inicializar el parser
	parser = argparse.ArgumentParser(
		description ="Demo en linea para video denoising usando flujo óptico"
	)

	#Parámetros posicional/opcional
	parser.add_argument('metodo', help="Mátodo a ejecutar: PWC_Net/LiteFlowNet")  
	parser.add_argument('img1', help="Proporcione imagen1")
	parser.add_argument('img2', help="Proporcione imagen2")


	#Parsear los argumentos
	args = parser.parse_args()
	
	
	if args.metodo == 'PWC_Net':
		exec_PWC_Net(args.metodo, args.img1, args.img2)
	elif args.metodo == 'LiteFlowNet':
		exec_LiteFlowNet(args.metodo, args.img1, args.img2)
	else:
		print("Proporcione un método válido")
	
