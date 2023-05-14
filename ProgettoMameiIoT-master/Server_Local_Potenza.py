import paho.mqtt.client as mqtt

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

mqtt_client.loop_forever()