import paho.mqtt.client as mqtt
import json
from google.cloud import firestore
from requests import post
from secret import secret_key
import time
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask import Flask,request,render_template,redirect,url_for
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime

prima_previsione = 0
def on_connectE(client, userdata, flags, rc):
    mqtt_client.subscribe(default_topicE)

def on_message(client, userdata, message):
    s = message.topic.split('/')[-1]
    val = float(str(message.payload.decode("utf-8")).split(',')[1])
    date = str(message.payload.decode("utf-8")).split(',')[0].split('=')[1] #da convertire in data
    #richiesta post di invio dei dati
    base_url = 'http://localhost' #va bene sia per pc mio che per ssh
    #base_url = '34.154.51.140'
    #base_url = 'https://mamei-test2-382313.appspot.com'
    r = post(f'{base_url}/sensors/{s}', data={'date':date, 'val':val})
    time.sleep(1)

def remove_dup (collezione, documento_id, campo_da_modificare, date_check):
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
            valore = documento.get(campo_da_modificare)
            for i in valore:
                if i['date'] == str(date_check):
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
                return ''
            else:
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

@app.route('/sensors/prediction/<s>',methods=['POST'])
def add_prediction(s):
    #aggiungi la previsione al database firestore
    s1 = s+'_prediction'
    data_prev = request.values['data_prev']
    prediction = float(request.values['prediction'])
    date_pred = {'date': data_prev, 'pred': prediction}
    db = firestore.Client.from_service_account_json('Credentials.json')
    doc_ref = db.collection('sensors').document(s1)
    entity_pred = doc_ref.get()
    documento_ref = db.collection('sensors').document(s1)
    documento = documento_ref.get()
    if entity_pred.exists and 'prediction' in entity_pred.to_dict():
        # se frigorigero_pred esiste e se ha una colonna prediction
        d_pred = entity_pred.to_dict()['prediction']
        valore_da_rimuovere = remove_dup('sensors', s1, 'prediction', data_prev)
        if valore_da_rimuovere != '' and valore_da_rimuovere in d_pred:
            d_pred.remove(valore_da_rimuovere)
        d_pred.append(date_pred)
        doc_ref.update({'prediction': d_pred})
    else:
        # se frigorigero_pred non esiste, aggiungi tutto
        print('Sono in SET')
        doc_ref.set({'prediction': [date_pred]})
        print('date_val in set: ', date_pred)
    return 'ok', 200

@app.route('/sensors/<s>',methods=['POST'])
def add_data(s):
    #aggiunta dei valori dei sensori nel database firestore
    date = request.values['date']
    val = float(request.values['val'])
    date_val = {'date': date, 'val': val}
    print('sono in add data date_val', date_val)
    db = firestore.Client.from_service_account_json('Credentials.json')
    doc_ref = db.collection('sensors').document(s)
    entity = doc_ref.get()
    documento_ref = db.collection('sensors').document(s)
    documento = documento_ref.get()
    if entity.exists and 'energia' in entity.to_dict():
        # se frigorigero esiste e se ha una colonna data
        # se esiste una data, me la sovrascrivi con l'ultimo valore
        d = entity.to_dict()['energia']
        valore_da_rimuovere = remove_dup('sensors', s, 'energia', date)
        if valore_da_rimuovere != '' and valore_da_rimuovere in d:
            d.remove(valore_da_rimuovere)
        d.append(date_val)
        doc_ref.update({'energia': d})
    else:
        #se frigorifero non esiste, aggiungimi tutto
        doc_ref.set({'energia':[date_val]})
    return 'ok',200

@app.route('/graph/<s>',methods=['GET','POST'])
@login_required
def graph_data(s):
    db = firestore.Client.from_service_account_json('Credentials.json')
    entity = db.collection('sensors').document(s).get()
    if entity.exists:
        # grafico consumi orari
        di = []
        di.append(['Number','Serie Storica'])
        #x la data
        #y i valori
        for x in entity.to_dict()['energia']:
            di.append([x['date'], x['val']])
            #new_entry = x['val']
            #new_date = x['date']
        #grafico delle fasce di consumo
        #F1 = 0
        #F2 = 0
        #F3 = 0
        date_fasce = []
        d1 = []
        d1.append(['Giorno', 'F1', 'F2', 'F3'])
        #giorno = ''
        for x in entity.to_dict()['energia']:
            giorno = x['date'].split(" ")[0]
            if giorno not in date_fasce:
                date_fasce.append(giorno)
        #giorno = ''
        for data_for in date_fasce:
            F1 = 0
            F2 = 0
            F3 = 0
            for x in entity.to_dict()['energia']:
                hour = int(x['date'].split(" ")[1].split(':')[0])
                day = datetime.datetime.strptime(x['date'], "%Y/%m/%d %H:%M:%S").strftime("%A").lower().strip()
                giorno = x['date'].split(" ")[0]
                if giorno == data_for:
                    if day != 'saturday' and day!= 'sunday':
                        if hour >= 8 and hour < 19:
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

        #Regressione lineare
        array_date = []
        consumi = []
        date_future = []
        m = 0
        for i in range(len(entity.to_dict()['energia'])):
            array_date.append(i)
            consumi.append(entity.to_dict()['energia'][i]['val'])
            m=i

        array_date = np.array(array_date).reshape(-1, 1)
        consumi = np.array(consumi)
        # Creazione del modello di regressione lineare
        modello = LinearRegression()
        # Addestramento del modello
        modello.fit(array_date, consumi)
        # Determina l'ultima data presente nel dataset
        ultimo_numero = m
        #ultima_data = entity.to_dict()['energia'][ultimo_numero]['date']
        # Genera una sequenza di date per le 4 ore successive
        numeri_futuri = np.arange(ultimo_numero+1, ultimo_numero+9).reshape(-1, 1)

        #calcolo delle 8 ore successive di cui prevedere il consumo
        def AggiungiOra(data):
            formato_data = "%Y/%m/%d %H:%M:%S"
            # Converti la stringa di data in un oggetto datetime
            data_datetime = datetime.datetime.strptime(data, formato_data)
            # Aggiungi un'ora all'oggetto datetime
            data_avanti = data_datetime + datetime.timedelta(hours=1)
            # Converti l'oggetto datetime risultante in una stringa nel formato desiderato
            data_avanti_stringa = data_avanti.strftime(formato_data)
            return data_avanti_stringa

        ora_attuale = entity.to_dict()['energia'][-1]['date']
        for i in range(7):
            prossima_ora = AggiungiOra(ora_attuale)
            date_future.append(prossima_ora)
            ora_attuale=prossima_ora
        date_future = np.array(date_future).reshape(-1,1)

        doc_ref = db.collection('sensors').document(s+'_prediction')
        entity_prediction = doc_ref.get()
        base_url = 'http://localhost'

        # Prevedi i consumi per le date future
        consumi_previsti = modello.predict(numeri_futuri)
        prima_previsione = consumi_previsti[0]
        r1 = post(f'{base_url}/sensors/prediction/{s}', data={'data_prev':date_future[0],'prediction': consumi_previsti[0]})

        # Stampa dei risultati
        for dat, consumo in zip(numeri_futuri, consumi_previsti):
            print(f"Data {dat}: {consumo}")

        #dati da passare all'html
        de = []
        dp = []
        ds = []
        dap = []
        dan = []
        de.append(['Data', 'Serie Storica'])
        dp.append(['Data', 'Previsione '])
        ds.append(['Data', 'Scostamento'])
        dap.append(['Data', 'Anomalia Negativa'])
        dan.append(['Data', 'Anomalia Positiva'])
        # x la data
        # y i valori

        for x in entity.to_dict()['energia']:
            de.append([x['date'], x['val']])
        if entity_prediction.exists:
            for x in entity_prediction.to_dict()['prediction']:
                dp.append([x['date'], x['pred']])
            for y in range(len(date_future)):
                if(y>0): #la prima previsione è considerata nel ciclo sopra
                    dp.append([date_future[y][0], consumi_previsti[y]])
            #calcolo dello scostamento e della media tra scostamenti aggiornata
            for x in entity.to_dict()['energia']:
                for y in entity_prediction.to_dict()['prediction']:
                    if (x['date']==str(y['date'])):
                        scost = x['val'] - y['pred']
                        ds.append([x['date'],scost])
            somma_scost = 0
            for i in ds:
                try:
                    if i[1] > 0:
                        somma_scost += i[1]
                    else:
                        somma_scost += ((i[1])*(-1))
                except:
                    print("Sono al primo giro, salto header")
            num_elem = len(ds)
            media = somma_scost / num_elem
            for i in ds:
                print(i)
                try:
                    if (i[1] < -media):
                        dap.append([i[0],i[1]])
                    if (i[1] > media):
                        dan.append([i[0], i[1]])
                except:
                    print("Sono al primo giro, salto header")
        return render_template('graph.html',sensor=s,data=json.dumps(di), data2=json.dumps(d1), data3=json.dumps(de), data4=json.dumps(dp), data5=json.dumps(ds), data6=json.dumps(dap), data7=json.dumps(dan))
    else:
        return redirect(url_for('static', filename='sensor404.html'))

@app.route('/login', methods=['POST'])
def login():
    #se utente già loggato
    if current_user.is_authenticated == True:
        return redirect('/static/gia_loggato.html')
    username = request.values['u']
    password = request.values['p']
    db = firestore.Client.from_service_account_json('Credentials.json')
    try:
      user_get = db.collection('utenti').document(username).get()
      user = db.collection('utenti').document(username)
    except:
        return redirect('/static/login_post_errore.html')
    #se password sbagliato o utente non esiste -> pagina di errore
    if user_get.exists and user_get.to_dict()['password']==password:
        login_user(User(username))
        if username == 'gaia':
            return redirect('/')
        else:
            return redirect('/')
    return redirect('/static/login_post_errore.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/elimina_utente', methods=['POST'])
def eliminautente():
    if current_user.username == 'gaia':
        username = request.values['u']
        db = firestore.Client.from_service_account_json('Credentials.json')
        user_get = db.collection('utenti').document(username).get()
        user = db.collection('utenti').document(username)
        #solo l'amministratore può eliminare un utente
        if user_get.exists:
            if username != 'gaia':
                user.delete()
            else:
                return redirect('/static/errore_eliminazione_utente.html')
            return redirect('/static/utente_eliminato.html')
        else:
            return redirect('/static/errore_eliminazione_utente.html')
    else:
        return redirect('/static/reserved_admin.html')

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

@app.route('/Contatti')
@login_required
def contatti():
    return redirect('/static/Contatti.html')

@app.route('/adduser', methods=['GET','POST'])
@login_required
def adduser():
    #solo l'amministratore può aggiungere o modificare un utente
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
                #modifica utente
                user.set({'username': username, 'password': password})
                return redirect('/static/utente_modificato.html')
            else:
                #aggiungi utente
                user.set({'username': username, 'password': password})
                return redirect('/static/utente_inserito.html')
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

mqtt_client.loop_stop()