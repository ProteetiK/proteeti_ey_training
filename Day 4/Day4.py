import pandas as pd
import sqlite3
conn_challenge = sqlite3.connect(':memory:')
cursor = conn_challenge.cursor()

challenge_data = {
    "Visit_Id": [5001, 5001, 5002, 5003],
    "Student_Id": [101, 101, 102, 104],
    "Student_Name": ['Alice', 'Alice', 'Bob', 'David'],
    "Doctor_Id": ['DOC_XYZ', 'DOZ_XYZ', 'DOC_ABC', 'DOC_XYZ'],
    "Doctor_Name": ['Dr. Evans', 'Dr. Evans', 'Dr. Green', 'Dr. Evans'],
    "Doctor_clinic": ['General', 'General', 'Sports', 'General'],
    "Prescriptions": ['Amoxicilin Ibuprofen', 'Amoxicilin Ibuprofen', 'Bandages', 'Vitamin D']
}

df_challenge = pd.DataFrame(challenge_data)
df_challenge.to_sql('Patient_Visits_0NF', conn_challenge, index=False, if_exists='replace')
print('0NF: ')
df_challenge

#1. Why does table defy 1NF and which column?
#Ans. Prescriptions is violating the Atomic clause

#2. If Visit_Id is primary key of flattened table, why do Student Name and Doctor Clinic violate 2NF and 3NF
#Student name depends on Student Id and Doctor Clinic depends on Doctor Id and those two together are not the primary key so it violates 3NF

#3. If knowing Doctor Id immediately tells you which is the clinic but Doctor ID is not the primary key, which NF does it violate?
#2NF

#4. Fix table to 1NF with code
df_challenge = df_challenge.assign(Prescriptions = df_challenge['Prescriptions'].str.split(' ')).explode('Prescriptions')
df_challenge