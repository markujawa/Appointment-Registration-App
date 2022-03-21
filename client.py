"""Client

Skrypt umożliwiający utworzenie gniazda strumienia w domenie internetowej (TCP) i uruchomienie 
klienta w terminalu (po wcześniejszym uruchomieniu serwera w terminalu) i połączenie się z serwerem, 
dzięki czemu możliwa jest wymiana informacji z serwerem. 

Skrypt wymaga zaimportowania modułu socket.

Skrypt zawiera następujące funkcje:
	* send(msg) - koduje wiadomość, a następnie wysyła ją do serwera
    * message exchange() - umożliwia wymianę wiadomości między klientem a serwerem 
    * main() - główna funkcja skryptu
"""

import socket

#stałe przyjmowane w programie 
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
CONNECT_MSG = "[!CONNECTED!]"
DISCONNECT_MSG = "[!DISCONNECTED!]"
ERROR_MSG = "*" * 28 + "\n! Błędny zapis !\nWprowadź dane ponownie\n" + "*" * 28
EMPTY_MSG = "[!EMPTY INPUT!]"

#socket.gethostbyname - zwraca adres IP hosta
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

#socket.AF_INET - address family 
#socket.SOCK_STREAM - TCP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

x = True

def send(msg):
    """Zakoduj wiadomość w formacie utf-8 i prześli ją do serwera
    
    Parameters
    ----------
    msg : str
    	Treść wiadomości, która ma zostać zakodowana i wysłana
      
    """
      
    message = msg.encode(FORMAT)
    client.send(message)

def message_exchange():
    """Uruchom się po połączeniu klienta z serwerem i pozwól na odczytanie i wysłanie 
    zakodowanych (w formatcie utf-8) wiadomości między klientem a serwerem"""

    message = client.recv(2048).decode(FORMAT)
    if message[0:3] == '[I]':
        print(message[3:])
        data = input()
        if data:
            send(data)
        else:
            send(EMPTY_MSG)
    elif message == ERROR_MSG:
        print(message)
    elif message == DISCONNECT_MSG:
        global x  	#zmienna przechowująca informację o tym, czy połączenie z serwerem 
        			#ma zostać zachowane
        x = False
        send(DISCONNECT_MSG)
    else:
        print(message)

def main():
    """Główna funkcja skryptu"""

    send(CONNECT_MSG)
    while True:
        message_exchange()
        if x == False:
            break
          
main()

