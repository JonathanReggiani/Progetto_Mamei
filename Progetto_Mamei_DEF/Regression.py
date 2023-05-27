import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Dati di esempio: consumi storici
anni = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
print(anni)
consumi = np.array([10, 12, 15, 18, 20, 22, 25, 28, 30, 32, 35, 38])

# Trasformazione dei dati in un formato adatto per la regressione
anni = anni.reshape(-1, 1) # Trasforma il vettore degli anni in una matrice colonna
print(anni)
# Creazione del modello di regressione lineare
modello = LinearRegression()

# Addestramento del modello
modello.fit(anni, consumi)

# Generazione dei valori futuri
anni_futuri = np.array([2022, 2023, 2024, 2025]).reshape(-1, 1)# Anni futuri per i quali si desidera fare la previsione
consumi_previsti = modello.predict(anni_futuri)

# Stampa dei risultati
print("Consumi previsti:")
for anno, consumo in zip(anni_futuri.flatten(), consumi_previsti):
    print(f"Anno {anno}: {round(consumo, 2)}")

# Plot dei risultati
plt.scatter(anni, consumi, color='blue', label='Dati storici')
plt.plot(anni_futuri, consumi_previsti, color='red', label='Previsione')
plt.xlabel('Anno')
plt.ylabel('Consumi')
plt.title('Previsione dei consumi futuri')
plt.legend()
plt.show()