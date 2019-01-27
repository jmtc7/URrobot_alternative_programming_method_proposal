
print("\n\n[<]Iniciada reproduccion de movimientos[>]\n\n")
print("[#]Iniciado proceso de configuracion previa")




###### ### ##  IMPORTACION DE DEPENDENCIAS  ## ### ######


print("    [*]Importando dependencias...")

#Para uso general
import os #Para comprobar si existe el archivo a leer
import time  #Para usar "sleep"

#Para escribir por MODBUS TCP
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.client.sync import ModbusTcpClient as ModbusClient




###### ### ##  C O N S T A N T E S   D E   C O N F I G U R A C I O N  ## ### ######


#Comunicaciones
HOST = "192.168.1.147" #IP del robot
PORT = 502 #Puerto del servidor Modbus del robot

#Tiempo entre lectura y envio (en segundos)
DELAY_ITERACIONES = 0.048496 # 0.048496s es lo que tardaba el otro programa en obtener cada dato




###### ### ##  O T R A S   I N I C I A L I Z A C I O N E S  ## ### ######


#Abrir archivo de escritura
print("    [*]Abriendo archivo para leer los movimientos almacenados...")
respuesta = "s"
if(os.path.isfile("correcciones.txt")): #Si ya existe el archivo en el directorio desde el que se ejecuta el programa
	fichero = open("correcciones.txt", "r") #Abrir
else:
	print("    [!]ERROR! No existe el archivo 'correcciones.txt' en el directorio actual")
	


#Inicializar comunicaciones
print("    [*]Configurando comunicaciones...")
client = ModbusClient(HOST, PORT) #Abrir puerto de comunicacion con el robot (para enviar valores por MODBUS)
comunicacion_OK = True

if(client.connect() == False):
	print("    [!]ERROR! Ha sido imposible conectarse al servidor Modbus")
	comunicacion_OK = False
	ret = False

#Escribir 0 en los registros
time.sleep(0.01) #esperar 10ms
client.write_register(128, 0) #Anular correccion en X
time.sleep(0.01) #esperar 10ms
client.write_register(129, 0) #Anular correccion en Y
raw_input("    [*]Todo listo. Pulse 'Enter' para continuar...")
print("\n")




###### ###### ### ## #   ###### ### ##  #  ## ### ######   # ## ### ######

###### ### ##  I N I C I O   D E   B U C L E   P R I N C I P A L  ## ### ######

###### ###### ### ## #   ###### ### ##  #  ## ### ######   # ## ### ######


print("[#]Iniciado programa principal")

linea1 = fichero.readline() #Leer primera linea

while linea1 != "": #Bucle mientras no se alcance el fin de fichero
	try:
		#Separar lectura por espacios y almacenar valores (correcciones en X e Y de la posicion del robot)
		correccionX, correccionY = linea1.split(" ")
		
		#Convertir de "string" (lectura de fichero) a "float"
		correccionX = float(correccionX)
		correccionY = float(correccionY)
		
		time.sleep(DELAY_ITERACIONES) #Aproximacion de lo que tardaba una ejecucion del bucle de control


		
		
		###### ### ##  E S C R I T U R A   D E   R E G I S T R O S   P O R   M O D B U S  ## ### ######


		#Indicar signo de X en el registro 130
		if correccionX > 0:
			client.write_register(130, 1)
		else:
			client.write_register(130, 0)
				
		#Escribir la correccion de X en el registro 128
		client.write_register(128, abs(float(correccionX)*1000/2))


		#Indicar signo de Y en el registro 131
		if correccionY > 0:
			client.write_register(131, 1)
		else:
			client.write_register(131, 0)
		#Escribir la correccion de Y en el registro 129
		client.write_register(129, abs(float(correccionY)*1000/2))



		#Leer nueva linea
		linea1 = fichero.readline()



	#Si se pulsa "Ctrl+C" -> SALIR
	except KeyboardInterrupt:
		print("s\n[!]Se ha puslado 'Ctrl+C' -> Finalizando programa...")
		break




###### ### ##  S E C U E N C I A   D E   F I N A  L I Z A C I O N  ## ### ######


print("\n[#]Iniciado proceso de finalizacion del programa")

#Cerrar sockets
if(comunicacion_OK == True):
	print("    [*]Cerrando comunicaciones...")
	time.sleep(0.01) #esperar 10ms
	client.write_register(128, 0) #Anular correccion en X
	time.sleep(0.01) #esperar 10ms
	client.write_register(129, 0) #Anular correccion en Y
	client.close() #Cerrar comunicacion
	
#Cerrar archivo de escritura
print("    [*]Liberando archivo de lectura...")
file.close(fichero)
	
	
print("\n\n[<]Reproduccion de movimientos finalizado con exito[>]\n\n")

