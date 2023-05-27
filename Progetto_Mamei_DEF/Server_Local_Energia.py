import paho.mqtt.client as mqtt
from flask import Flask, request, flash
import json
from google.cloud import firestore
from secret import secret_key
import time
from requests import get, post
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask import Flask,request,render_template,redirect,url_for
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import datetime
import tkinter as tk
import tkinter as tk
from tkinter import messagebox
import threading

prima_previsione = 0
def on_connectE(client, userdata, flags, rc):
    mqtt_client.subscribe(default_topicE)

def on_message(client, userdata, message):
    #print("message topic: ", message.topic)
    #print("message received: ", str(message.payload.decode("utf-8")))
    s = message.topic.split('/')[-1]
    val = float(str(message.payload.decode("utf-8")).split(',')[1])
    date = str(message.payload.decode("utf-8")).split(',')[0].split('=')[1] #da convertire in data
    #print("s: " + s)
    #print("val: ", val)
    #print("data: " + date)
    #richiesta post di invio dei dati
    base_url = 'http://localhost' #va bene sia per pc mio che per ssh
    #base_url = '34.154.51.140'
    #base_url = 'https://mamei-test2-382313.appspot.com'
    #print('eseguo r')
    r = post(f'{base_url}/sensors/{s}', data={'date':date, 'val':val})
    #r1 = post(f'{base_url}/sensors/{s}', data={'val':val})
    #info = {'colonna1':r, 'colonna2':r1}
    #print('eseguito')
    time.sleep(1)

def remove_dup (collezione, documento_id, campo_da_modificare, date_check):
    #db = firestore.Client()
    db = firestore.Client.from_service_account_json('Credentials.json')
    # Specifica il percorso del documento e l'ID del documento
    collezione = collezione
    documento_id = documento_id
    # Specifica il campo da modificare
    campo_da_modificare = campo_da_modificare
    # Recupera il riferimento al documento
    documento_ref = db.collection(collezione).document(documento_id)
    valore_da_elim = ''
    # Recupera il documento
    documento = documento_ref.get()
    if documento.exists:
        dati_documento = documento.to_dict()
        # Verifica se il campo da modificare esiste nel documento
        if campo_da_modificare in dati_documento:
            campo = dati_documento[campo_da_modificare]
            #print('campo: ', campo)
            #print('campo da mod: ', campo_da_modificare)
            valore = documento.get(campo_da_modificare)
            #print('valore: ', valore)
            for i in valore:
                if i['date'] == str(date_check):
                    #print('trovato')
                    valore_da_elim = i
                    # Verifica se il campo è di tipo array o mappa
                    if isinstance(campo, list):
                        # Elimina il valore dall'array
                        campo.remove(valore_da_elim)
                    elif isinstance(campo, dict):
                        # Elimina il valore dalla mappa
                        campo.pop(valore_da_elim, None)
                    else:
                        print("Il campo specificato non è di tipo array o mappa.")
                        exit()
            # Aggiorna il campo nel documento
            documento_ref.update({campo_da_modificare: campo})
            if valore_da_elim == '':
                #print('Non è stato eliminato nulla')
                #print('valore: ', valore)
                return ''
            else:
                #print(f"Il valore '{valore_da_elim}' è stato eliminato con successo dal campo '{campo_da_modificare}'.")
                #print('valore: ', valore)
                return valore_da_elim
        else:
            print(f"Il campo '{campo_da_modificare}' non è presente nel documento.")
    else:
        print("Il documento non esiste.")

client_id = 'c2'
broker_ip = 'broker.emqx.io'
broker_port = 1883

default_topicE = 'ProgettoMameiIoT/energia/sensor/#'

mqtt_client = mqtt.Client(f'ProgettoMameiIoT-{client_id}')
mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connectE
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

'''
@app.route('/',methods=['GET','POST'])
@app.route('/main',methods=['GET','POST'])
@app.route('/sensors',methods=['GET'])
def main():
    db = firestore.Client.from_service_account_json('Credentials.json')
    s = []
    for doc in db.collection('sensors').stream():
        s.append(doc.id)
    return json.dumps(s), 200'''


@app.route('/sensors/prediction/<s>',methods=['POST'])
def add_prediction(s):
    s1 = s+'_prediction'
    data_prev = request.values['data_prev']
    prediction = float(request.values['prediction'])
    date_pred = {'date': data_prev, 'pred': prediction}
    #val = request.values['val']
    #print('sono in add data date', date)
    #print('sono in add data val', val)
    #print('sono in add pred', date_pred)
    db = firestore.Client.from_service_account_json('Credentials.json')
    doc_ref = db.collection('sensors').document(s1)
    entity_pred = doc_ref.get()
    #print("Entity: ", entity)
    documento_ref = db.collection('sensors').document(s1)
    documento = documento_ref.get()
    if entity_pred.exists and 'prediction' in entity_pred.to_dict():
        # se frigorigero_pred esiste e se ha una colonna prediction
        d_pred = entity_pred.to_dict()['prediction']
        #print("d prima di rimuovere: ", d)
        valore_da_rimuovere = remove_dup('sensors', s1, 'prediction', data_prev)
        if valore_da_rimuovere != '' and valore_da_rimuovere in d_pred:
            d_pred.remove(valore_da_rimuovere)
        #print("d dopo di rimuovere: ", d)
        d_pred.append(date_pred)
        #print('d con append', d_pred)
        doc_ref.update({'prediction': d_pred})
    else:
        # se frigorigero_pred non esiste, aggiungi tutto
        print('Sono in SET')
        doc_ref.set({'prediction': [date_pred]})
        print('date_val in set: ', date_pred)
    return 'ok', 200

    #doc_ref.set({'prediction': [prediction]})
    #print('date_val in set: ', prediction)
    #return 'ok',200

@app.route('/sensors/<s>',methods=['POST'])
def add_data(s):
    date = request.values['date']
    val = float(request.values['val'])
    date_val = {'date': date, 'val': val}
    #val = request.values['val']
    #print('sono in add data date', date)
    #print('sono in add data val', val)
    print('sono in add data date_val', date_val)
    db = firestore.Client.from_service_account_json('Credentials.json')
    doc_ref = db.collection('sensors').document(s)
    entity = doc_ref.get()
    #print("Entity: ", entity)
    documento_ref = db.collection('sensors').document(s)
    documento = documento_ref.get()
    #print('Inizio rim dup: ', date)
    if entity.exists and 'energia' in entity.to_dict():
        # se frigorigero esiste e se ha una colonna data
        # se esiste una data, me la sovrascrivi con l'ultimo valore
        d = entity.to_dict()['energia']
        #print("d prima di rimuovere: ", d)
        valore_da_rimuovere = remove_dup('sensors', s, 'energia', date)
        if valore_da_rimuovere != '' and valore_da_rimuovere in d:
            d.remove(valore_da_rimuovere)
        #print("d dopo di rimuovere: ", d)
        d.append(date_val)
        #print('d con append', d)
        doc_ref.update({'energia': d})
    else:
        #se frigorifero non esiste, aggiungimi tutto
        #print('Sono in SET')
        doc_ref.set({'energia':[date_val]})
        #print('date_val in set: ', date_val)
    return 'ok',200

'''@app.route('/sensors/<s>',methods=['GET'])
def get_data(s):
    db = firestore.Client.from_service_account_json('Credentials.json')
    entity = db.collection('sensors').document(s).get()
    #print('entity', entity)
    if entity.exists:
        return json.dumps(entity.to_dict()['energia']), 200
    else:
        return 'sensor not found', 404'''

@app.route('/graph/<s>',methods=['GET'])
@login_required
def graph_data(s):
    db = firestore.Client.from_service_account_json('Credentials.json')
    entity = db.collection('sensors').document(s).get()
    if entity.exists:
        di = []
        di.append(['Number',s])
        #x la data
        #y i valori
        for x in entity.to_dict()['energia']:
            di.append([x['date'], x['val']])
            new_entry = x['val']
            #print('x,y', (x['date'], x['val']))
            #print('d', di)
        F1 = 0
        F2 = 0
        F3 = 0
        date_fasce = []
        d1 = []
        d1.append(['Giorno', 'F1', 'F2', 'F3'])
        giorno = ''
        print('date_fasce prima: ', date_fasce)
        for x in entity.to_dict()['energia']:
            giorno = x['date'].split(" ")[0]
            if giorno not in date_fasce:
                date_fasce.append(giorno)
        print('date_fasce dopo: ', date_fasce)
        giorno = ''
        for data_for in date_fasce:
            F1 = 0
            F2 = 0
            F3 = 0
            for x in entity.to_dict()['energia']:
                hour = int(x['date'].split(" ")[1].split(':')[0])
                day = datetime.datetime.strptime(x['date'], "%Y/%m/%d %H:%M:%S").strftime("%A").lower().strip()
                #print('date', x['date'], 'day', day)
                giorno = x['date'].split(" ")[0]
                if giorno == data_for:
                    if day != 'saturday' and day!= 'sunday':
                        if hour >= 8 and hour < 19:
                            #print(x['date'].split(" ")[1].split(':')[0])
                            F1+=x['val']
                        elif (hour >= 19 and hour < 23) or (hour==7):
                            F2+=x['val']
                        else:
                            F3+=x['val']
                    elif day == 'saturday':
                        if hour>=7 and hour<=22:
                            F2 += x['val']
                        else:
                            F3 += x['val']
                    else:
                        F3 += x['val']
            d1.append([data_for, F1, F2, F3])
        print('d1------------------>', d1)

        ####regressione####
        # Dati di esempio: consumi storici
        #anni = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
        #print(anni)
        #consumi = np.array([10, 12, 15, 18, 20, 22, 25, 28, 30, 32, 35, 38])

        array_date = []
        consumi = []
        date_future = []
        m = 0
        for i in range(len(entity.to_dict()['energia'])):
            array_date.append(i)
            consumi.append(entity.to_dict()['energia'][i]['val'])
            m=i

        array_date = np.array(array_date).reshape(-1, 1)
        #print('Array DATE: ', array_date)
        consumi = np.array(consumi)

        # Creazione del modello di regressione lineare
        modello = LinearRegression()

        # Addestramento del modello
        modello.fit(array_date, consumi)

        # Determina l'ultima data presente nel dataset
        ultimo_numero = m
        ultima_data = entity.to_dict()['energia'][ultimo_numero]['date']

        # Genera una sequenza di date per le 4 ore successive
        numeri_futuri = np.arange(ultimo_numero+1, ultimo_numero+9).reshape(-1, 1)

        # Calcola l'ora successiva all'ultima ora
        #prossima_ora = datetime.datetime.fromordinal(ultima_data).replace(hour=datetime.datetime.fromordinal(ultima_data).hour + 1)
        #prossima_ora = ultima_data + datetime.timedelta(hours=1)

        def AggiungiOra(data):
            #data = "2023/05/25 15:30:00"
            formato_data = "%Y/%m/%d %H:%M:%S"

            # Converti la stringa di data in un oggetto datetime
            data_datetime = datetime.datetime.strptime(data, formato_data)

            # Aggiungi un'ora all'oggetto datetime
            data_avanti = data_datetime + datetime.timedelta(hours=1)

            # Converti l'oggetto datetime risultante in una stringa nel formato desiderato
            data_avanti_stringa = data_avanti.strftime(formato_data)

            print(data_avanti_stringa)
            return data_avanti_stringa

        def show_custom_popup():
            popup = tk.Toplevel()
            popup.title("Pop-up Personalizzato")
            popup.geometry("300x150")
            label = tk.Label(popup, text="Questo è un pop-up personalizzato!", font=("Arial", 14))
            label.pack(pady=20)
            button = tk.Button(popup, text="Chiudi", command=popup.destroy)
            button.pack()
            # Solleva la finestra pop-up davanti a tutto
            popup.lift()
            popup.attributes("-topmost", True)
            popup.mainloop()
            # Funzione per eseguire il codice tkinter nel thread UI
        def run_tkinter():
            root = tk.Tk()
            root.withdraw() # Nasconde la finestra principale
            show_custom_popup()

        # Esegui il codice tkinter nel thread UI
        #thread = threading.Thread(target=run_tkinter)
        #thread.start()
        #prossima_ora = AggiungiOra(entity.to_dict()['energia'][-1]['date'])
        '''ultima_data = datetime.datetime.strptime(entity.to_dict()['energia'][-1]['date'], '%Y/%m/%d %H:%M:%S')
        print('entityy -1 date',type(entity.to_dict()['energia'][-1]['date']))
        #print('tipo di ultima data', type(ultima_data))
        prossima_ora = ultima_data + timedelta(hours=1)'''
        #print('ora prima del for', entity.to_dict()['energia'][-1]['date'])
        ora_attuale = entity.to_dict()['energia'][-1]['date']
        for i in range(7):
            prossima_ora = AggiungiOra(ora_attuale)
            date_future.append(prossima_ora)
            #print('prossima ora', prossima_ora)
            ora_attuale=prossima_ora
        #print('date future dopo for', date_future)
        date_future = np.array(date_future).reshape(-1,1)
        #print('date future con reshape', date_future)
        # Genera una sequenza di date per le 4 ore successive
        #date_future = np.arange(prossima_ora.toordinal(), prossima_ora.toordinal() + 8).reshape(-1, 1)
        #print('DATE FUTUREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE',date_future)


        doc_ref = db.collection('sensors').document(s+'_prediction')
        entity_prediction = doc_ref.get()
        print('new entry inizio', new_entry)
        try:
            last_prediction = entity_prediction.to_dict()['prediction']
            #print('last predicrtion try: ', last_prediction[0])
            #print("Try => non primo giro") #se non è vuoto allora calcoliamo
            #print('new entry', new_entry)
            #print('last prediction VAL', last_prediction[0]['pred'])
            scostamento = new_entry - last_prediction['pred']
            #print('scostamento', scostamento)
        except Exception:
            print("Exception => primo giro")

        # Prevedi i consumi per le date future
        consumi_previsti = modello.predict(numeri_futuri)
        #print('consumi previsti',consumi_previsti[0])
        prima_previsione = consumi_previsti[0]
        base_url = 'http://localhost'
        #print("DATE FUTUREEEEE: ", date_future[0])
        #print("Consumi: ", consumi_previsti[0])
        r1 = post(f'{base_url}/sensors/prediction/{s}', data={'data_prev':date_future[0],'prediction': consumi_previsti[0]})

        # Stampa dei risultati
        #print("--------------------------------Consumi previsti:")
        for dat, consumo in zip(numeri_futuri, consumi_previsti):
            print(f"Data {dat}: {consumo}")

        de = []
        dp = []
        de.append(['Data', s])
        dp.append(['Number', 'Previsione '+s])
        # x la data
        # y i valori

        for x in entity.to_dict()['energia']:
            de.append([x['date'], x['val']])
            #print('x,y', (x['date'], x['val']))
            #print('d', de)
        for x in entity_prediction.to_dict()['prediction']:
            dp.append([x['date'], x['pred']])
        for y in range(len(date_future)):
            if(y>0): #la prima previsione è considerata nel ciclo sopra
                #print('y', y)
                #print(date_future[y][0])
                #print('y in data', datetime.datetime.fromordinal(date_future[y]))
                dp.append([date_future[y][0], consumi_previsti[y]])
                #print('x,y', (x['date'], x['val']))
                #print('d', de)
        #print(dp)
        return render_template('graph.html',sensor=s,data=json.dumps(di), data2=json.dumps(d1), data3=json.dumps(de), data4=json.dumps(dp))
    else:
        return redirect(url_for('static', filename='sensor404.html'))

@app.route('/login', methods=['POST'])
def login():
    print('sono dentro il login')
    print(current_user.is_authenticated)
    if current_user.is_authenticated == True:
        return redirect('/static/gia_loggato.html')
    username = request.values['u']
    password = request.values['p']
    db = firestore.Client.from_service_account_json('Credentials.json')
    user_get = db.collection('utenti').document(username).get()
    user = db.collection('utenti').document(username)

    if user_get.exists and user_get.to_dict()['password']==password:
        login_user(User(username))
        if username == 'gaia':
            return redirect('/')
        else:
            #next_page = request.args.get('/static/home_utente.html')
            return redirect('/')
    return redirect('/static/login_post_errore.html')

@app.route('/logout')
def logout():
    print('sono dentro il logout')
    logout_user()
    return redirect('/')

@app.route('/')
@app.route('/main')
def main():
    return redirect('/static/main.html')

@app.route('/home_admin')
@login_required
def home_admin():
    if current_user.username == 'gaia':
        if request.method == 'GET':
            return redirect('/static/home_admin.html')
    else:
        return redirect('/static/reserved_admin.html')

@app.route('/home_utente')
@login_required
def home_utente():
    return redirect('/static/home_utente.html')

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
            user_get = db.collection('utenti').document(username).get()
            user = db.collection('utenti').document(username)
            if user_get.exists:
                user.set({'username': username, 'password': password})
                return redirect('/static/utente_modificato.html')
            else:
                user.set({'username': username, 'password': password})
                return redirect('/static/utente_inserito.html')
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

mqtt_client.loop_stop()