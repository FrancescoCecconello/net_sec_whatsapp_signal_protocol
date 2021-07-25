# network_security

client.py e chat_server.py simulano una conversazione.

1) Apri una finestra del terminale nella cartella e manda 

python chat_server.py

per avviare il server

2) Apri altre due terminali nella cartella e manda

python client.py

in entrambe, scegliendo Alice e Bob come nickname.

Nel terminale del server compaiono l'indirizzo IP del server e la porta associata a ogni client, si può modificare il print in modo che stampi anche le chiavi pubbliche e private in chiaro o altre informazioni. Se guardi da pagina 57 in poi nel PDF c'è scritto che entrambi devono postare sul server le chiavi pubbliche (long-term e effimere), quindi bisogna modificare il codice in modo che il server memorizzi quelle chiavi.
Poi c'è anche da crittografare il messaggio e decodificarlo durante la fase di invio/ricezione

In pratica dobbiamo mettere la parte di generazione di tutte le chiavi pubbliche e private (+ shared secret) e la codifica/decodifica nel file client.py, che va a pescarsi le chiavi dell'altro client dal server
