#!/bin/bash

#------------------------------------------------------------#
# LIBRERIAS
#------------------------------------------------------------#
import os
import sys
from socket import *
from socket import error
import json
import MySQLdb
import paho.mqtt.client as mqtt
import subprocess
import threading
#------------------------------------------------------------#
# PUERTOS UDP
#------------------------------------------------------------#
PORT = 5678         #puerto escuha del servidor UDP
BUFSIZE = 1024

#------------------------------------------------------------#
# VARIABLE
#------------------------------------------------------------#
sensor_temp = {0}
global payload
MQTT_HOST = "34.139.167.162"     # Dirección IP de la plataforma google cloud
#MQTT_HOST = "192.168.1.46"
MQTT_PORT = 1883                 #Puerto escucha del protocolo MQTT
MQTT_TOPIC = "hidroponia/datos"  # Tópico
#user="sensores"
#password="user"
#------------------------------------------------------------#
# Conexion MQTT
#------------------------------------------------------------#
client = mqtt.Client("hidroponia")
#client.username_pw_set(user,password=password)
#client.connect(MQTT_HOST,MQTT_PORT,60)
#------------------------------------------------------------#
# Start a client or server application for testing
#------------------------------------------------------------#
def main():
        if len(sys.argv) < 2:
                usage()
        if sys.argv[1] == '-s':
                server()
        elif sys.argv[1] == '-c':
                client()
        else:
                usage()
#------------------------------------------------------------#
# Prints the instructions
#------------------------------------------------------------#
def usage():
        sys.stdout = sys.stderr
        print 'Usage: udpecho -s [port] (server)'
        print 'or: udpecho -c host [port] <file (client)'
        sys.exit(2)

#------------------------------------------------------------#
# VERIFICAR CONEXION AL SERVIDOR
#------------------------------------------------------------#
def ping(MQTT_HOST, MQTT_MSG):
    response = subprocess.call(['ping', '-c', '1', MQTT_HOST],stdout=open('/dev/null', 'w'),
    stderr=open('/dev/null', 'w'))
    if response ==0:
        print MQTT_HOST, 'is up!'
        client.connect(MQTT_HOST,MQTT_PORT,60)   #envío de datos hacia la nube
        client.publish(MQTT_TOPIC,MQTT_MSG)

    else:
        print MQTT_HOST, 'is down'
#    return response
#------------------------------------------------------------#
# Conexion UDP
#------------------------------------------------------------#
def server():
    if len(sys.argv) > 2:
        port = eval(sys.argv[2])
    else:
        port = PORT
    try:
        s = socket(AF_INET6, SOCK_DGRAM)
        s.bind(('bbbb::1', port))
    except Exception:
        print "ERROR: Server Port Binding Failed"
        return
    print 'udp echo server ready: %s' % port
    while 1:
        data, addr = s.recvfrom(BUFSIZE)   #la variable data contiene la información de los sensores
        MQTT_MSG=json.dumps(data)          #MQTT_MSG= almacena los datos para enviar hacia el cloud

        payload =  (data.split("|")[2])
        if payload == 't':
                          tem = (data.split("|")[3])
                          dirip = (addr[0])

                          db = MySQLdb.connect(host="192.168.0.46",  # Dirección IP del servidor MYSQL
                                               user="6lowpan",       # Usuario del servidor MYSQL
                                               passwd="user",     # Contraseña del usuario
                                               db="temperatura")   # nombre de tabla
                          val = (dirip, tem)  # Datos almacenar en el servidor MYSQL
                          cur = db.cursor()   
                          sql = "INSERT INTO tempe (address,temp) VALUES (%s,%s)" # Ingresar los datos en la tabla de MSQL
                          val = [dirip, tem]
                          cur.execute(sql,val)
                          db.commit()
                          db.close()  #cierre de conexión con la base de datos

        if payload == 'h':
                          hum=  (data.split("|")[3])
                          dirip = (addr[0])
                          dbhum = MySQLdb.connect(host="192.168.0.46",  # your host
                                                  user="6lowpan",       # username
                                                  passwd="user",     # password
                                                  db="humedad")   # name of the database
                          cur = dbhum.cursor()
                          sqlhum = "INSERT INTO datos (address,hum) VALUES (%s,%s)"
                          valhum = [dirip, hum]
                          cur.execute(sqlhum,valhum)
                          dbhum.commit()
#                          dbhum.close()
        if payload == 'p':
                          ph=  (data.split("|")[3])
                          dirip = (addr[0])
                          dbph = MySQLdb.connect(host="192.168.0.46",  # your host
                                                  user="6lowpan",       # username
                                                  passwd="user",     # password
                                                  db="ph")   # name of the database
                          cur = dbph.cursor()
                          sqlph = "INSERT INTO dato (address,ph) VALUES (%s,%s)"
                          valph = [dirip, ph]
                          cur.execute(sqlph,valph)
                          dbph.commit()



#        sql = "INSERT INTO datos (address,temp,hum,ph) VALUES (%s,%s,%s,%s)"
#        val = [dirip,tem,hum,ph]
#        cur.execute(sql, val)
#        db.commit()
#        print tem
#        print dirip
        x = threading.Thread(target=ping, args=(MQTT_HOST, MQTT_MSG,))
        x.start()


        print 'server received', `data`, 'from', `addr`
        s.sendto(data, addr)
#------------------------------------------------------------#
# MAIN APP
#------------------------------------------------------------#
main()
