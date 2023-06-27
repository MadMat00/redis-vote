import redis
from getpass import getpass
from cryptography.fernet import Fernet
import datetime
import os
from dotenv import load_dotenv
import re

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

fernet = Fernet(r.get("ENCRIPTION_KEY"))


def register():
    user = input("Inserisci username: ")
    email = input("Inserisci email: ")
    password = getpass("Inserisci password: ")

    if r.hgetall(email):
        raise ValueError("Utente già registrato")
    else:
        r.hset(email, mapping={
            "Username": user,
            "Password": fernet.encrypt(password.encode())
        })
        print(f"Benvenuto, {user}!")
    return user, email


def login():
    email = input("Inserisci email: ")
    password = getpass("Inserisci password: ")
    if r.hgetall(email) == {}:
        raise ValueError("Utente non registrato")
    else:
        if fernet.decrypt(r.hget(email, "Password")).decode() != password:
            raise ValueError("Password errata")
        user = r.hget(email, "Username")
        print(f"Benvenuto, {user}!")
    return user, email


def nuova_proposta(user, email):
    titolo = input(f"Ciao {user}, inserisci il titolo della tua proposta: ")
    testo = input("Molto bene, ora fai una breve descrizione della tua descrizione: ")
    autori = []
    controlla_proposte_simili(user)

    scelta = int(input("Se è una proposta fatta in collaborazione inserisci 1, se è una idea solo tua allora 0:"))
    if scelta == 1:
        autori.append(email) # aggiunge email dell'utente
        print("Per uscire scrivere exit")
        while True:
            email_compagno = input("Inserisci l'email del tuo compagno: ")
            if email_compagno == "exit":
                break
            autori.append(email_compagno) # email dei co-autori
    else:
        autori.append(email)

    # Set Titolo:Testo, Autori
    #for a in autori:
    #    r.sadd(titolo + ":" + testo, a)
    [r.sadd(titolo + ":" + testo, a) for a in autori]
    # Set Testo, Votanti
    for a in autori:
        r.sadd(testo, a) # si suppone che gli autori votino

    # per ottenere il testo bastera fare sismember(titolo)
    # mentre per ottenere chi ha fatto la proposta basta fare sismemer(sismeber(titolo))

    """
    Permette all'utente di creare una nuova proposta.
    L'utente inserisce il titolo e la descrizione della proposta.
    Un utente può creare più proposte.
    Non ci possono essere proposte con lo stesso titolo.
    Si deve vedere chi ha creato la proposta.
    Al momento della creazione viene aggiunto un voto.
    La lista dei voti deve essere un set.
    """
    return

def vota_proposta(user, email):
    """
    Permette all'utente di votare una proposta.
    L'utente inserisce il titolo della proposta.
    Un utente può votare più proposte.
    Non ci possono essere più voti per la stessa proposta da parte dello stesso utente(il set da errore).
    L'utente non può votare la sua proposta.
    """
    # struttura del set proposta: "Testo": set{ votante1, votante2, ...}

    vedi_proposte(user)
    # print("\nQuale vuoi votare? Inserisci qui il testo della proposta: ")
    print("\nQuale vuoi votare? Inserisci qui il numero: ")
    choice = int(input())

    proposte = r.keys("*:*")
    # Ordina in base al numero di voti (come le vede l'utente)
    proposte.sort(key = lambda p: r.scard(p.split(":")[1]), reverse=True)
    _, testo = proposte[choice].split(":")
    
    
    # Controlla se la email è presente nel set con chiave = proposta
    if r.sismember(testo, email):
        print("Hai già votato, non puoi votare due volte.\n")
    else:
        r.sadd(testo, email)
        voti = r.scard(testo) # cardinalità del set
        print(f"Hai votato la proposta: {testo}.\nNumero voti: {voti}")



def vedi_proposte(user):
    """
    Permette all'utente di vedere le proposte.
    L'utente può vedere le proposte ordinate per numero di voti (lunghezza del set).
    """
    # Il formato della chiave è "Titolo:Testo"
    proposte = r.keys("*:*")
    # Ordina in base al numero di voti
    proposte.sort(key = lambda p: r.scard(p.split(":")[1]), reverse=True)
    # Itera e stampa
    print("\nEcco le proposte:\n")
    for proposta, i in zip(proposte, range(len(proposte))):
        titolo, testo = proposta.split(":")
        voti = r.scard(testo)
        email_autori = list( r.smembers(proposta))
        
        """
        # Codice per stampare gli Username degli autori, invece che le mail
        # funziona solo se l'utente registrato
        autori = []
        for email in email_autori:
            autori.append( r.hget(email, "Username"))
        """
        
        print(f"{i}. {titolo}")
        print(f"{testo}")
        print(f"Autori: {', '.join(email_autori)}")
        print(f"Voti: {voti}")
        print()



def controlla_proposte_simili(proposta):
    """
    Controlla se ci sono proposte con lo stesso titolo.
    Controlla se ci sono proposte con la descrizione simile.
    Se ci sono proposte simili non permette di creare la proposta ma viene aggiunto alla proposta l'utente che ha creato la proposta simile.
    """
    return


def main():
    print("1. Login\n2. Registrazione")
    choice = int(input())

    if choice == 1:
        user, email = login()
    elif choice == 2:
        user, email = register()
    else:
        raise ValueError("Valore non valido")

    while True:
        print("1. Nuova proposta\n2. Vota proposta\n3. Vedi proposte\n4. Esci")
        choice = int(input())
        if choice == 1:
            nuova_proposta(user, email)
        elif choice == 2:
            vota_proposta(user, email)
        elif choice == 3:
            vedi_proposte(user)
        elif choice == 4:
            print("Arrivederci!")
            break

if __name__ == '__main__':
    main()