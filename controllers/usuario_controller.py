from flask import Blueprint, render_template, request, redirect, jsonify, session
from services.auth_service import autenticar_usuario
from services.usuario_service import cadastrar_usuario, remover_usuario
from services.biometria_service import validar_face
from services.reconhecimento_service import reconhecer_usuario
from services.liveness_service import validar_variacao_frames
from services.dashboard_service import obter_dashboard
from services.usuario_service import cadastrar_usuario, remover_usuario, listar_usuarios
from services.acesso_service import obter_registros
from services.usuario_service import obter_usuario, editar_usuario, editar_foto_usuario
from flask import send_file
from openpyxl import Workbook
import tempfile
from functools import wraps
from services.admin_service import autenticar_admin


usuario_bp = Blueprint('usuario', __name__)

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            return redirect("/admin/login")

        return func(*args, **kwargs)

    return wrapper

@usuario_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")

    email = request.form.get("email")
    senha = request.form.get("senha")

    resultado = autenticar_admin(email, senha)

    if not resultado["sucesso"]:
        return render_template("admin_login.html", erro=resultado["mensagem"])

    admin = resultado["admin"]

    session["admin_id"] = admin["id"]
    session["admin_nome"] = admin["nome"]

    return redirect("/admin")


@usuario_bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_nome", None)

    return redirect("/admin/login")



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

@usuario_bp.route("/entrada")
def entrada():
    return render_template("entrada.html")


@usuario_bp.route("/reconhecer", methods=["POST"])
def reconhecer():
    data = request.get_json()
    imagem = data.get("imagem")

    resultado = reconhecer_usuario(imagem)

    return jsonify(resultado)

@usuario_bp.route("/validar_liveness", methods=["POST"])
def validar_liveness():
    data = request.get_json()
    frames = data.get("frames")

    resultado = validar_variacao_frames(frames)

    return jsonify(resultado)

@usuario_bp.route("/admin")
@admin_required
def admin():
    dados = obter_dashboard()

    return render_template("admin.html", dados=dados)

@usuario_bp.route("/gerenciar")
@admin_required
def gerenciar():
    usuarios = listar_usuarios()

    return render_template("gerenciar.html", usuarios=usuarios)



@usuario_bp.route("/usuarios/listar")
@admin_required
def usuarios_listar():
    termo = request.args.get("termo", "")
    offset = int(request.args.get("offset", 0))

    usuarios = listar_usuarios(termo, 25, offset)

    return jsonify(usuarios)

@usuario_bp.route("/usuario/editar/<int:usuario_id>", methods=["GET"])
@admin_required
def editar_usuario_view(usuario_id):
    usuario = obter_usuario(usuario_id)

    if not usuario:
        return "Usuário não encontrado"

    return render_template("editar_usuario.html", usuario=usuario)




@usuario_bp.route("/usuario/editar/<int:usuario_id>", methods=["POST"])
@admin_required
def editar_usuario_post(usuario_id):

    dados = request.form

    imagem = dados.get("imagemCapturada")

    sucesso = editar_usuario(usuario_id, dados)

    if imagem:
        editar_foto_usuario(usuario_id, imagem)

    if not sucesso:
        return "Erro ao atualizar usuário"

    return redirect("/gerenciar")

@usuario_bp.route("/registros")
@admin_required
def registros():
    acessos = obter_registros(limite=50, offset=0)
    return render_template("registros.html", acessos=acessos)


@usuario_bp.route("/registros/listar")
@admin_required
def registros_listar():
    termo = request.args.get("termo", "")
    status = request.args.get("status", "")
    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")
    offset = int(request.args.get("offset", 0))

    acessos = obter_registros(termo, status, data_inicio, data_fim, 50, offset)

    return jsonify(acessos)


@usuario_bp.route("/registros/exportar")
@admin_required
def registros_exportar():
    termo = request.args.get("termo", "")
    status = request.args.get("status", "")
    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")

    acessos = obter_registros(termo, status, data_inicio, data_fim, 10000, 0)

    wb = Workbook()
    ws = wb.active
    ws.title = "Registros"

    ws.append(["ID", "Usuário", "CPF", "Status", "Observação", "Distância", "Data/Hora"])

    for acesso in acessos:
        ws.append([
            acesso["id"],
            acesso["usuario_registro"],
            acesso["cpf"],
            acesso["status"],
            acesso["observacao"],
            acesso["distancia"],
            str(acesso["data_hora"])
        ])

    arquivo = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(arquivo.name)

    return send_file(
        arquivo.name,
        as_attachment=True,
        download_name="registros_acessos.xlsx"
    )