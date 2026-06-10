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

def reconhecer_usuario(imagem_base64, evento_id_atual=1):
    caminho_captura = None
    caminho_foto_temp = None

    try:
        if not imagem_base64:
            return {
                "sucesso": False,
                "tipo": "IMAGEM_NAO_ENVIADA",
                "mensagem": "Imagem não enviada. Procure a administração."
            }

        if "," not in imagem_base64:
            return {
                "sucesso": False,
                "tipo": "FORMATO_INVALIDO",
                "mensagem": "Formato de imagem inválido. Procure a administração."
            }

        caminho_captura = salvar_captura_temporaria(imagem_base64)
        usuarios = listar_usuarios_com_foto()

        if not usuarios:
            remover_arquivo(caminho_captura)

            return {
                "sucesso": False,
                "tipo": "SEM_CADASTROS",
                "mensagem": "Nenhum cadastro biométrico localizado. Procure a administração."
            }

        houve_usuario_evento = False
        houve_usuario_lgpd = False
        houve_usuario_cancelado = False
        houve_foto_valida = False
        houve_erro_biometria = False

        for usuario in usuarios:
            try:
                usuario_evento_id = int(usuario.get("evento_id", 1))
            except Exception:
                usuario_evento_id = 1

            if usuario_evento_id != int(evento_id_atual):
                continue

            houve_usuario_evento = True

            if int(usuario.get("consentimento_lgpd", 0)) != 1:
                continue

            houve_usuario_lgpd = True

            if int(usuario.get("intencao_evento", 1)) != 1:
                houve_usuario_cancelado = True
                continue

            caminho_foto = usuario.get("foto")

            if not caminho_foto or not os.path.exists(caminho_foto):
                continue

            houve_foto_valida = True

            try:
                caminho_foto_temp = descriptografar_foto_para_temp(caminho_foto)
            except Exception:
                houve_erro_biometria = True
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
                houve_erro_biometria = True
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
                    usuario_registro,
                    cpf_mascarado,
                    "PERMITIDO",
                    "Usuário reconhecido na entrada do evento",
                    distancia
                )

                remover_arquivo(caminho_captura)

                return {
                    "sucesso": True,
                    "tipo": "ACESSO_PERMITIDO",
                    "usuario_id": usuario["id"],
                    "nome": usuario["nome"],
                    "usuario_registro": usuario_registro,
                    "cpf": cpf_mascarado,
                    "mensagem": "Acesso permitido",
                    "distancia": distancia
                }

        remover_arquivo(caminho_captura)

        if not houve_usuario_evento:
            return {
                "sucesso": False,
                "tipo": "EVENTO_NAO_AUTORIZADO",
                "mensagem": "Participante não autorizado para este evento. Procure a administração."
            }

        if not houve_usuario_lgpd:
            return {
                "sucesso": False,
                "tipo": "LGPD_PENDENTE",
                "mensagem": "Consentimento LGPD pendente. Procure a administração."
            }

        if houve_usuario_cancelado:
            return {
                "sucesso": False,
                "tipo": "EVENTO_CANCELADO",
                "mensagem": "Participação no evento cancelada. Procure a administração."
            }

        if not houve_foto_valida:
            return {
                "sucesso": False,
                "tipo": "SEM_FOTO_BIOMETRICA",
                "mensagem": "Biometria não encontrada. Procure a administração."
            }

        if houve_erro_biometria:
            return {
                "sucesso": False,
                "tipo": "ERRO_BIOMETRIA",
                "mensagem": "Erro na biometria cadastrada. Procure a administração."
            }

        return {
            "sucesso": False,
            "tipo": "NAO_RECONHECIDO",
            "mensagem": "Não foi possível validar sua identidade automaticamente. Procure a administração do evento."
        }

    except Exception as e:
        remover_arquivo(caminho_captura)
        remover_arquivo(caminho_foto_temp)

        return {
            "sucesso": False,
            "tipo": "ERRO_RECONHECIMENTO",
            "mensagem": "Erro na validação biométrica. Procure a administração.",
            "erro": str(e)
        }