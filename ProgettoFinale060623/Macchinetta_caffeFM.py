import pandas as pd
import paho.mqtt.client as mqtt
import time

#Variabili da impostare
#filePath = "C:\\Users\\Francesco Mindoli\PycharmProjects\ProgettoFinale"#!!!! to modify
filePath = "C:\\Users\\Jonathan\Desktop\Csv"
xlsEnergia = "MacchinettaCaffe_EnergiaFM.xls"
csvEnergia = filePath + "\MacchinettaCaffe_EnergiaFM.csv"
defaultTopicE = "/sensor/energia"
defaultTopicP = "/sensor/potenza"
broker_ip = "broker.emqx.io"
portaMosquito = 1883 #porta specifica nel localhost da cui si lancia il codice
sensor = 'macchinetta_caffeFM'

#FUNZIONI
# funzione di callback per la connessione al broker MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

#lettura file excel
df = pd.read_excel(xlsEnergia, skiprows=[0], header=None)
df = df.replace('/',0)
print(df)

#salvo i file in un csv
df.to_csv(csvEnergia, index=False)
# connessione al broker MQTT
mqtt_client = mqtt.Client(f'ProgettoMameiIoT-{sensor}')
#mqtt_client.on_connect = on_connect
mqtt_client.connect(broker_ip, portaMosquito)
mqtt_client.loop_start()

# apertura del file data e invio dei dati al server
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