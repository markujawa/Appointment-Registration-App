"""Serwer

Skrypt umożliwiający utworzenie gniazda strumienia w domenie internetowej (TCP) i uruchomienie 
serwera w terminalu. Aby serwer zadziałał musi zostać stworzona baza danych - przed uruchomieniem skryptu
należy uruchomić skrypt database.py.Skrypt należy uruchomić przed uruchomieniem skryptu client.py.

Skrypt umożliwia połączenie klienta z serwerem. Uruchomiony serwer nasłuchuje i czeka na
połączenie ze strony klienta.

Skrypt wymaga zaimportowania modułów sqlite3, socket i threading. 

Skrypt zawiera następujące funkcje:
	* validate_date(date) - funkcja sprawdzająca, czy wpisany format daty jest prawidłowy
  * send_client(client, msg) - funkcja umożliwiająca zakodowanie (w formacie utf-8) i wysłanie 
  														 wiadomości do klienta  				
  * get_data_and_set_visit(client) - funkcja pobierająca dane od pacjenta i umożliwiająca zapis na wizytę
  * handle_client(client, addr) - funkcja obsługująca połączenie z klientem 
  * start() - funkcja rozpoczynająca działanie serwera
  * main() - główna funkcja programu 
"""

import sqlite3 #moduł umożliwiający tworzenie i "obsługiwanie" bazy danych
import socket
from sqlite3.dbapi2 import DatabaseError
import threading #moduł umożliwiający tworzenie wątków

class Error(Exception):
    """Klasa błędu"""
    
    pass

class EmptyInputException(Error):
    """Klasa wyjątku mówiąca o tym, że został wprowadzony "pusty" input"""
    
    pass

class WrongInputException(Error):
    """Klasa wyjątku, mówiąca o tym, że zostały wprowdzone dane błędne, bądź w złym formacie"""
    
    pass

#stałe przyjmowane w programie
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
CONNECT_MSG = "[!CONNECTED!]"
DISCONNECT_MSG = "[!DISCONNECTED!]"
ERROR_MSG = "*" * 28 + "\n! Błędny zapis !\nWprowadź dane ponownie\n" + "*" * 28
EMPTY_MSG = "[!EMPTY INPUT!]"

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# To pozwala na "zablokowanie" fragmentu kodu i zatrzymanie wykonywania programu aż do momentu,
#gdy jeden użytkownik się zapisze na konkretny termin wizyty, zabezpiecza przed nadpisaniem terminu/zapisanie 
#się na ten sam termin przez następnego klienta
thread_lock = threading.Lock() 

def validate_date(date):
    """Sprawdź poprawność formatu daty wpisanej przez użytkownika

    Parameters
    -----------
    date : string
        Data podana przez użytkownika

    Returns
    -------
    boolean
        Poprawność daty wyrażona za pomocą wartości True/False
    """
    allowed = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
    for symbol in date:
        if not symbol in allowed:
            return False
    if len(date) != 10:
        return False
    elif date[2] != '.' or date[5] != '.':
        return False
    else:
        return True


def send_client(client, msg):
    """Zakoduj i wyślij wiadomość do klienta (w formacie utf-8)

    Parameters
    ---------
    client : socket object
        Gniazdo strumienia klienta
    msg : str
        Treść wiadomości, która ma zostać zakodowana i wysłana

    """
    message = msg.encode(FORMAT)
    client.send(message)


def get_data_and_set_visit(client):
    """Pobierz dane od pacjenta i zapisz na wizytę/wizyty

    Parameters
    -----------
    client : socket object
        Gniazdo strumienia klienta
    """
    print("[APP IS RUNNING...]")
    db = sqlite3.connect('baza_wizyt.db')
    cur = db.cursor()
    patient_data = []
    try:
        while True:
            send_client(client, "[I]PODAJ SWÓJ PESEL: ")
            pesel = client.recv(1024).decode(FORMAT)
            pesel_existance = cur.execute("SELECT patient_id FROM patient WHERE pesel = ?", (pesel, )).fetchone()
            existing = False
            try:
                if pesel == EMPTY_MSG:
                    raise EmptyInputException
                elif len(pesel) != 11 or pesel.isdigit() == False:
                    raise WrongInputException
                elif pesel_existance is not None:
                    send_client(client, "\n*** Twój PESEL jest już w naszej bazie danych! ***\n")
                    existing = True
                    break
                else:
                    break
            except WrongInputException:
                print("[EXCEPTION] -> WrongInputException")
                send_client(client, ERROR_MSG)
            except EmptyInputException:
                print("[EXCEPTION] -> EmptyInputException")
                send_client(client, ERROR_MSG)
        
        if existing == False:
            patient_data.append(pesel)
            print("[PESEL]: {}".format(pesel))

            while True:
                send_client(client, "[I]PODAJ SWOJE IMIĘ: ")
                name = client.recv(1024).decode(FORMAT)
                try:
                    if name == EMPTY_MSG:
                        raise EmptyInputException
                    elif name.isalpha() == False:
                        raise WrongInputException
                    else:
                        break
                except EmptyInputException:
                    print("[EXCEPTION] -> EmptyInputException")
                    send_client(client, ERROR_MSG)
                except WrongInputException:
                    print("[EXCEPTION] -> WrongInputException")
                    send_client(client, ERROR_MSG)
                
            patient_data.append(name)
            print("[NAME]: {}".format(name))

            while True:
                send_client(client, "[I]PODAJ SWOJE NAZWISKO: ")
                last_name = client.recv(1024).decode(FORMAT)
                try:
                    if last_name == EMPTY_MSG:
                        raise EmptyInputException
                    elif last_name.isalpha() == False:
                        raise WrongInputException
                    else:
                        break
                except EmptyInputException:
                    print("[EXCEPTION] -> EmptyInputException")
                    send_client(client, ERROR_MSG)
                except WrongInputException:
                    print("[EXCEPTION] -> WrongInputException")
                    send_client(client, ERROR_MSG)

            patient_data.append(last_name)
            print("[LAST_NAME]: {}".format(last_name))
            print("[NEW PATIENT DATA]: " + str(patient_data))

            cur.execute("INSERT INTO patient VALUES (NULL, ?, ?, ?)", patient_data)
            patient_id = cur.lastrowid
            db.commit()
            print("[!DATA ABOUT PATIENT SAVED SUCCESSFULLY!]")
            send_client(client, "\n*** Twoje dane zostały pomyślnie zapisane! Dziękuję! ***\n")
          
        else:
            cur.execute("SELECT patient_id FROM patient WHERE pesel = ?", (pesel,))
            patient = cur.execute("SELECT patient_id FROM patient WHERE pesel = ?", (pesel,)).fetchone()
            patient_id = int(patient[0])

        while True:
            if thread_lock.locked():
                    send_client(client, "\n*** Wczytywanie... Proszę czekać ... ***\n")
            thread_lock.acquire()
            while True:
                send_client(client, "[I]PODAJ DATĘ WIZYTY, NA KTÓRĄ CHCESZ SIĘ ZAPISAĆ (np. 08.08.2022): ")
                date = client.recv(1024).decode(FORMAT)
                date_existance = cur.execute("SELECT visit_id FROM visits WHERE date = ?", (date, )).fetchone()
                availability = cur.execute("SELECT is_free FROM visits WHERE date = ?", (date, )).fetchall()
                try:
                    if date == EMPTY_MSG:
                        raise EmptyInputException
                    elif validate_date(date) == False:
                        raise WrongInputException
                    elif date_existance is None:
                        send_client(client, """*** Błędny zapis! Sprawdź, czy wybrany dzień nie jest niedzielą albo czy podana data znajduje się\n 
                                            znajduje się w roku! ***""")
                    elif (1,) not in availability:
                        send_client(client, "*** Wszystkie terminy w tym dniu są już zajęte! Wybierz inny termin! ***")
                    else:
                        break
                except WrongInputException:
                        print("[EXCEPTION] -> WrongInputException")
                        send_client(client, ERROR_MSG)
                except EmptyInputException:
                    print("[EXCEPTION] -> EmptyInputException")
                    send_client(client, ERROR_MSG)

            print("[DATE]: {}".format(date))
            
            send_client(client, "\nOTO TERMINY WIZYT W TYM DNIU WRAZ Z ICH DOSTĘPNOŚCIĄ:")
            rows = cur.execute("SELECT visit_id, hour, is_free FROM visits WHERE date = ?", (date,)).fetchall()
            i = 1
            x = 5
            for row in rows:
                if row[2] == 1:
                    send_client(client, "\n({}):{} {}   TERMIN DOSTĘPNY".format(str(i), " " * x, row[1]))
                    print(row)
                else:
                    send_client(client, "\n({}):{} {}   TERMIN NIEDOSTĘPNY".format(str(i), " " * x, row[1]))
                    print(row)

                i += 1
                if i > 9:
                    x = 4 

            print("\n\n")

            while True:
                print("[PICKING A VISIT HOUR]")
                send_client(client, "[I]\nWPISZ NR WIZYTY, NA KTÓRĄ CHCESZ SIĘ ZAPISAĆ:")
                number = client.recv(1024).decode(FORMAT)
                try:
                    if number == EMPTY_MSG:
                        raise EmptyInputException
                    elif number.isdigit() == False:
                        raise WrongInputException
                    int_number = int(number)
                    if int_number not in range(1,22):
                        raise WrongInputException
                    elif rows[int_number-1][2] == 0:
                        send_client(client, "\n*** Ten termin jest NIEDOSTĘPNY! Wybierz inny termin! ***\n")
                    else:
                        break

                except EmptyInputException:
                    print("[EXCEPTION] -> EmptyInputException")
                    send_client(client, ERROR_MSG)
                except WrongInputException:
                    print("[EXCEPTION] -> WrongInputException")
                    send_client(client, ERROR_MSG)

            visit_id = rows[int_number-1][0]
            cur.execute("UPDATE visits SET is_free = ?, patient_id = ? WHERE visit_id = ?", (0, patient_id, visit_id,))
            db.commit()
            send_client(client, "*** Pomyślnie zapisano na wizytę ***")
            
            thread_lock.release()

            visit_data = cur.execute("SELECT date, hour FROM visits WHERE visit_id = ?", (visit_id, )).fetchall()
            send_client(client, "DATA WIZYTY:     {}\nGODZINA WIZYTY:  {}\n".format(visit_data[0][0], visit_data[0][1]))
            print(visit_data)
            send_client(client, "[I]*** Czy chcesz umówić kolejną wizytę? (1 - TAK / 0 - NIE) ***")
            answer = client.recv(1024).decode(FORMAT)
            
            if answer != '1':
                cur.close()
                db.close()
                break
                
        send_client(client, DISCONNECT_MSG)
        
    except DatabaseError:
        print("[!DATABASE NOT FOUND!]")
        send_client(client, "\n*** Zapisanie Twoich danych nie powiodło się! ***\n")
        send_client(client, DISCONNECT_MSG)

def handle_client(client, addr):
    """Obsłuż połączenie z klientem

    Parameters
    ----------
    client : socket objects
        Gniazdo strumienia klienta
    addr : address info
        Informacja o adresie
    """
    
    print("[NEW CONNECTION] {} połączył się z serwerem".format(addr))
    try:
        connected = True
        while connected:
            msg = client.recv(1024).decode(FORMAT) 
                      
            if not msg:
                break
            elif msg == DISCONNECT_MSG:
                print("[{}] {}".format(addr, msg))
                connected = False
            elif msg == CONNECT_MSG:
                send_client(client, "*** WITAMY W KALENDARZU ZAPISÓW NA WIZYTY LEKARSKIE! ***\n")
                get_data_and_set_visit(client)
    finally:
        client.close()

def start():
    """Rozpocznij działanie serwera"""
    
    server.listen()
    print("[LISTENING] server is listening on {}".format(SERVER))
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target = handle_client, args = (client, addr))
        thread.start()
        print("[ACTIVE CONNECTIONS]  ->  {}".format(threading.active_count()-1))

def main():
    """Główna funkcja programu"""
    
    print("[STARTING] server is starting...")
    start()

main()