'''from google.cloud import firestore

# Inizializza il client Firestore
db = firestore.Client()

# Specifica il percorso del documento e del campo desiderato
collezione = 'sensors'
documento_id = 'frigoriferoJZ'
campo = 'date_val'

# Recupera il documento e il valore del campo desiderato
documento_ref = db.collection(collezione).document(documento_id)
documento = documento_ref.get()

if documento.exists:
    valore = documento.get(campo)
    #indice = valore.get('date')
    if valore is not None:
        for i in valore:
            print(i['date'], i['val'])
            #print("Date: ", indice)
    else:
        print("Il campo non è presente nel documento.")
else:
    print("Il documento non esiste.")


from google.cloud import firestore

# Inizializza il client Firestore
db = firestore.Client()

# Specifica il percorso del documento e l'ID del documento
collezione = 'sensors'
documento_id = 'frigoriferoJZ'

# Specifica il campo da modificare
campo_da_modificare = 'date_val'

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
        print('campo: ', campo)
        print('campo da mod: ', campo_da_modificare)
        valore = documento.get(campo_da_modificare)
        print('valore: ', valore)
        for i in valore:
            if i['date'] == '2023/05/12 09:45:00':
                print('trovato')
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
            print('Non è stato eliminato nulla')
        else:
            print(f"Il valore '{valore_da_elim}' è stato eliminato con successo dal campo '{campo_da_modificare}'.")
    else:
        print(f"Il campo '{campo_da_modificare}' non è presente nel documento.")
else:
    print("Il documento non esiste.")'''


data_stringa = "23/10/2023 01:00:00"
data = datetime.datetime.strptime(data_stringa, "%d/%m/%Y %H:%M:%S")
giorno_settimana = data.strftime("%A")
print(giorno_settimana)