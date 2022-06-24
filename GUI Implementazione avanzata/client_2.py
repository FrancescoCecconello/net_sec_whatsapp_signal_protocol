import sys
from tkinter import *
import tkinter as tk
from socket import *
import _thread
import ast
from datetime import datetime
from Crypto.Cipher import AES
from generate_keys import *
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

# scelgo se leggere i messaggi in chiaro o cifrati
global mode
if len(sys.argv) != 1:    
    if sys.argv[1] == "plain":
        mode = "plain"
        print("Mostrerò il testo delle chat in chiaro.")
    elif sys.argv[1] == "ciphered":
        mode = "ciphered"
        print("Mostrerò il testo delle chat criptato.")
    else:
        print(f"La modalità deve essere 'plain' o 'ciphered', non {sys.argv[1]}.")
        exit(0)
else:
    print("Mostrerò il testo delle chat in chiaro.")
    mode = "plain"

def gen_message_key():
    global message_key
    global ep_secret_key
    global lt_secret_key
    shk1 = lt_x_secret_key.exchange(ep_pub_key_other_client)
    shk2 = ep_secret_key.exchange(ep_pub_key_other_client)
    shk3 = ep_secret_key.exchange(lt_pub_key_other_client)
    message_key = concat_KDF(shk1, shk2, shk3)    

# aggiornamento della finestra della chat
def update_chat(msg, state):
    global chatlog
    if state == 0:
        msg = fix_text(str(msg).rstrip("\n"),"right")+ "\n"
    else:
        msg = fix_text(str(msg).rstrip("\n"))+ "\n"
    chatlog.config(state=NORMAL)
    # aggiornamento del messaggio
    current_time = datetime.now().strftime("%H:%M")
    if msg != "":
        if state==0:            
            chatlog.insert(END,current_time + " "*(chars_per_line + 8) + "\n","my_time")
            chatlog.insert(END, msg +"\n","me")
        else:
            chatlog.insert(END, current_time + "\n","other_time")
            chatlog.insert(END,msg +"\n","other")
            
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
        update_chat(str(c_msg[0])+"\n", 0)
    else: # voglio vedere i messaggi in chiaro
        update_chat(msg, 0)
    # invio il messaggio
    client.send(str(c_msg).encode('utf-8'))
    textbox.delete("0.0", END)

    
# funzione per la ricezione dei messaggi
def receive():
# Ricezione del mesaggio cifrato dall'altro client con relativa decifratura e stampa
    while 1:
        # ricevo il messaggio        
        try:
            msg_pack = ast.literal_eval(client.recv(8192).decode('utf-8'))	          
        except:
            print("Chat terminata dall'altro client.")
            exit(0)
        nonce = msg_pack[1]
        cipher = AES.new(message_key, AES.MODE_EAX, nonce)
        # lo decifro
        msg = cipher.decrypt(msg_pack[0])
        if mode == "ciphered": # voglio vedere i messaggi cifrati
            update_chat(str(msg_pack[0]) +"\n", 1)
        else: # voglio vedere i messaggi in chiaro
            update_chat(str(msg,'utf-8') + "\n", 1)
            
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
    chatlog = tk.Text(gui, bg='white')
    chatlog.config(state=DISABLED)
    chatlog.pack()
    chatlog.tag_config('me',foreground="green",justify='right',font="Consolas 10 bold")
    chatlog.tag_config('other', foreground="royalblue",font="Consolas 10 bold")
    chatlog.tag_config('my_time', foreground="green",justify='right',font="Consolas 7 bold")
    chatlog.tag_config('other_time', foreground="royalblue",justify='left',font="Consolas 7 bold")
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

def fix_text(msg,alignment="left"):
    f = ""
    for i in range(len(msg)):
        if i%chars_per_line == 0:
            if i!= 0:
                f += "\n"
            f += msg[i]
        else:
            f += msg[i]
    if alignment == "right":
        return pad(f)
    return f

def pad(txt):
    t = txt.split("\n")
    t[-1] = t[-1] + " "*(chars_per_line-len(t[-1]))
    return "\n".join(t)
    
chatlog = textbox = None
# inizializzo socket
client = socket(AF_INET, SOCK_STREAM)
host = 'localhost'  # 127.0.0.1, teoricamente è possibile il collegamento fra due dispositivi sulla stessa rete
port = 8080
# inizializzo client
client.connect((host, port))
# inserisco nickname
my_name = input("Inserisci il tuo nome: ")
# ricevo il nickname dell'altro client
other_name = client.recv(8192).decode('utf-8')
global names
names = [my_name,other_name]
# invio nickname all'altro client
client.sendall(my_name.encode('utf-8'))

# ricevo il pacchetto di chiavi dall'altro client
key_pack = ast.literal_eval(client.recv(8192).decode('utf-8'))
global lt_pub_key_other_client
global ep_pub_key_other_client

# Ricostruisco la chiave pubblica long term dell'altro client dai byte (X25519)
lt_pub_key_other_client = x25519.X25519PublicKey.from_public_bytes(key_pack[0])

# Ricostruisco la chiave pubblica effimera dell'altro client dai byte (X25519)
ep_pub_key_other_client = x25519.X25519PublicKey.from_public_bytes(key_pack[1])

# Ricostruisco la chiave pubblica firmata dell'altro client (Ed25519)
signed_pub_key_other_client = ed25519.Ed25519PublicKey.from_public_bytes(key_pack[2])

# Prendo la firma
signature = key_pack[3]

try:
    # Controllo la validità della firma
    signed_pub_key_other_client.verify(signature,b'auth')
except InvalidSignature:
    print('Non è possibile certificare l\'identità del client. La chat verrà terminata.')
    sys.exit(0)

public_keys = []    
# Creo una chiave long term segreta di tipo Ed25519 per consentire la firma digitale e l'autenticazione
lt_ed_secret_key = Ed25519PrivateKey.generate()

# Calcolo la corrispondente chiave pubblica (sempre di tipo Ed25519)
lt_ed_public_key = lt_ed_secret_key.public_key()

# Converto le chiavi in byte
ed_secret_bytes =lt_ed_secret_key.private_bytes(encoding=serialization.Encoding.Raw,format=serialization.PrivateFormat.Raw,encryption_algorithm=serialization.NoEncryption())	
ed_public_bytes = lt_ed_public_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)

# Genero la stessa chiave segreta long term, ma stavolta di tipo X25519 per consentire il calcolo delle shared key
lt_x_secret_key = x25519.X25519PrivateKey.from_private_bytes(ed_secret_bytes)

# Calcolo la corrispondente chiave pubblica
lt_x_public_key = lt_x_secret_key.public_key()
public_bytes = lt_x_public_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)

# Dato che non posso inviare direttamente le chiavi tramite i socket, invio all'altro client i byte dalle quali ricavarle
public_keys.append(public_bytes)

# Creo la chiave effimera segreta
ep_secret_key = X25519PrivateKey.generate()

# Calcolo la chiave effimera pubblica e invio all'altro client i byte per ricavarla
ep_secret_bytes = ep_secret_key.private_bytes(encoding=serialization.Encoding.Raw,format=serialization.PrivateFormat.Raw,encryption_algorithm=serialization.NoEncryption())
ep_public_key = ep_secret_key.public_key()
ep_public_bytes = ep_public_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
public_keys.append(ep_public_bytes)	# aggiungo quelle pubbliche a quelle da mandare all'altro client

# Genero la firma per la chiave segreta long term. b'auth' è il messaggio che deve controllare il verificatore per certificare la mia identità all'altro client
signature = lt_ed_secret_key.sign(b'auth')

# Invio i byte per calcolare la chiave pubblica di tipo Ed25519
public_keys.append(ed_public_bytes)

# Invio la firma
public_keys.append(signature)

# Invio tutto
client.sendall(str(public_keys).encode('utf-8')) 

gen_message_key()
del ep_secret_key
chars_per_line = 40
GUI(my_name)
