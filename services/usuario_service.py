import bcrypt
from models.usuario_model import salvar_usuario, excluir_usuario
from models.usuario_model import listar_usuarios_paginado
from models.usuario_model import buscar_usuario_por_id, atualizar_usuario, atualizar_foto_usuario
from services.mascara_service import mascarar_lista_usuarios, mascarar_usuario
from models.usuario_model import excluir_usuario as excluir_usuario_model
from models.usuario_model import (
    salvar_usuario,
    excluir_usuario,
    listar_usuarios_paginado,
    buscar_usuario_por_id,
    atualizar_usuario,
    atualizar_foto_usuario,
    atualizar_meus_dados
)

def cadastrar_usuario(dados, imagem):
    try:
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

        resultado = salvar_usuario(dados)

        if not resultado["sucesso"]:
            return {
                "sucesso": False,
                "mensagem": resultado["mensagem"]
            }

        return {
            "sucesso": True,
            "usuario_id": resultado["usuario_id"],
            "mensagem": "Usuário cadastrado com sucesso."
        }

    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao cadastrar usuário: {str(e)}"
        }

def remover_usuario(usuario_id):
    return excluir_usuario(usuario_id)


def listar_usuarios(termo="", limite=25, offset=0):
    usuarios = listar_usuarios_paginado(termo, limite, offset)
    return mascarar_lista_usuarios(usuarios)

def excluir_usuario(usuario_id):
    return excluir_usuario_model(usuario_id)


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

def atualizar_dados_do_usuario_logado(usuario_id, dados):

    campos_obrigatorios = [
        "nome",
        "email",
        "cep",
        "rua",
        "numero",
        "bairro",
        "cidade",
        "estado"
    ]

    for campo in campos_obrigatorios:
        if not dados.get(campo):
            return {
                "sucesso": False,
                "mensagem": f"O campo {campo} é obrigatório."
            }

    if "cpf" in dados:
        return {
            "sucesso": False,
            "mensagem": "O CPF não pode ser alterado."
        }

    dados_tratados = dict(dados)

    dados_tratados["intencao_evento"] = (
        1 if dados.get("intencao_evento") == "1" else 0
    )

    atualizar_meus_dados(usuario_id, dados_tratados)

    return {
        "sucesso": True,
        "mensagem": "Dados atualizados com sucesso."
    }