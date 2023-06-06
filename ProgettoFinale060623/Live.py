import time
from PyP100 import PyP110
import paho.mqtt.client as mqtt

p110 = PyP110.P110("192.168.0.179", "mindolifrancesco@gmail.com", "ProvaPw99")
p110.handshake() #Creates the cookies required for further methods
p110.login() #Sends credentials to the plug and creates AES Key and IV for further methods

defaultTopicE = "/sensor/energia"
broker_ip = "broker.emqx.io"
portaMosquito = 1883 #porta specifica nel localhost da cui si lancia il codice
sensor = 'TV_FM'

#FUNZIONI
# funzione di callback per la connessione al broker MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# connessione al broker MQTT
mqtt_client = mqtt.Client(f'ProgettoMameiIoT-{sensor}')
#mqtt_client.on_connect = on_connect
mqtt_client.connect(broker_ip, portaMosquito)
mqtt_client.loop_start()

run = True
count=0
energy_list = []
while(run):
    count += 1
    #The P110 has all the same basic functions as the plugs and additionally allow for energy monitoring.
    r = p110.getEnergyUsage() #Returns dict with all of the energy usage of the connected plug
    date = r['result']['local_time']
    today_energy = r['result']['today_energy']
    energy_list.append(today_energy)
    hour = date.split(" ")[1][:2]
    if(hour=='00'): #se lo facciamo al minuto, deve essere 00 anche il minuto
        count=1
    if(count>1):
        last_energy = energy_list[count-1] - energy_list[count-2]
        date = date.replace('-','/')
        toFirestore = str(date) + ',' + str(last_energy)
        #dati firestore
        print(sensor, 'invio...')
        infot = mqtt_client.publish(f'ProgettoMameiIoT/energia/sensor/{sensor}', f'val={toFirestore}')
        infot.wait_for_publish()
        #inviamo i dati una volta all'ora
    time.sleep(5)