from flask import Blueprint, render_template, request, jsonify, session
from models.usuario_model import salvar_usuario
import base64
import numpy as np
import cv2

usuario_bp = Blueprint('usuario', __name__)

# 🧾 ETAPA 1 - CADASTRO
@usuario_bp.route("/")
def cadastro():
    return render_template("cadastro.html")


# 📸 ETAPA 2 - BIOMETRIA
@usuario_bp.route("/biometria", methods=["POST"])
def biometria():

    dados = request.form

    # salva dados na sessão
    session["dados_usuario"] = dict(dados)

    return render_template("biometria.html")


# 💾 SALVAR USUÁRIO FINAL
@usuario_bp.route("/salvar", methods=["POST"])
def salvar():

    dados = session.get("dados_usuario", {})

    if not dados:
        return "Sessão expirada"

    imagem = request.form.get("imagem")
    dados["imagem"] = imagem

    sucesso = salvar_usuario(dados)

    # limpa sessão
    session.pop("dados_usuario", None)

    if not sucesso:
        return "CPF já cadastrado!"

    return "Usuário cadastrado com sucesso!"


# 🧠 VALIDAÇÃO DE ROSTO
@usuario_bp.route("/validar_rosto", methods=["POST"])
def validar_rosto():
    try:
        data = request.get_json()
        imagem = data.get("imagem")

        if not imagem:
            return jsonify({"erro": "Imagem não enviada"})

        # converter base64
        imagem = imagem.split(",")[1]
        imagem_bytes = base64.b64decode(imagem)

        np_arr = np.frombuffer(imagem_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"erro": "Imagem inválida"})

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # detectores
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        rosto_detectado = False
        rosto_centralizado = False
        olhos_detectados = False

        h, w = gray.shape

        for (x, y, fw, fh) in faces:
            rosto_detectado = True

            # 🎯 centro do rosto
            centro_x = x + fw // 2
            centro_y = y + fh // 2

            # 🎯 centro da tela
            tela_x = w // 2
            tela_y = h // 2

            # tolerância
            margem_x = w * 0.15
            margem_y = h * 0.20

            if (abs(centro_x - tela_x) < margem_x and
                abs(centro_y - tela_y) < margem_y):
                rosto_centralizado = True

            # 👀 olhos
            roi_gray = gray[y:y+fh, x:x+fw]
            olhos = eye_cascade.detectMultiScale(roi_gray)

            if len(olhos) >= 2:
                olhos_detectados = True

            break

        return jsonify({
            "rosto_detectado": rosto_detectado,
            "rosto_centralizado": rosto_centralizado,
            "olhos_detectados": olhos_detectados
        })

    except Exception as e:
        print("Erro ao processar imagem:", e)
        return jsonify({
            "erro": "Erro ao processar imagem",
            "rosto_detectado": False,
            "rosto_centralizado": False,
            "olhos_detectados": False
        })