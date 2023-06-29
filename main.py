import redis
from getpass import getpass
from cryptography.fernet import Fernet
import datetime
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords


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
    testo = input("Molto bene, ora fai una breve descrizione della tua descrizione: ")

    if r.hexists("proposals", titolo):
        print("La proposta esiste già ed è la seguente:")

        print(f"Titolo: {titolo}")
        print(f"Descrizione: {r.hget('proposals', titolo).decode()}")

        scelta = int(input("Se vuoi aggiungerti come collaboratore inserisci 1, altrimenti premi 0 e la proposta non sarà inserita:"))
        if scelta == 1:
            r.sadd(titolo, user)
        return
    else:
        for titolo_esistente in r.hkeys("proposals"):
            print(controlla_proposte_simili(testo,r.hget("proposals", titolo_esistente).decode()))
            if controlla_proposte_simili(testo,r.hget("proposals", titolo_esistente).decode()) > 0.5 and controlla_proposte_simili(testo,r.hget("proposals", titolo_esistente).decode()) < 0.9:
                print("La tua proposta è molto simile a questa:")
                print(f"Titolo: {titolo_esistente.decode()}")
                print(f"Descrizione: {r.hget('proposals', titolo_esistente).decode()}")
                scelta = int(input("Se ritieni che ci sia un errore e la tua proposta è diversa premi 1 per aggiungerla comunque, altrimenti premi 0 e la proposta non sarà inserita:"))
                if scelta == 1:
                    r.hset("proposals", titolo, testo) 
                    r.sadd(titolo, user)
                return
            elif controlla_proposte_simili(testo,r.hget("proposals", titolo_esistente).decode()) >= 0.9:
                print("La tua proposta è troppo simile a questa:")
                print(f"Titolo: {titolo_esistente.decode()}")
                print(f"Descrizione: {r.hget('proposals', titolo_esistente).decode()}")
                return

    r.hset("proposals", titolo, testo) 
    r.sadd(titolo, user)

    scelta = int(input("Se è una proposta fatta in collaborazione inserisci 1, se è una idea solo tua allora 0:"))
    if scelta == 1:
        print("Per uscire scrivere exit")
        while True:
            email_compagno = input("Inserisci l'email del tuo compagno: ")
            if email_compagno == "exit":
                break
            if r.hexists("user_emails", email_compagno):
                compagno_username = r.hget("user_emails", email_compagno).decode()
                r.sadd(titolo, compagno_username)
            else:
                print("Email non registrata.")
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
    for titolo in r.hkeys("proposals"):
        print(f"Titolo: {titolo.decode()}")
        print(f"Descrizione: {r.hget('proposals', titolo).decode()}")
        print(f"Numero di voti: {r.scard(f'{titolo.decode()}_votes')}")
        collaboratori = [email.decode() for email in r.smembers(titolo.decode())]
        print(f"Collaboratori: {', '.join(collaboratori)}")


def controlla_proposte_simili(descrizione1,descrizone2):
    stop_words = stopwords.words('italian')
    vectorizer = CountVectorizer(stop_words=stop_words)
    vectorizer.fit([descrizione1,descrizone2])
    vector = vectorizer.transform([descrizione1,descrizone2])
    return cosine_similarity(vector)[0][1]


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