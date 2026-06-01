import bcrypt
from models.usuario_model import salvar_usuario, excluir_usuario
from models.usuario_model import listar_usuarios_paginado
from models.usuario_model import buscar_usuario_por_id, atualizar_usuario, atualizar_foto_usuario
from services.mascara_service import mascarar_lista_usuarios, mascarar_usuario

def cadastrar_usuario(dados, imagem):
    if not imagem:
        return {
            "sucesso": False,
            "mensagem": "Capture a imagem antes de finalizar!"
        }

    email = dados.get("email")

    if not email:
        return {
            "sucesso": False,
            "mensagem": "Email obrigatório"
        }

    senha = dados.get("senha")

    if not senha:
        return {
            "sucesso": False,
            "mensagem": "Senha obrigatória"
        }

    hash_senha = bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    )

    dados["senha"] = hash_senha.decode("utf-8")
    dados["imagem"] = imagem

    usuario_id = salvar_usuario(dados)

    if not usuario_id:
        return {
            "sucesso": False,
            "mensagem": "CPF ou Email já cadastrado!"
        }

    return {
        "sucesso": True,
        "usuario_id": usuario_id
    }


def remover_usuario(usuario_id):
    return excluir_usuario(usuario_id)


def listar_usuarios(termo="", limite=25, offset=0):
    usuarios = listar_usuarios_paginado(termo, limite, offset)
    return mascarar_lista_usuarios(usuarios)


def obter_usuario(usuario_id):
    usuario = buscar_usuario_por_id(usuario_id)

    if not usuario:
        return None

    return mascarar_usuario(usuario)


def editar_usuario(usuario_id, dados):
    imagem = dados.get("imagemCapturada")

    sucesso = atualizar_usuario(usuario_id, dados)

    if imagem:
        atualizar_foto_usuario(usuario_id, imagem)

    return sucesso


def editar_foto_usuario(usuario_id, imagem):
    return atualizar_foto_usuario(usuario_id, imagem)