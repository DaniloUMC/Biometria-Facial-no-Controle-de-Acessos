import os
import base64
import mysql.connector
from database.db import conectar


# 📁 pasta onde salva as fotos
PASTA_FOTOS = "static/fotos"

if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)


# 🔹 SALVAR USUÁRIO
def salvar_usuario(dados):

    try:
        conn = conectar()
        cursor = conn.cursor()

        cpf = dados.get("cpf")
        email = dados.get("email")

        
        cursor.execute(
            "SELECT id FROM usuarios WHERE cpf = %s OR email = %s",
            (cpf, email)
        )

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        
        imagem = dados.get("imagem")
        caminho_foto = None

        if imagem:
            imagem = imagem.split(",")[1]
            imagem_bytes = base64.b64decode(imagem)

            caminho_foto = f"{PASTA_FOTOS}/{cpf}.png"

            with open(caminho_foto, "wb") as f:
                f.write(imagem_bytes)

        
        query = """
        INSERT INTO usuarios 
        (nome, cpf, cep, rua, numero, bairro, cidade, estado, ano_nascimento, foto, senha, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            dados.get("nome"),
            cpf,
            dados.get("cep"),
            dados.get("rua"),
            dados.get("numero"),
            dados.get("bairro"),
            dados.get("cidade"),
            dados.get("estado"),
            dados.get("ano"),
            caminho_foto,
            dados.get("senha"),
            email,
        )

        cursor.execute(query, valores)
        conn.commit()

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print("Erro ao salvar usuário:", e)
        return False


def buscar_usuario(login):

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM usuarios 
        WHERE cpf = %s OR email = %s
        """

        cursor.execute(query, (login, login))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        return usuario

    except Exception as e:
        print("Erro ao buscar usuário:", e)
        return None






def excluir_usuario(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()