from cryptography.fernet import Fernet
import os

CHAVE = os.getenv("SECRET_FACE_KEY").encode()

fernet = Fernet(CHAVE)

def criptografar_arquivo(caminho):
    with open(caminho, "rb") as arquivo:
        dados = arquivo.read()

    dados_criptografados = fernet.encrypt(dados)

    with open(caminho, "wb") as arquivo:
        arquivo.write(dados_criptografados)