from flask import Blueprint, render_template, request, redirect, jsonify, session
from services.auth_service import autenticar_usuario
from services.usuario_service import cadastrar_usuario, remover_usuario
from services.biometria_service import validar_face

usuario_bp = Blueprint('usuario', __name__)


@usuario_bp.route("/evento")
def evento():
    return render_template("evento.html")


@usuario_bp.route("/")
def cadastro():
    return render_template("cadastro.html")


@usuario_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    login = request.form.get("login")
    senha = request.form.get("senha")

    resultado = autenticar_usuario(login, senha)

    if not resultado["sucesso"]:
        return resultado["mensagem"]

    usuario = resultado["usuario"]

    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]

    return redirect("/confirmacao")


@usuario_bp.route("/confirmacao")
def confirmacao():

    if "usuario_id" not in session:
        return redirect("/login")

    return render_template("confirmacao.html")


@usuario_bp.route("/biometria", methods=["POST"])
def biometria():

    dados = request.form

    session["dados_usuario"] = dict(dados)

    return render_template("biometria.html")


@usuario_bp.route("/salvar", methods=["POST"])
def salvar():

    dados = session.get("dados_usuario", {})

    if not dados:
        return "Sessão expirada"

    imagem = request.form.get("imagem")

    resultado = cadastrar_usuario(dados, imagem)

    session.pop("dados_usuario", None)

    if not resultado["sucesso"]:
        return resultado["mensagem"]

    session["usuario_id"] = resultado["usuario_id"]
    session["usuario_nome"] = dados.get("nome")

    return redirect("/confirmacao")


@usuario_bp.route("/excluir", methods=["POST"])
def excluir():

    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return redirect("/login")

    remover_usuario(usuario_id)

    session.clear()

    return "Seus dados foram excluídos com sucesso!"


@usuario_bp.route("/validar_rosto", methods=["POST"])
def validar_rosto():

    data = request.get_json()

    imagem = data.get("imagem")

    resultado = validar_face(imagem)

    return jsonify(resultado)