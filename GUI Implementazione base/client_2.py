import sys
from tkinter import *
import tkinter as tk
from datetime import datetime
from socket import *
import _thread
import ast
from Crypto.Cipher import AES
from generate_keys import *


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
    shk1 = shared_key(ep_pub_key_other_client, lt_secret_key, p)
    shk2 = shared_key(ep_pub_key_other_client, ep_secret_key, p)
    shk3 = shared_key(lt_pub_key_other_client, ep_secret_key, p)
    message_key = KDF(shk1, shk2, shk3)

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
other_name = client.recv(1024).decode('utf-8')
global names
names = [my_name,other_name]
# invio nickname all'altro client
client.sendall(my_name.encode('utf-8'))
# ricevo p e g dall'altro client
p_g = ast.literal_eval(client.recv(1024).decode('utf-8'))
global p
global g
p = p_g[0]
g = p_g[1]
# generate my keys
global lt_public_key
global lt_secret_key
global ep_public_key
global ep_secret_key
# genero le mie chiavi
lt_public_key, lt_secret_key = pub_priv_keys(p, g, 16)
ep_public_key, ep_secret_key = pub_priv_keys(p, g, 16)
public_keys = [lt_public_key,ep_public_key]
# mando all'altro client le mie chiavi
client.sendall(str(public_keys).encode('utf-8'))
# ricevo le chiavi dell'altro client
his_keys = ast.literal_eval(client.recv(1024).decode('utf-8'))
lt_pub_key_other_client = his_keys[0]
ep_pub_key_other_client = his_keys[1]
# genero la chiave condivisa
gen_message_key()
chars_per_line = 40
GUI(my_name)

