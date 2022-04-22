import sys
from tkinter import *
from socket import *
import _thread
import ast
from Crypto.Cipher import AES
from generate_keys import *
from generate_prime import *

global mode
if sys.argv[1] == "plain":
    mode = "plain"
elif sys.argv[1] == "ciphered":
    mode = "ciphered"
else:
    print("Mode must be 'plain' or 'ciphered'. Exiting")
    exit(0)
def gen_message_key():
    global message_key
    global ep_secret_key
    global lt_secret_key
    shk1 = shared_key(lt_pub_key_other_client, ep_secret_key, p)
    shk2 = shared_key(ep_pub_key_other_client, ep_secret_key, p)
    shk3 = shared_key(ep_pub_key_other_client, lt_secret_key, p)    
    message_key = KDF(shk1, shk2, shk3)

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
    gui.geometry("800x860")

    # text space to display messages
    chatlog = Text(gui, bg='white')
    chatlog.config(state=DISABLED)

    # button to send messages
    sendbutton = Button(gui, bg='orange', fg='black', text='SEND', command=send, relief="raised")

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
s = socket(AF_INET, SOCK_STREAM)
# config details of server
host = 'localhost'  ## to use between devices in the same network eg.192.168.1.5
port = 8080
# initialize server
s.bind((host, port))
# set no. of clients
s.listen(1)
# accept the clientection from client
client, addr = s.accept()
# send generators to the other client
# Generazione di p e g da condividere ai due client
# write my name
my_name = input("Insert your nickname: ")
# send my name
client.sendall(my_name.encode('utf-8'))
# receive other client's name
other_name = client.recv(1024).decode('utf-8')
global names
names = [my_name,other_name]
p_bit_length = 16
p = prime_generator(p_bit_length)
g = find_group_generators(p,1)[0]
p_g = str([p,g])
client.sendall(p_g.encode('utf-8'))
# generate my keys
lt_public_key, lt_secret_key = pub_priv_keys(p, g, 16)
ep_public_key, ep_secret_key = pub_priv_keys(p, g, 16)
public_keys = [lt_public_key,ep_public_key]
# receive other client's keys
his_keys = ast.literal_eval(client.recv(1024).decode('utf-8'))
lt_pub_key_other_client = his_keys[0]
ep_pub_key_other_client = his_keys[1]
# send him my keys
client.sendall(str(public_keys).encode('utf-8'))
# generate shared key
gen_message_key()
GUI(my_name)
