import datetime

data = "2023/05/25 15:30:00"
formato_data = "%Y/%m/%d %H:%M:%S"


# Converti la stringa di data in un oggetto datetime
data_datetime = datetime.datetime.strptime(data, formato_data)

# Aggiungi un'ora all'oggetto datetime
data_avanti = data_datetime + datetime.timedelta(hours=1)

# Converti l'oggetto datetime risultante in una stringa nel formato desiderato
data_avanti_stringa = data_avanti.strftime(formato_data)

print(data_avanti_stringa)
# Stampa la nuova stringa di data