
print("\n\n[<]Iniciada programacion por vision artificial[>]\n\n")
print("[#]Iniciado proceso de configuracion previa")


###### ### ##  IMPORTACION DE DEPENDENCIAS  ## ### ######



print("    [*]Importando dependencias...")

#Para uso general
import time #Para contar tiempo (time()) y hacer pausas (sleep())

#Para el tracking
import numpy as np
import cv2

#Para escribir por MODBUS TCP
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

#Para saber si un archivo existe
import os.path

#Para leer del HC-SR04
import RPi.GPIO as GPIO






###### ### ##  C O N S T A N T E S   D E   C O N F I G U R A C I O N  ## ### ######



print("    [*]Realizando configuraciones generales...")

#Comunicaciones
HOST = "192.168.1.147" #IP del robot
PORT_MODBUS= 502 #Puerto donde el robot tiene el servidor (esclavo) Modbus

#Constantes para el sensor
CORRECCION_SENSOR = -0.006 #Distancia entre el sensor y la camara en Z en metros (para corregir la lectura)
DISTANCIA_CAMARA_PAPEL = 0.2715 #Distancia camara-superficie

#Longitud del filtro de media movil -> A mas longitud -> Mas precision y menos velocidad
LONG_FILTRO = 4 

#Umbrales de area para considerar valida una deteccion de caracteristica
AREA_LOW = 500 #Estaba a 200
AREA_TOP = 6500 #Estaba a 15000

#Zona donde se considera que la camara esta sobre el centro (Valor de menos a mas estricto: 10-30)
ZONA_TOLERANCIA = 14






###### ### ##  F U N C I O N E S   A U X I L I A R E S  ## ### ######



#Funcion para hacer la media movil (recibe los historiales de posiciones del identificador)
def media_movil(historial_cx, historial_cy):
	sumax = 0
	sumay = 0
	contador = 0
	
	#Recorrer los historiales de valores y  sumar los elementos
	while contador < LONG_FILTRO:
		sumax += historial_cx[contador]
		sumay += historial_cy[contador]

		contador += 1
	
	return sumax/LONG_FILTRO, sumay/LONG_FILTRO #Devolver la media



#Funcion para clasificar formas (recibe un contorno)
def detectarTriangulo(c):
	#Aproximar el contorno con lineas rectas 
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.04 * peri, True)

	#Si la aproximacion se ha resuelto con tres puntos (vertices)
	if len(approx) == 3:
		return True #Confirmar que la forma es un triangulo
	else:
		return False
		
		
		
#Funcion para medir distancia con el HC-SR04 (asume que Trig y Echo se han inicializado antes de la llamada con los pines donde este conectado el sensor)
def medirDistancia():
	GPIO.output(Trig, False) #Apagar el pin Trig (disparador)
	time.sleep(2*10**-6) #esperar 2 us
	GPIO.output(Trig, True) #Encender Trig 
	time.sleep(10*10**-6) #esperamos 10 us
	GPIO.output(Trig, False) #Apagar Trig
 
	#Empezar a contar el tiempo cuando el pin Echo se encienda
	while GPIO.input(Echo) == 0:
		start = time.time()
 
	while GPIO.input(Echo) == 1:
		end = time.time()
 
	#Calcular tiempo transcurrido entre inicio y fin (en segundos) 
	duracion = end-start

	#Pasar tiempo a microsegundos
	duracion = duracion*10**6
	medida = duracion/58 #Calcular distancia en cm
	medida = medida/100 #Pasar medida a metros

	return medida #Devolver distancia recibida






###### ### ##  O T R A S   I N I C I A L I Z A C I O N E S  ## ### ######



#Inicializar camara
print("    [*]Accediendo a la camara...")
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

if(ret == False):
	print("    [!]ERROR! Ha sido imposible acceder a la camara")
	
	
#Inicializaciones para el sensor
print("    [*]Preparando modulo HC-SR04...")
GPIO.setwarnings(False) #Ignorar posibles fallos en otros programas que no limpiasen los puertos
GPIO.setmode(GPIO.BOARD) #Usar la numeracion de la placa
#Definir los pines donde se conectaran Trigger y Echo
Trig = 11
Echo = 13
#Configurar ambos pines 
GPIO.setup(Trig, GPIO.OUT)
GPIO.setup(Echo, GPIO.IN)


#Inicializar comunicaciones
print("    [*]Configurando comunicaciones...")
client = ModbusClient(HOST, PORT_MODBUS) #Abrir puerto de comunicacion con el robot (para enviar valores por MODBUS)
comunicacion_OK = True

if(client.connect() == False):
	print("    [!]ERROR! Ha sido imposible conectarse al servidor Modbus")
	comunicacion_OK = False
	ret = False


#Abrir archivo de escritura
print("    [*]Abriendo archivo para almacenar los movimientos...")
respuesta = "s"
if(os.path.isfile("./correcciones.txt")): #Si ya existe el archivo en el directorio desde el que se ejecuta el programa
	while(1):
		respuesta = raw_input("    [!]ALERTA! Existe un 'correcciones.txt' en el directorio actual. Desea continuar (y sobreescribirlo)? (s/n): ") #Pedir autorizacion para seguir (y sobreescribirlo)
		
		if(respuesta == "n"): #Si NO se quiere
			ret = False #Acabar programa
			break
		elif(respuesta == "s"): #Si SI se quiere
			archivo = open("correcciones.txt", "w") #Abrir archivo
			break
		else: #Si se introduce una respuesta no valida
			print("    [!]ERROR! No se ha introducido una respuesta valida. Introduzca 's' para seguir adelante o 'n' para abortar la ejecucion")
else:
	archivo = open("correcciones.txt", "w")
		
		
#Variables para el procesado de imagen
print("    [*]Preparando el procesado de imagen...")
err_areaNoDetectada = False
#Rango de color a coger
verde_min = (40, 30, 40)
verde_max = (60, 215, 215)
#Leer tamano de la imagen
w = cap.get(3)
h = cap.get(4)
#Inicializar variables del centro, area y contorno (para evitar inicializaciones y destrucciones en bucle)
cx = w/2
cy = h/2
area = 0.0
area_max = 0.0
it = 0


#Inicializaciones para el control (variables y ajuste de distancia camara-superficie)
print("    [*]Adaptando el algoritmo al entorno...")
#Variables para el control
correccionX = 0
correccionY = 0
cambioX = False
cambioY = False
historial_x = []
historial_y = []
#Actualizar las correcciones maximas que se haran
contador = 0

#Medir LONG_FILTRO*2 veces la distancia y hacer la media
while(contador<LONG_FILTRO*2):
	DISTANCIA_CAMARA_PAPEL += medirDistancia() #Tomar medida del sensor
	contador += 1
DISTANCIA_CAMARA_PAPEL = DISTANCIA_CAMARA_PAPEL/LONG_FILTRO + CORRECCION_SENSOR #Calcular media de medidas y restar 5 cm para conseguir variaciones mas pequenyas
#Actualizar desplazamientos partiendo de la altura de la camara
DESPLAZAMIENTO_MAX_X = 0.6032385667*DISTANCIA_CAMARA_PAPEL
DESPLAZAMIENTO_MAX_Y = 0.4507693885*DISTANCIA_CAMARA_PAPEL



#Si NO se ha indicado ningun error
if(ret == True):
	#Informar del inicio del proceso principal
	print("\n[#]Todo listo! Iniciado bucle de control principal")
	print("    [!]AVISO: Recuerde iniciar la ejecucion del programa del robot")
	raw_input("    [*]Pulse 'Enter' para continuar...")
	print("\n")






###### ###### ### ## #   ###### ### ##  #  ## ### ######   # ## ### ######

###### ### ##  I N I C I O   D E   B U C L E   P R I N C I P A L  ## ### ######

###### ###### ### ## #   ###### ### ##  #  ## ### ######   # ## ### ######



#Bucle hasta que se pulse "Ctrl+C" o hasta que haya algun fallo capturando un frame
while(ret):
	try:		
		#Capturar nuevo frame de la camara
		ret, frame = cap.read()

		#Si hay error -> SALIR
		if (ret == False):
			print ("    [!]ERROR! No se ha podido caputar una nueva imagen")
			break
		





###### ### ##  P R O C E S A D O   D E   L A   I M A G E N  ## ### ######



		#Convertir a HSV
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		
		#Umbralizar para obtener imagen binaria
		binaria = cv2.inRange(hsv, verde_min, verde_max) #Detectar colores verdes

		#Encuadrar con un rectangulo y mostrar
		cnt, hie = cv2.findContours(binaria, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		#Buscar area verde mas grande
		area_max = 0.0

		for item in cnt:
			area = cv2.contourArea(item)
			if area > area_max: #Si el area es mayor que la mas grande actual
				if detectarTriangulo(item): #Si es un triangulo
					#Almacenar area y contorno actuales
					area_max = area
					it = item

		#Si se ha detectado algun area valida (Se ha sobreescrito el valor "0.0") -> Dibujar bounding box y centroide
		if area_max < AREA_TOP and area_max > AREA_LOW:
			M = cv2.moments(it)
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])
		else:
			if err_areaNoDetectada == False: #Imprimir la alerta solo si en la iteracion anterior se ha encontrado area
				print("    [!]ALERTA! La camara NO visualiza un triangulo verde valido")
				print("        [*]Intentando relocalizar el identificador...")
				err_areaNoDetectada = True #Indicar que se ha mostrado el error de area no detectada
			continue #Si no es un area valida -> Pasar a siguiente iteracion (para no perder tiempo, la PRIORIDAD es encontrar el identificador)

		if err_areaNoDetectada == True: #Imprimir la notificacion solo si en la iteracion anterior NO se ha encontrado area
			print("        [*]Identificador localizado -> Programa funcionando...")
			err_areaNoDetectada = False #Indicar que se ha encontrado un area






###### ### ##  C A L C U L O   D E   C O R R E C C I O N E S  ## ### ######



		#Almacenar resultado en historiales
		historial_x.append(cx)
		historial_y.append(cy)

		#Volver a buscar punto si aun no hay suficientes elementos en el historial_x (en el "y" sera igual) (longitud+1 porque se acaba de anadir otro)
		if historial_x.__len__() < LONG_FILTRO:
			print("    [*]Tomando medida " + str(historial_x.__len__()) + " de " + str(LONG_FILTRO) + " para el filtro...")
			continue
		elif historial_x.__len__() == LONG_FILTRO:
			print("    [*]Tomando medida " + str(historial_x.__len__()) + " de " + str(LONG_FILTRO) + " para el filtro...")
			print("    [#]Filtro preparado -> Programa funcionando")
		else:
			#Eliminar el primer elemento de ambos historiales
			del historial_x[0]
			del historial_y[0]

			#Si si los hay, hacer la media y seguir
			cx, cy = media_movil(historial_x, historial_y)

		#Correcciones de X e Y
		if (cx<((w/2)-(w/ZONA_TOLERANCIA))) or (cx>((w/2)+(w/ZONA_TOLERANCIA))): #Corregir X solo si esta alejado del centro en X mas de una veinteava parte del ancho total (640/20 = 32 pixeles)
			correccionX = -((cx-(w/2))/(w/2))*DESPLAZAMIENTO_MAX_X
		else:
			correccionX = 0
			
		if (cy<((h/2)-(h/ZONA_TOLERANCIA))) or (cy>((h/2)+(h/ZONA_TOLERANCIA))): #Corregir Y solo si esta alejado del centro en Y mas de una veinteava parte del ancho total (480/20 = 24 pixeles)
			correccionY = -((cy-(h/2))/(h/2))*DESPLAZAMIENTO_MAX_Y
		else:
			correccionY = 0






###### ### ##  E S C R I T U R A   D E   R E G I S T R O S   P O R   M O D B U S  ## ### ######



		#Indicar signo de X en el registro 130
		if correccionX > 0:
			client.write_register(130, 1)
		else:
			client.write_register(130, 0)
			
		#Escribir la correccion de X en el registro 128
		client.write_register(128, abs(correccionX*1000/2))

		#Indicar signo de Y en el registro 131
		if correccionY > 0:
			client.write_register(131, 1)
		else:
			client.write_register(131, 0)
		#Escribir la correccion de Y en el registro 129
		client.write_register(129, abs(correccionY*1000/2))






###### ### ##  E S C R I T U R A   D E   A R C H I V O  ## ### ######


 
		archivo.write(str(correccionX) + " " + str(correccionY) + "\n")
		
		
	#Si se pulsa "Ctrl+C" -> SALIR
	except KeyboardInterrupt:
		print("s\n[!]ALERTA! Se ha puslado 'Ctrl+C' -> Finalizando programa...")
		break






###### ### ##  F I N A L I Z A C I O N   D E L   P R O G R A M A  ## ### ######



print("\n[#]Iniciado proceso de finalizacion del programa")

#Liberar camara (cerrar archivo de captura) y liberar memoria
print("    [*]Liberando camara...")
cap.release()

#Cerrar sockets
if(comunicacion_OK == True):
	print("    [*]Cerrando comunicaciones...")
	time.sleep(0.01) #esperar 10ms
	client.write_register(128, 0) #Anular correccion en X
	time.sleep(0.01) #esperar 10ms
	client.write_register(129, 0) #Anular correccion en Y
	client.close() #Cerrar comunicacion

#Cerrar archivo de escritura
if(respuesta == "s"): #Cerrar solo si se ha abierto
	print("    [*]Liberando archivo de escritura...")
	archivo.write("0 0\n0 0\n0 0\n0 0\n0 0\n0 0\n") #Escribir 6 veces que NO se hagan correcciones en los archivos
	archivo.close() #Liberar fichero
	
#Configurar GPIOs utilizados como entradas por seguridad (evita salidas HIGH y cortocircuitos accidentales)
print("    [*]Reseteando GPIOs...")
GPIO.cleanup()

print("\n\n[<]Programacion finalizada con exito[>]\n\n")





