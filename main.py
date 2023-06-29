import redis
from getpass import getpass
from cryptography.fernet import Fernet
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
)


if not r.get("encryption_key"):
    encryption_key = Fernet.generate_key()
    r.set("encryption_key", encryption_key)

encryption_key = r.get("encryption_key")
fernet = Fernet(encryption_key)


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
    return user


def login():
    email = input("Inserisci email: ")
    password = getpass("Inserisci password: ")
    if r.hgetall(email) == {}:
        raise ValueError("Utente non registrato")
    else:
        if fernet.decrypt(r.hget(email, "Password")).decode() != password:
            raise ValueError("Password errata")
        user = r.hget(email, "Username").decode()
        print(f"Benvenuto, {user}!")
    return user


def nuova_proposta(user):
    titolo = input(f"Ciao {user}, inserisci il titolo della tua proposta: ")
    testo = input("Molto bene, ora fai una breve descrizione della tua descrizione:")
    controlla_proposte_simili(user)
    r.sadd(titolo, testo)
    scelta = int(input("Se è una proposta fatta in collaborazione inserisci 1, se è una idea solo tua allora 0:"))
    if scelta == 1:
        print("Per uscire scrivere exit")
        while True:
            email_compagno = input("Inserisci l'email del tuo compagno: ")
            if email_compagno == "exit":
                break
            r.sadd(testo, email_compagno)
    else:
        r.sadd(testo, email)

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


def vota_proposta(user):
    """
    Permette all'utente di votare una proposta.
    L'utente inserisce il titolo della proposta.
    Un utente può votare più proposte.
    Non ci possono essere più voti per la stessa proposta da parte dello stesso utente(il set da errore).
    L'utente non può votare la sua proposta.
    """
    return


def vedi_proposte(user):
    """
    Permette all'utente di vedere le proposte.
    L'utente può vedere le proposte ordinate per numero di voti (lunghezza del set).    
    """
    return


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
        user = login()
    elif choice == 2:
        user = register()
    else:
        raise ValueError("Valore non valido")

    while True:
        print("1. Nuova proposta\n2. Vota proposta\n3. Vedi proposte\n4. Esci")
        choice = int(input())
        if choice == 1:
            nuova_proposta(user)
        elif choice == 2:
            vota_proposta(user)
        elif choice == 3:
            vedi_proposte(user)
        elif choice == 4:
            print("Arrivederci!")
            break

if __name__ == "__main__":
    main()