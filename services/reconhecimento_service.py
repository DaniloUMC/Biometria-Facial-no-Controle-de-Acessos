import os
import base64
import tempfile
from deepface import DeepFace
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from models.usuario_model import listar_usuarios_com_foto
from models.acesso_model import registrar_acesso


load_dotenv()

SECRET_FACE_KEY = os.getenv("SECRET_FACE_KEY")

if not SECRET_FACE_KEY:
    raise ValueError("SECRET_FACE_KEY não encontrada no arquivo .env")

fernet = Fernet(SECRET_FACE_KEY.encode())

def mascarar_cpf_registro(cpf):
    if not cpf:
        return ""

    cpf_limpo = "".join(filter(str.isdigit, str(cpf)))

    if len(cpf_limpo) < 4:
        return "***" + cpf_limpo

    return "***" + cpf_limpo[-4:]

def remover_arquivo(caminho):
    if caminho and os.path.exists(caminho):
        os.remove(caminho)


def montar_registro_usuario(usuario):
    nome = usuario.get("nome", "").strip()
    primeiro_nome = nome.split()[0] if nome else "Usuario"
    return f"{usuario['id']} - {primeiro_nome}"


def descriptografar_foto_para_temp(caminho_foto):
    with open(caminho_foto, "rb") as arquivo:
        dados_criptografados = arquivo.read()

    dados = fernet.decrypt(dados_criptografados)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp.write(dados)
    temp.close()

    return temp.name


def salvar_captura_temporaria(imagem_base64):
    imagem_base64 = imagem_base64.split(",")[1]
    imagem_bytes = base64.b64decode(imagem_base64)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp.write(imagem_bytes)
    temp.close()

    return temp.name


def reconhecer_usuario(imagem_base64):
    caminho_captura = None
    caminho_foto_temp = None

    try:
        if not imagem_base64:
            return {
                "sucesso": False,
                "mensagem": "Imagem não enviada"
            }

        if "," not in imagem_base64:
            return {
                "sucesso": False,
                "mensagem": "Formato de imagem inválido"
            }

        caminho_captura = salvar_captura_temporaria(imagem_base64)

        usuarios = listar_usuarios_com_foto()

        if not usuarios:
            remover_arquivo(caminho_captura)

            return {
                "sucesso": False,
                "mensagem": "Nenhum usuário com foto cadastrada"
            }

        for usuario in usuarios:
            caminho_foto = usuario.get("foto")

            if not caminho_foto or not os.path.exists(caminho_foto):
                continue

            try:
                caminho_foto_temp = descriptografar_foto_para_temp(caminho_foto)
            except Exception:
                remover_arquivo(caminho_foto_temp)
                caminho_foto_temp = None
                continue

            try:
                resultado = DeepFace.verify(
                    img1_path=caminho_captura,
                    img2_path=caminho_foto_temp,
                    model_name="Facenet",
                    detector_backend="opencv",
                    enforce_detection=False
                )
            except Exception:
                remover_arquivo(caminho_foto_temp)
                caminho_foto_temp = None
                continue

            remover_arquivo(caminho_foto_temp)
            caminho_foto_temp = None

            if resultado.get("verified"):
                distancia = float(resultado.get("distance", 0))
                usuario_registro = montar_registro_usuario(usuario)
                cpf_mascarado = mascarar_cpf_registro(usuario.get("cpf"))

                registrar_acesso(
                    usuario["id"],
                    usuario_registro,
                    cpf_mascarado,
                    "PERMITIDO",
                    "Usuário reconhecido na entrada do evento",
                    distancia
                )

                remover_arquivo(caminho_captura)

                return {
                    "sucesso": True,
                    "usuario_id": usuario["id"],
                    "nome": usuario["nome"],
                    "usuario_registro": usuario_registro,
                    "mensagem": "Acesso permitido",
                    "distancia": distancia
                }

        remover_arquivo(caminho_captura)

        return {
            "sucesso": False,
            "mensagem": "Usuário não reconhecido"
        }

    except Exception as e:
        remover_arquivo(caminho_captura)
        remover_arquivo(caminho_foto_temp)

        return {
            "sucesso": False,
            "mensagem": "Erro no reconhecimento facial",
            "erro": str(e)
        }
    



