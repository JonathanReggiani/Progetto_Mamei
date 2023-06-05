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
filePath = "C:\\Users\\Francesco Mindoli\PycharmProjects\ProgettoFinale" #!!!! to modify
#filePath = "C:\\Users\\Jonathan\Desktop\Csv"
#xlsEnergia = "Consumo di Energia_Storico.xls"
xlsEnergia = "MacchinettaCaffe_EnergiaJZ.xls"
csvEnergia = filePath + "\MacchinettaCaffe_EnergiaJZ.csv"
defaultTopicE = "/sensor/energia"
defaultTopicP = "/sensor/potenza"
broker_ip = "broker.emqx.io"
portaMosquito = 1883 #porta specifica nel localhost da cui si lancia il codice
sensor = 'macchinetta_caffeJZ'

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

#salvo i file in un csv
df.to_csv(csvEnergia, index=False)

# connessione al broker MQTT
mqtt_client = mqtt.Client(f'ProgettoMameiIoT-{sensor}')
#mqtt_client.on_connect = on_connect
mqtt_client.connect(broker_ip, portaMosquito)
mqtt_client.loop_start()

# apertura del file data e invio dei dati al server
print("Inizio csv Energia")
c=0
with open(csvEnergia) as f:
    for line in f:
        if(c>0):
            for i in range(2):
                print(sensor, 'invio...', i)
                infot = mqtt_client.publish(f'ProgettoMameiIoT/energia/sensor/{sensor}', f'val={line.strip()}')
                infot.wait_for_publish()
                print('Message Sent: ' + line.strip())
                if i == 1:
                    time.sleep(30)
                else:
                    time.sleep(15)
        else:
            print("Saltiamo l'header")
            c += 1
mqtt_client.loop_stop()