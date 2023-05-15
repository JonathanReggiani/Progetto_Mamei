import paho.mqtt.client as mqtt
from flask import Flask, request
import json
from google.cloud import firestore
from secret import secret_key

data = {}
diz = {}

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
    if (date in diz.keys()):
        diz.update({date: val})
        print("update")
    else:
        diz[date] = val
        print("else")
    data[s] = diz
    print(data)


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
'''
@app.route('/sensors/<s>',methods=['POST'])
def add_data(s):
    val = request.values['val']
    if s in data:
        data[s].append(val)
    else:
        data[s] = [val]
    print(data)
    print('ciao')
    return 'ok',200'''
@app.route('/sensors/<s>',methods=['POST'])
def add_data(s):
    print('sono in add data gays')
    local = True
    val = float(request.values['val'])
    print('val',val)
    db = firestore.Client.from_service_account_json('Credentials.json') if local else firestore.Client()
    doc_ref = db.collection('sensors').document(s)
    entity = doc_ref.get()
    if entity.exists and s in entity.to_dict():
        v = entity.to_dict()[s]
        v.append(val)
        doc_ref.update({s:v})
    else:
        doc_ref.set({s:[val]})
    return 'ok',200

'''# creazione di un entity (document)
id = 'ciao'
doc_ref = db.collection(coll).document(id) #id can be omitted
doc_ref.set({'nome':'sensor','value': [{'val':1}]})
print(doc_ref.get().id)

# accesso a un documento specifico (dato l'id)
entity = db.collection(coll).document(id).get()
print(entity.id,'--->',entity.to_dict()['nome'])'''
@app.route('/sensors/<s>',methods=['GET'])
def get_data(s):
    '''if s in data:
        return json.dumps(data[s]),200
    else:
        return 'sensor not found',404'''
    print('scopami forte')
    local = True
    db = firestore.Client.from_service_account_json('Credentials.json') if local else firestore.Client()
    entity = db.collection('sensors').document(s).get()
    print('entity', entity)
    if entity.exists:
        print('bello mio')
        return json.dumps(entity.to_dict()[s]), 200
    else:
        print('sono fatto')
        return 'sensor not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


mqtt_client.loop_stop()