
# IDEA

Questo codice rappresenta una rudimentale implementazione dell'algoritmo X3DF utilizzato da WhatsApp e Signal per garantire la segretezza delle conversazioni. La comunicazione avviene attraverso due client collegati ad un server, posto all'indirizzo '127.0.0.1/8080' (localhost). 

# UTILIZZO

client.py e server.py simulano una conversazione.

1) Apri una finestra del terminale nella cartella e manda 

python server.py

per avviare il server

2) Apri altre due terminali nella cartella e manda

python client.py

in entrambe, immettendo Alice e Bob come nickname (o i nickname che vuoi).

Il server si avvia silenziosamente, mentre entrambi i client comunicano l'apertura della chat e richiedono l'inserimento dei nickname.
A questo punto è possibile per entrambi i client avviare una conversazione crittografata attraverso il server.
Per chiudere i due client si deve ricorrere due volte al KeyboardInterrupt (CTRL + C) dal terminale per ognuno di essi; in questo caso, il lancio di eccezioni nei due terminali non comporterà alcun problema per quanto riguarda la riuscita della chat.
Il server si spegnerà silenziosamente.

# FILE GENERATI

Vengono generati quattro file:

1) 'chat.txt' è il file che contiene la chat dal punto di vista del frontend e contiene solamente i messaggi della conversazione, riportati con il formato [ora , mittente , messaggio].
2) 'public_chat.txt' è il file che contiene la chat dal punto di vista di un agente esterno (attaccante) che controlli il movimento dei pacchetti tra i client e il server e che possa leggerne il contenuto (cifrato).
3) 'secret_chat_<utente 1>.txt' e 'secret_chat_<utente 2>.txt' sono i file che contengono le chat dal punto di vista dei due utenti (<utente 1> e <utente 2>), in cui vengono riportate le chiavi segrete e i processi di decrittazione dei messaggi. 

# POSSIBILI PROBLEMI

1) L'implementazione tramite il modulo 'socket' di Python ha dei problemi noti alla radice, i quali non garantiscono sempre l'invio corretto dei dati e, di conseguenza, la loro corretta valutazione da parte del programma, generando possibilmente delle eccezioni.

SOLUZIONE: Modificare la porta del socket del server in 'server.py' da 8080 ad un numero maggiore di 1024 e, conseguentemente, il numero di porta all'interno di 'client.py'. In seguito riavviare i programmi.

2) La chiusura del processo 'server.py' durante l'esecuzione dei due programmi client comporterà un'eccezione all'interno dei due terminali client. 

SOLUZIONE: Interrompere l'esecuzione di tutti i programmi coinvolti con KeyboardInterrupt (CTRL + C). Modificare la porta del socket del server in 'server.py' da 8080 ad un numero maggiore di 1024 e, conseguentemente, il numero di porta all'interno di 'client.py'. In seguito riavviare i programmi.



