"""Baza danych

Skrypt umożliwiający stworzenie bazy danych. Utworzona baza danych odpowiada kalendarzowi wizyt lekarskich.
Baza danych została stworzona na cały rok 2022, wizyty są w dni poniedziałek-sobota i każdego dnia jest dostępnych 
21 terminów 15-minutowych wizyt z 5-minutową przerwą pomiędzy kolejnymi wizytami.

Do wyświetlania bazy danych stworzonej przy pomocy modułu sqlite3 można wykorzystać program DB Browser (SQ Lite).

Skrypt wymaga zaimportowania modułu sqlite3 oraz calendar. 

! Ten skrypt należy uruchomić jako pierwszy !
"""


import sqlite3 #umożliwia utowrzenie lokalnej bazy danych
import calendar #wykorzystany w celu usunięcia terminów będących niedzielami z kalendarza

cal = calendar.Calendar()

godzina_wizyty = []
for i in range(0, 7):
    godzina_wizyty.append("1{}:00 - 1{}:15".format(str(i), str(i)))
    godzina_wizyty.append("1{}:20 - 1{}:35".format(str(i), str(i)))
    godzina_wizyty.append("1{}:40 - 1{}:55".format(str(i), str(i)))

db = sqlite3.connect('baza_wizyt.db')
db.execute("PRAGMA foreign_keys = ON")
cur = db.cursor()

#utworzenie tabeli dostępnych terminów wizyt
cur.execute("DROP TABLE IF EXISTS visits;")
cur.execute("""CREATE TABLE IF NOT EXISTS visits (
        visit_id INTEGER PRIMARY KEY ASC, 
        date TEXT, 
        hour TEXT, 
        is_free INTEGER,
        patient_id INTEGER, 
        FOREIGN KEY (patient_id) REFERENCES patient (patient_id))""")

#utworzenie tabeli pacjentów 
cur.execute("DROP TABLE IF EXISTS patient;")
cur.execute("""CREATE TABLE IF NOT EXISTS patient (
        patient_id INTEGER PRIMARY KEY ASC,
        pesel TEXT,
        name TEXT,
        last_name TEXT)""")

i = 10
for month in range(1, 13):
    for day in cal.itermonthdays(2022, month):
        for godzina in godzina_wizyty:
            if(day != 0):
                if(calendar.weekday(2022, month, day) == 6):
                    continue
                elif(day in range(1, 10)):
                    if(month in range(1, 10)):
                        id_num = '{}{}2022{}'.format(day, month, i)
                        date = '0{}.0{}.2022'.format(day, month)
                    else:  
                        id_num = '{}{}2022{}'.format(day, month, i)
                        date = '0{}.{}.2022'.format(day, month)
                else:
                    if(month in range(1, 10)):
                        id_num = '{}{}2022{}'.format(day, month, i)
                        date = '{}.0{}.2022'.format(day, month)
                    else:
                        id_num = '{}{}2022{}'.format(day, month, i)
                        date = '{}.{}.2022'.format(day, month)
                dane = [date, godzina]
                cur.execute("INSERT INTO visits VALUES (NULL, ?, ?, 1, NULL)", dane)
            else:
                continue
            i += 1
        i = 10

db.commit()
cur.close()
db.close()