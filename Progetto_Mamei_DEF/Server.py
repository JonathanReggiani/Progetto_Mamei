import paho.mqtt.client as mqtt
from google.cloud import firestore
import json
import os

#Variabili da impostare
pathCredential = r"C:\Users\Francesco Mindoli\Desktop\Mamei\Credentials.json"
portaMosquito=1434
defaultTopicE = "/sensor/energia"
defaultTopicP = "/sensor/potenza"

#Recupero credenziali
service_account_info = json.load(open("Credentials.json"))
print(service_account_info)

# Inizializza un client Firestore
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = pathCredential
db = firestore.Client.from_service_account_json('Credentials.json')
print("DB inizializzato")

# Funzione di callback che viene chiamata quando il client riceve un messaggio MQTT
def on_message(client, userdata, message):
    # Decodifica il messaggio come stringa
    payload_str = message.payload.decode('utf-8')

    # Esempio di elaborazione dei dati: scrivi il messaggio ricevuto nel database Firestore
    doc_ref = db.collection(u'data').document()
    doc_ref.set({
        u'value': payload_str,
    })


# Creazione del client MQTT
client = mqtt.Client()

# Impostazione delle funzioni di callback per la connessione e la ricezione dei messaggi
client.on_connect = lambda client, userdata, flags, rc: \
    print("Connected with result code " + str(rc))
client.on_message = on_message


# Connessione al broker MQTT
client.connect("localhost", portaMosquito, 60)
print("Connesso")


# Iscrizione al topic "data" per ricevere i messaggi pubblicati su questo topic
client.subscribe(defaultTopicE)

'''
def upload_data(msg):
    print("caricamento dati..")
    db = firestore.Client.from_service_account_json('Credentials.json')
    data = msg.split("next")
    for d in data:
        if d != "":
            values = d.split("$")
            db.collection(values[0]).document(values[1]).set({
                "data&ora": values[1], "portata": float(values[2]), "temperatura1": float(values[3]), "temperatura2": float(values[4]), "energia": float(values[5]), "potenza": float(values[6]), "volume": float(values[7])
            })
            db.collection("last").document(values[0]).set({
                "data&ora": values[1], "portata": float(values[2]), "temperatura1": float(values[3]), "temperatura2": float(values[4])
            })
    return "OK"
'''

# Loop del client MQTT per ricevere i messaggi in modo asincrono
client.loop_forever()

