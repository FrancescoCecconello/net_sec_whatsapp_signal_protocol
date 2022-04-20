import sys
from tkinter import *
from socket import *
import _thread
import ast
from Crypto.Cipher import AES
from generate_keys import *
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

global mode
if sys.argv[1] == "plain":
    mode = "plain"
elif sys.argv[1] == "ciphered":
    mode = "ciphered"
else:
    print("Mode must be 'plain' or 'chipered'. Exiting")
    exit(0)

def gen_message_key():
    global message_key
    global ep_secret_key
    global lt_secret_key
    shk1 = lt_x_secret_key.exchange(ep_pub_key_other_client)
    shk2 = ep_secret_key.exchange(ep_pub_key_other_client)
    shk3 = ep_secret_key.exchange(lt_pub_key_other_client)
    message_key = concat_KDF(shk1, shk2, shk3)
    

# update the chat log
def update_chat(msg, state):
    global chatlog

    chatlog.config(state=NORMAL)
    # update the message in the window
    if state==0:
        chatlog.insert(END, f'YOU: ' + str(msg))
    else:
        chatlog.insert(END, f'{other_name}: ' + str(msg))
    chatlog.config(state=DISABLED)
    # show the latest messages
    chatlog.yview(END)

# function to send message
def send():    
    # creazione del pacchetto msg: [msg_cifrato, nonce]
    global textbox
    # get the message
    msg = textbox.get("0.0", END)
    cipher = AES.new(message_key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext = cipher.encrypt(str(msg).encode('utf-8'))
    c_msg = []
    c_msg.append(ciphertext)
    c_msg.append(nonce)
    # update the chatlog
    if mode == "ciphered":
        update_chat(str(c_msg[0])+"\n", 0)
    else:
        update_chat(msg, 0)
    # send the message
    client.send(str(c_msg).encode('utf-8'))
    textbox.delete("0.0", END)

    
# function to receive message
def receive():
# Ricezione del mesaggio cifrato dall'altro client con relativa decifratura e stampa
    while 1:
        msg_pack = ast.literal_eval(client.recv(1024).decode('utf-8'))              
        nonce = msg_pack[1]
        cipher = AES.new(message_key, AES.MODE_EAX, nonce)
        msg = cipher.decrypt(msg_pack[0])
        if mode == "ciphered":
            update_chat(str(msg_pack[0]) +"\n", 1)
        else:
            update_chat(str(msg,'utf-8'), 1)
            
def press(event):
    send()

# GUI function
def GUI(name):
    global chatlog
    global textbox

    # initialize tkinter object
    gui = Tk()
    # set title for the window
    gui.title(f"{name}'s point of view ({mode})")
    # set size for the window
    gui.geometry("760x860")

    # text space to display messages
    chatlog = Text(gui, bg='white')
    chatlog.config(state=DISABLED)

    # button to send messages
    sendbutton = Button(gui, bg='orange', fg='black', text='SEND', command=send)

    # textbox to type messages
    textbox = Text(gui, bg='white')

    # place the components in the window
    chatlog.place(x=6, y=6, height=750, width=700)
    textbox.place(x=6, y=750, height=40, width=700)
    sendbutton.place(x=720, y=750, height=40, width=50)
    
    # bind textbox to use ENTER Key
    textbox.bind("<KeyRelease-Return>", press)

    # create thread to capture messages continuously
    _thread.start_new_thread(receive, ())

    # to keep the window in loop
    gui.mainloop()


chatlog = textbox = None
# initialize socket
client = socket(AF_INET, SOCK_STREAM)
# config details of server
host = 'localhost'  ## to use between devices in the same network eg.192.168.1.5
port = 8080
# connect to server
client.connect((host, port))
# write my name
my_name = input("Insert your nickname: ")
# receive other client's name
other_name = client.recv(1024).decode('utf-8')
global names
names = [my_name,other_name]
# send my name
client.sendall(my_name.encode('utf-8'))

# ricevo il pacchetto di chiavi dall'altro client
key_pack = ast.literal_eval(client.recv(1024).decode('utf-8'))
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
GUI(my_name)
