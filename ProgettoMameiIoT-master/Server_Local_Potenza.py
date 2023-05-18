import paho.mqtt.client as mqtt
from flask import Flask, request
import json
from google.cloud import firestore
from secret import secret_key
import time
from requests import get, post
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask import Flask,request,render_template,redirect,url_for

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

class User(UserMixin):
    def __init__(self, username):
        super().__init__()
        self.id = username
        self.username = username
        self.par = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

login = LoginManager(app)
login.login_view = '/static/login.html'

@login.user_loader
def load_user(username):
    db = firestore.Client.from_service_account_json('Credentials.json')
    user = db.collection('utenti').document(username).get()
    if user.exists:
        return User(username)
    return None

@app.route('/',methods=['GET','POST'])
@app.route('/main',methods=['GET','POST'])
@app.route('/sensors',methods=['GET'])
def main():
    db = firestore.Client.from_service_account_json('Credentials.json')
    s = []
    for doc in db.collection('sensors').stream():
        s.append(doc.id)
    return json.dumps(s), 200

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

@app.route('/graph/<s>',methods=['GET'])
@login_required
def graph_data(s):
    db = firestore.Client.from_service_account_json('Credentials.json')
    entity = db.collection('sensors').document(s).get()
    if entity.exists:
        d = []
        d.append(['Number',s])
        t = 0
        for x in entity.to_dict()['values']:
            d.append([t,x])
            t+=1
        return render_template('graph.html',sensor=s,data=json.dumps(d))
    else:
        return redirect(url_for('static', filename='sensor404.html'))

@app.route('/login', methods=['POST'])
def login():
    print('sono dentro il login')
    if current_user.is_authenticated:
        return redirect(url_for('/main'))
    username = request.values['u']
    password = request.values['p']
    db = firestore.Client.from_service_account_json('Credentials.json')
    user = db.collection('utenti').document(username).get()
    if user.exists and user.to_dict()['password']==password:
        login_user(User(username))
        next_page = request.args.get('next')
        if not next_page:
            next_page = '/main'
        return redirect(next_page)
    return redirect('/static/login.html')
@app.route('/logout')
def logout():
    print('sono dentro il logout')
    logout_user()
    return redirect('/')

@app.route('/adduser', methods=['GET','POST'])
@login_required
def adduser():
    if current_user.username == 'gaia':
        if request.method == 'GET':
            return redirect('/static/adduser.html')
        else:
            username = request.values['u']
            password = request.values['p']
            db = firestore.Client.from_service_account_json('Credentials.json')
            user = db.collection('utenti').document(username)
            user.set({'username':username,'password':password})
            return 'ok'
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

mqtt_client.loop_stop()