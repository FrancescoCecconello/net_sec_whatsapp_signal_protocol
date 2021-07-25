# network_security

client.py e server.py simulano una conversazione.

1) Apri una finestra del terminale nella cartella e manda 

python server.py

per avviare il server

2) Apri altre due terminali nella cartella e manda

python client.py

in entrambe, scegliendo Alice e Bob come nickname.

Nel terminale del server compaiono l'indirizzo IP del server e la porta associata a ogni client, si può modificare il print in modo che stampi anche le chiavi pubbliche e private in chiaro o altre informazioni. Se guardi da pagina 57 in poi nel PDF c'è scritto che entrambi devono postare sul server le chiavi pubbliche (long-term e effimere), quindi bisogna modificare il codice in modo che il server memorizzi quelle chiavi (teoricamente l'ho già fatto).
Poi c'è anche da crittografare il messaggio e decodificarlo durante la fase di invio/ricezione dal lato client. Sarebbe ottimo mostrare tutte le fasi di codifica prima dell'invio e di decodifica dopo la ricezione con qualche print.

In pratica dobbiamo mettere la parte di generazione di tutte le chiavi pubbliche e private (+ shared secret) e la codifica/decodifica nel file client.py, che va a pescarsi le chiavi pubbliche dell'altro client dal server

Il file main serve solo per ricordarsi cosa c'è da fare più o meno, ma alla fine verrà cancellato

Potrebbe essere un'idea creare un file explain_client.py nel quale fai vedere tutti i passaggi crittografici per lasciare pulita la conversazione sul terminale in cui esegui client.py
