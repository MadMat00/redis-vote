import redis
from getpass import getpass
from cryptography.fernet import Fernet
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
)

fernet = Fernet(r.get("ENCRIPTION_KEY"))

def register():
    user = input("Inserisci username: ")
    email = input("Inserisci email: ")
    password = getpass("Inserisci password: ")

    if r.hgetall(email) != {}:
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
    return

def vota_proposta(user):
    return

def vedi_proposte(user):
    return

def controlla_proposte_simili(proposta):
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