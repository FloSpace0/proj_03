import pandas as pd

#LEGGERE UN DATA FRAME
df = pd.read_csv("Cost_of_Living_Index_2022.csv", encoding="utf-8") #data frame
#LEGGERE UN DATA FRAME
#df2 = pd.read_csv("job_descriptions.csv", encoding="utf-8") #data frame

#STAMPARE le PRIME 5 RIGHE
print(df.head())

#PRENDERE UN SOLO dato FACENDO un INTERSEZIONE
italy_cost = df.loc[df['Country'] == 'Italy', 'Cost of Living Index'].values[0] #values lo trasforma solo prendendo il valore
print(italy_cost)

#PRENDE TUTTE LE INFORMAZIONI da una SOLA RIGA o COLONNA
romania_info = df.loc[df['Country'] == 'Romania']
print(romania_info)

#PRENDE FACENDO UN ORDINE I PRIMI 5 
top5 = df.sort_values("Cost of Living Index", ascending=False).head(5)
print(top5[["Country", "Cost of Living Index"]])

#PRENDE SOLO 1, IL PIÙ BASSO IN QUALCOSA
min_grocery = df.loc[df["Groceries Index"].idxmin()]
print(min_grocery[["Country", "Groceries Index"]])



# SECONDO DF

# Ottenere le prime 5 offerte di lavoro dall'Italia
#italy_jobs = df2.loc[df2['Country'] == 'USA', ['Country', 'Salary Range', 'location']].head(100)
#print(italy_jobs)
 
