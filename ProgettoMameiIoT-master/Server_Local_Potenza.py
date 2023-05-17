import paho.mqtt.client as mqtt
from flask import Flask, request
import json
from google.cloud import firestore
from secret import secret_key
import time
from requests import get, post

'''data = {}
diz = {}'''

def on_connectP(client, userdata, flags, rc):
    mqtt_client.subscribe(default_topicP)

def on_message(client, userdata, message):
    print("message topic: ", message.topic)
    print("message received: ", str(message.payload.decode("utf-8")))
    s = message.topic.split('/')[-1]
    val = float(str(message.payload.decode("utf-8")).split(',')[1])
    date = str(message.payload.decode("utf-8")).split(',')[0].split('=')[1] #da convertire in data
    print("s: " + s)
    print("val: ", val)
    print("data: " + date)
    #richiesta post di invio dei dati
    base_url = 'http://localhost' #va bene sia per pc mio che per ssh
    #base_url = '34.154.51.140'
    #base_url = 'https://mamei-test2-382313.appspot.com'
    print('eseguo r')
    r = post(f'{base_url}/sensors/{s}', data={ 'val': val})
    print('eseguito')
    time.sleep(1)

    '''if (date in diz.keys()):
        diz.update({date: val})
        print("update")
    else:
        diz[date] = val
        print("else")
    data[s] = diz
    print(data)'''


client_id = 'c2'
broker_ip = 'broker.emqx.io'
broker_port = 1883

default_topicP = 'ProgettoMameiIoT/potenza/sensor/#'

mqtt_client = mqtt.Client(f'ProgettoMameiIoT-{client_id}')
mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connectP
print('connect',broker_ip, broker_port)
mqtt_client.connect(broker_ip, broker_port, keepalive=60)
print("connected")

mqtt_client.loop_start()

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

@app.route('/sensors/<s>',methods=['POST'])
def add_data(s):
    val = float(request.values['val'])
    #print('val',val)
    print('sono in add data', val)
    db = firestore.Client.from_service_account_json('Credentials.json')
    doc_ref = db.collection('sensors').document(s)
    entity = doc_ref.get()
    if entity.exists and 'values' in entity.to_dict():
        v = entity.to_dict()['values']
        v.append(val)
        doc_ref.update({'values':v})
    else:
        doc_ref.set({'values':[val]})
    return 'ok',200

@app.route('/sensors/<s>',methods=['GET'])
def get_data(s):
    print('scopami forte')
    db = firestore.Client.from_service_account_json('Credentials.json')
    entity = db.collection('sensors').document(s).get()
    print('entity', entity)
    if entity.exists:
        print('bello mio')
        return json.dumps(entity.to_dict()['values']), 200
    else:
        print('sono fatto')
        return 'sensor not found', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


mqtt_client.loop_stop()