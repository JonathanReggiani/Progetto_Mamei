import time
from PyP100 import PyP110
import paho.mqtt.client as mqtt

p110 = PyP110.P110("192.168.1.158", "reggianijonathan@gmail.com", "tapoteam1")
p110.handshake() #Creates the cookies required for further methods
p110.login() #Sends credentials to the plug and creates AES Key and IV for further methods

defaultTopicE = "/sensor/energia"
broker_ip = "broker.emqx.io"
portaMosquito = 1883 #porta specifica nel localhost da cui si lancia il codice
sensor = 'TV_JZ'

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
    r = p110.getEnergyUsage() #Returns dict with all of the energy usage of the connected plug
    print(r)
    #{'result': {'today_runtime': 91, 'month_runtime': 91, 'today_energy': 62, 'month_energy': 62, 'local_time': '2023-06-11 16:13:32', 'electricity_charge': [0, 0, 0], 'current_power': 41461}, 'error_code': 0}
    date = r['result']['local_time']
    today_energy = r['result']['today_energy']/1000 #da W a KW
    energy_list.append(today_energy)
    hour = date.split(" ")[1][:2]
    if(hour=='00'): #se lo facciamo al minuto, deve essere 00 anche il minuto
        count=1
    if(count>1):
        last_energy = energy_list[count-1] - energy_list[count-2]
        date = date.replace('-','/')
        print(date)
        toFirestore = str(date) + ',' + str(last_energy)
        print(toFirestore)
        #dati firestore
        print(sensor, 'invio...')
        infot = mqtt_client.publish(f'ProgettoMameiIoT/energia/sensor/{sensor}', f'val={toFirestore}')
        infot.wait_for_publish()
        #inviamo i dati una volta all'ora
    time.sleep(3600)