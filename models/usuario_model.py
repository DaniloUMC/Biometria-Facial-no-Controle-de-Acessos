import os
import base64
from database.db import conectar

PASTA_FOTOS = "static/fotos"

if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)


def salvar_usuario(dados):

    conn = conectar()
    cursor = conn.cursor()

    cpf = dados.get("cpf")

    # 🚫 EVITA CPF DUPLICADO
    cursor.execute("SELECT id FROM usuarios WHERE cpf = %s", (cpf,))
    if cursor.fetchone():
        conn.close()
        return False

    # 📸 SALVAR FOTO
    imagem = dados.get("imagem")
    caminho_foto = None

    if imagem:
        imagem = imagem.split(",")[1]
        imagem_bytes = base64.b64decode(imagem)

        caminho_foto = f"{PASTA_FOTOS}/{cpf}.png"

        with open(caminho_foto, "wb") as f:
            f.write(imagem_bytes)

    # 💾 INSERIR NO BANCO
    query = """
    INSERT INTO usuarios 
    (nome, cpf, cep, rua, numero, bairro, cidade, estado, ano_nascimento, foto)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        caminho_foto
    )

    cursor.execute(query, valores)
    conn.commit()

    cursor.close()
    conn.close()

    return True