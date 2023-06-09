import pandas as pd
import json
from flask import Flask, request, render_template, redirect, url_for, flash
from json import loads
from base64 import b64decode
#from google.cloud import firestore
#from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
#from secret import secret_key
import paho.mqtt.client as mqtt
import time
from google.cloud import firestore
from requests import get, post

#Variabili da impostare
filePath = "C:\\Users\\Jonathan\Desktop\Csv" #!!!! to modify
xlsEnergia = "Consumo di Energia_Storico.xls"
xlsPotenza = "Potenza_Storico.xls"
csvEnergia = filePath + "\Consumo di Energia_Storico.csv"
csvPotenza = filePath +  "\Potenza_Storico.csv"
defaultTopicE = "/sensor/energia"
defaultTopicP = "/sensor/potenza"
broker_ip = "broker.emqx.io"
portaMosquito = 1883 #porta specifica nel localhost da cui si lancia il codice
sensor = 'frigoriferoJZ'

#FUNZIONI
# funzione di callback per la connessione al broker MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

'''
def daDefinire
    # invio della riga al server sul topic "data"
    rc, mid = mqtt_client.publish(defaultTopicP, line.strip())
    if rc == mqtt.MQTT_ERR_SUCCESS:
        success = mqtt_client.wait_for_publish(mid, timeout=5)
        if success:
            print("Message published with success within timeout")
        else:
            print("Timeout expired while waiting for message publication confirmation")
    else:
        print("Error while publishing message")
    print("Sent")
    print(line)
    time.sleep(0.1)  # attesa di 1 secondo tra le invii
'''

#lettura file excel
df = pd.read_excel(xlsEnergia, skiprows=[0], header=None)
df = df.replace('/',0)
print(df)
'''dict = df.to_dict()
print(dict)'''

df1 = pd.read_excel(xlsPotenza, skiprows=[0], header=None)
df1 = df1.replace('/',0)
print(df1)

#salvo i file in un csv
df.to_csv(csvEnergia, index=False)
df1.to_csv(csvPotenza, index=False)

# connessione al broker MQTT
mqtt_client = mqtt.Client(f'ProgettoMameiIoT-{sensor}')
#mqtt_client.on_connect = on_connect
mqtt_client.connect(broker_ip, portaMosquito)
mqtt_client.loop_start()

# apertura del file data e invio dei dati al server
print("Inizio csv Potenza")
c=0
with open(csvPotenza) as f:
    for line in f:
        if (c > 0):
            print(sensor, 'invio....')
            infot = mqtt_client.publish(f'ProgettoMameiIoT/potenza/sensor/{sensor}', f'val={line.strip()}')
            infot.wait_for_publish()
            print('Message Sent: ' + line.strip())
            time.sleep(1)
            print(sensor, 'invio 2....')
            infot = mqtt_client.publish(f'ProgettoMameiIoT/potenza/sensor/{sensor}', f'val={line.strip()}')
            infot.wait_for_publish()
            print('Message Sent: ' + line.strip())
            time.sleep(1)
            print(sensor, 'invio 3....')
            infot = mqtt_client.publish(f'ProgettoMameiIoT/potenza/sensor/{sensor}', f'val={line.strip()}')
            infot.wait_for_publish()
            print('Message Sent: ' + line.strip())
            time.sleep(10)
        else:
            print("Saltiamo l'header")
            c+=1
print("Inizio csv Energia")
c=0
with open(csvEnergia) as f:
    for line in f:
        if(c>0):
            print(sensor, 'invio....')
            infot = mqtt_client.publish(f'ProgettoMameiIoT/energia/sensor/{sensor}', f'val={line.strip()}')
            infot.wait_for_publish()
            print('Message Sent: ' + line.strip())
            time.sleep(1)
            print(sensor, 'invio 2....')
            infot = mqtt_client.publish(f'ProgettoMameiIoT/energia/sensor/{sensor}', f'val={line.strip()}')
            infot.wait_for_publish()
            print('Message Sent: ' + line.strip())
            time.sleep(1)
            print(sensor, 'invio 3....')
            infot = mqtt_client.publish(f'ProgettoMameiIoT/energia/sensor/{sensor}', f'val={line.strip()}')
            infot.wait_for_publish()
            print('Message Sent: ' + line.strip())
            time.sleep(3)
            c+=1
        else:
            print("Saltiamo l'header")
            c+=1

mqtt_client.loop_stop()