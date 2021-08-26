
# IDEA

Questo codice rappresenta una rudimentale implementazione dell'algoritmo X3DH utilizzato da WhatsApp e Signal per garantire la segretezza delle conversazioni. La comunicazione avviene attraverso due client collegati ad un server, posto all'indirizzo '127.0.0.1/8080' (localhost, porta 8080). 

# PRIMA DI INIZIARE
## PYCRYPTODOME

Verifica di avere installato il modulo ***pycryptodome***. Apri un terminale Python ed esegui
```
import Crypto

print(Crypto.__version__)

```
La versione più recente disponibile durante la scrittura di questo readme è la 3.10.1, ma in futuro potrebbe essere aggiornata. Se hai già installato ***pycryptodome*** e vuoi aggiornarlo, esegui:
```
pip install pycryptodome -U

```

Se, invece, ***pycryptodome*** non è installato, esegui:
```
pip install pycryptodome

```
Il modulo ***Crypto*** all'interno dei file farà riferimento a ***pycryptodome*** e non più al modulo ***Crypto*** (deprecato).

## CRYPTOGRAPHY
Verifica di avere installato il modulo ***cryptography***. Apri un terminale Python ed esegui
```
import cryptography

print(cryptography.__version__)

```
La versione più recente disponibile durante la scrittura di questo readme è la 3.4.7, ma in futuro potrebbe essere aggiornata. Se hai già installato ***cryptography*** e vuoi aggiornarlo, esegui:
```
pip install cryptography -U

```

Se, invece, ***cryptography*** non è installato, esegui:
```
pip install cryptography

```

## COLORAMA
Verifica di avere installato il modulo ***colorama***. Apri un terminale Python ed esegui
```
import colorama

print(colorama.__version__)

```
La versione più recente disponibile durante la scrittura di questo readme è la 0.4.4, ma in futuro potrebbe essere aggiornata. Se hai già installato ***colorama*** e vuoi aggiornarlo, esegui:
```
pip install colorama -U

```

Se, invece, ***colorama*** non è installato, esegui:
```
pip install colorama

```


# FILE PRESENTI

1) ***server.py*** genera un server, di default all'indirizzo '127.0.0.1/8080' (localhost, porta 8080). Il suo compito è trasmettere il numero primo condiviso p, il generatore condiviso g del gruppo Zp*, le chiavi pubbliche e i messaggi crittografati da un client all'altro.
2) ***client.py*** genera un client e lo collega al server. Il suo compito è generare le chiavi pubbliche e private e consentire lo scambio di messaggi con l'altro client.
3) ***generate_prime*** ritorna un numero primo di n bit. Genera un numero casuale di n bit e sfrutta il test di Rabin-Miller (complessità polinomiale) per verificarne la primalità.
5) ***generator_finder*** ritorna un generatore per il gruppo ciclico Zp*, dove p è il numero primo condiviso fra i client.
6) ***generate_keys*** contiene due funzioni, *pub_priv_keys* e *KDF*. La prima calcola le chiavi pubbliche e private di n bit per un client, mentre il secondo calcola il segreto condiviso tramite KDF (Key Derivation Function).
7) ***nice_text.py*** serve per centrare e incorniciare i titoli delle chat.

# UTILIZZO

***client.py*** e ***server.py*** simulano una conversazione.

1) Apri una finestra del terminale nella cartella ed esegui 
```
python server.py

```

per avviare il server

2) Apri altre due terminali nella cartella e manda
```
python client.py

```

in entrambe, immettendo Alice e Bob come nickname (o i nickname che vuoi).

Il server si avvia silenziosamente, mentre entrambi i client comunicano l'apertura della chat e richiedono l'inserimento dei nickname.
A questo punto è possibile per entrambi i client avviare una conversazione crittografata attraverso il server.
Per chiudere i due client si deve ricorrere due volte al KeyboardInterrupt (**CTRL + C**) dal terminale per ognuno di essi; in questo caso, il lancio di eccezioni nei due terminali non comporterà alcun problema per quanto riguarda la riuscita della chat.
Il server si spegnerà silenziosamente.

# FILE GENERATI

Vengono generati quattro file:

1) *chat.txt* è il file che contiene la chat dal punto di vista del frontend e contiene solamente i messaggi della conversazione, riportati con il formato [ora , mittente , messaggio].
2) *public_chat.txt* è il file che contiene la chat dal punto di vista di un agente esterno (attaccante) che controlli il movimento dei pacchetti tra i client e il server e che possa leggerne il contenuto (cifrato).
3) *secret_chat_<utente 1>.txt* e *secret_chat_<utente 2>.txt* sono i file che contengono le chat dal punto di vista dei due utenti (<utente 1> e <utente 2>), in cui vengono riportate le chiavi segrete e i processi di decrittazione dei messaggi. 

# POSSIBILI PROBLEMI (riscontrati su Ubuntu 20.04)

1) L'implementazione tramite il modulo ***socket*** di Python ha dei problemi noti alla radice, i quali non garantiscono sempre l'invio corretto dei dati e, di conseguenza, la loro corretta valutazione da parte del programma, generando possibilmente delle eccezioni.

SOLUZIONE: Modificare la porta del socket del server in ***server.py*** da 8080 ad un numero maggiore di 1024 e, conseguentemente, il numero di porta all'interno di ***client.py***. In seguito riavviare i programmi.

2) La chiusura del processo ***server.py*** durante l'esecuzione dei due programmi client comporterà un'eccezione all'interno dei due terminali client. 

SOLUZIONE: Interrompere l'esecuzione di tutti i programmi coinvolti con KeyboardInterrupt (**CTRL + C**). Modificare la porta del socket del server in ***server.py*** da 8080 ad un numero maggiore di 1024 e, conseguentemente, il numero di porta all'interno di ***client.py***. In seguito riavviare i programmi.



