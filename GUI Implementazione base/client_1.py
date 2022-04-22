import sys
from tkinter import *
from socket import *
import _thread
import ast
from Crypto.Cipher import AES
from generate_keys import *
from generate_prime import *

# scelgo se leggere i messaggi in chiaro o cifrati
global mode
if sys.argv[1] == "plain":
    mode = "plain"
elif sys.argv[1] == "ciphered":
    mode = "ciphered"
else:
    print("Mode must be 'plain' or 'ciphered'. Exiting")
    exit(0)
    
# generazione chiave condivisa
def gen_message_key():
    global message_key
    global ep_secret_key
    global lt_secret_key
    shk1 = shared_key(lt_pub_key_other_client, ep_secret_key, p)
    shk2 = shared_key(ep_pub_key_other_client, ep_secret_key, p)
    shk3 = shared_key(ep_pub_key_other_client, lt_secret_key, p)    
    message_key = KDF(shk1, shk2, shk3)

# aggiornamento della finestra della chat
def update_chat(msg, state):
    global chatlog
    chatlog.config(state=NORMAL)
    # aggiornamento del messaggio
    if state==0:
        chatlog.insert(END, f'Tu: ' + msg.rstrip("\n") + "\n")
    else:
        chatlog.insert(END, f'{other_name}: ' + msg.rstrip("\n") + "\n")
    chatlog.config(state=DISABLED)
    # mostra gli ultimi messaggi
    chatlog.yview(END)

# funzione per l'invio dei messaggi
def send():    
    # creazione del pacchetto msg: [msg_cifrato, nonce]
    global textbox
    # prendo il messaggio
    msg = textbox.get("0.0", END)
    # prendo la chiave condivisa
    cipher = AES.new(message_key, AES.MODE_EAX)
    # aggiungo il nonce
    nonce = cipher.nonce
    # cifro il messaggio
    ciphertext = cipher.encrypt(str(msg).encode('utf-8'))
    c_msg = []
    c_msg.append(ciphertext)
    c_msg.append(nonce)
    # aggiorno la finestra
    if mode == "ciphered": # voglio vedere i messaggi cifrati
        update_chat(str(c_msg[0]), 0)
    else: # voglio vedere i messaggi in chiaro
        update_chat(str(msg).rstrip("\n"), 0) 
    # invio il messaggio
    client.send(str(c_msg).encode('utf-8'))
    textbox.delete("0.0", END)

    
# funzione per la ricezione dei messaggi
def receive():
# Ricezione del mesaggio cifrato dall'altro client con relativa decifratura e stampa
    while 1:
        # ricevo il messaggio
        msg_pack = ast.literal_eval(client.recv(1024).decode('utf-8'))	          
        nonce = msg_pack[1]
        cipher = AES.new(message_key, AES.MODE_EAX, nonce)
        # lo decifro
        msg = cipher.decrypt(msg_pack[0]).decode('utf-8')
        if mode == "ciphered":  # voglio vedere i messaggi cifrati
            update_chat(str(msg_pack[0]), 1)
        else: # voglio vedere i messaggi in chiaro
            update_chat(msg, 1)

def press(event):
    send()

# Generazione GUI
def GUI(name):
    global chatlog
    global textbox
    
    gui = Tk()
    # titolo
    gui.title(f"Chat dal punto di vista di {name} ({mode})")
    # grandezza finestra
    gui.geometry("800x860")

    # spazio per il testo
    chatlog = Text(gui, bg='white')
    chatlog.config(state=DISABLED)

    # tasto invio
    sendbutton = Button(gui, bg='grey', fg='black', text='INVIA', command=send, relief="raised")

    # casella scrittura messaggio
    textbox = Text(gui, bg='white')
    
    chatlog.place(x=6, y=6, height=750, width=700)
    textbox.place(x=6, y=750, height=40, width=700)
    sendbutton.place(x=720, y=750, height=40, width=50)
    
    # ENTER = invia
    textbox.bind("<KeyRelease-Return>", press)

    # inizio il thread per la ricezione dei messaggi
    _thread.start_new_thread(receive, ())

    # mando in loop la finestra
    gui.mainloop()

chatlog = textbox = None
# inizializzo socket
s = socket(AF_INET, SOCK_STREAM)
host = 'localhost' # 127.0.0.1, teoricamente è possibile il collegamento fra due dispositivi sulla stessa rete
port = 8080
# inizializzo server
s.bind((host, port))
s.listen(1)
client, addr = s.accept()
# inserisco nickname
my_name = input("Insert your nickname: ")
# invio nickname all'altro client
client.sendall(my_name.encode('utf-8'))
# ricevo il nickname dell'altro client
other_name = client.recv(1024).decode('utf-8')
global names
names = [my_name,other_name]
# mando p e g all'altro client
p_bit_length = 16
p = prime_generator(p_bit_length)
g = find_group_generators(p,1)[0]
p_g = str([p,g])
client.sendall(p_g.encode('utf-8'))
# genero le mie chiavi
lt_public_key, lt_secret_key = pub_priv_keys(p, g, 16)
ep_public_key, ep_secret_key = pub_priv_keys(p, g, 16)
public_keys = [lt_public_key,ep_public_key]
# ricevo le chiavi dell'altro client
his_keys = ast.literal_eval(client.recv(1024).decode('utf-8'))
lt_pub_key_other_client = his_keys[0]
ep_pub_key_other_client = his_keys[1]
# mando all'altro client le mie chiavi
client.sendall(str(public_keys).encode('utf-8'))
# genero la chiave condivisa
gen_message_key()
GUI(my_name)
