import os
import base64
import mysql.connector
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from database.db import conectar

load_dotenv()

SECRET_FACE_KEY = os.getenv("SECRET_FACE_KEY")

if not SECRET_FACE_KEY:
    raise ValueError("SECRET_FACE_KEY não encontrada no arquivo .env")

fernet = Fernet(SECRET_FACE_KEY.encode())

PASTA_FOTOS = "storage/faces"

if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)


def salvar_imagem_criptografada(caminho_foto, imagem_base64):
    imagem = imagem_base64.split(",")[1]
    imagem_bytes = base64.b64decode(imagem)
    imagem_criptografada = fernet.encrypt(imagem_bytes)

    with open(caminho_foto, "wb") as f:
        f.write(imagem_criptografada)


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
            caminho_foto = os.path.join(PASTA_FOTOS, f"{cpf}.face")
            salvar_imagem_criptografada(caminho_foto, imagem)

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

        usuario_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return usuario_id

    except mysql.connector.IntegrityError:
        return False

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


def excluir_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()

    query = "DELETE FROM usuarios WHERE id = %s"

    cursor.execute(query, (usuario_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return True


def listar_usuarios_com_foto():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome, cpf, foto 
        FROM usuarios 
        WHERE foto IS NOT NULL
    """)

    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return usuarios

def listar_usuarios_paginado(termo="", limite=25, offset=0):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    termo_busca = f"%{termo}%"

    query = """
    SELECT id, nome, cpf, email, cidade, estado, data_cadastro
    FROM usuarios
    WHERE nome LIKE %s OR cpf LIKE %s OR email LIKE %s
    ORDER BY nome ASC
    LIMIT %s OFFSET %s
    """

    cursor.execute(query, (
        termo_busca,
        termo_busca,
        termo_busca,
        limite,
        offset
    ))

    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return usuarios


def buscar_usuario_por_id(usuario_id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome, cpf, email, cep, rua, numero, bairro, cidade, estado, ano_nascimento, foto
        FROM usuarios
        WHERE id = %s
    """, (usuario_id,))

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    return usuario


def atualizar_usuario(usuario_id, dados):
    conn = conectar()
    cursor = conn.cursor()

    query = """
    UPDATE usuarios
    SET nome = %s,
        email = %s,
        cep = %s,
        rua = %s,
        numero = %s,
        bairro = %s,
        cidade = %s,
        estado = %s
    WHERE id = %s
    """

    valores = (
        dados.get("nome"),
        dados.get("email"),
        dados.get("cep"),
        dados.get("rua"),
        dados.get("numero"),
        dados.get("bairro"),
        dados.get("cidade"),
        dados.get("estado"),
        usuario_id
    )

    cursor.execute(query, valores)
    conn.commit()

    cursor.close()
    conn.close()

    return True


def atualizar_foto_usuario(usuario_id, imagem_base64):
    if not imagem_base64 or "," not in imagem_base64:
        return False

    usuario = buscar_usuario_por_id(usuario_id)

    if not usuario:
        return False

    cpf = usuario["cpf"]

    if not os.path.exists(PASTA_FOTOS):
        os.makedirs(PASTA_FOTOS)

    caminho_foto = os.path.join(PASTA_FOTOS, f"{cpf}.face")

    salvar_imagem_criptografada(caminho_foto, imagem_base64)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET foto = %s
        WHERE id = %s
    """, (caminho_foto, usuario_id))

    conn.commit()

    cursor.close()
    conn.close()

    return True