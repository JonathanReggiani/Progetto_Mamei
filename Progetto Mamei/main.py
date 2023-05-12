import pandas as pd

#lettura file excel
df = pd.read_excel("Consumo di Energia.xls", skiprows=[0], header=None)
print(df)
'''dict = df.to_dict()
print(dict)'''

df1 = pd.read_excel("Potenza.xls", skiprows=[0], header=None)
df2 = df1.replace('/',0)
print(df2)
