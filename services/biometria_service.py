import base64
import numpy as np
import cv2


def validar_face(imagem):

    try:

        if not imagem:
            return {
                "erro": "Imagem não enviada"
            }

        imagem = imagem.split(",")[1]

        imagem_bytes = base64.b64decode(imagem)

        np_arr = np.frombuffer(imagem_bytes, np.uint8)

        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return {
                "erro": "Imagem inválida"
            }

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

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

            centro_x = x + fw // 2
            centro_y = y + fh // 2

            tela_x = w // 2
            tela_y = h // 2

            margem_x = w * 0.15
            margem_y = h * 0.20

            if (
                abs(centro_x - tela_x) < margem_x and
                abs(centro_y - tela_y) < margem_y
            ):
                rosto_centralizado = True

            roi_gray = gray[y:y + fh, x:x + fw]

            olhos = eye_cascade.detectMultiScale(roi_gray)

            if len(olhos) >= 2:
                olhos_detectados = True

            break

        return {
            "rosto_detectado": rosto_detectado,
            "rosto_centralizado": rosto_centralizado,
            "olhos_detectados": olhos_detectados
        }

    except Exception as e:

        print(e)

        return {
            "erro": "Erro ao processar imagem",
            "rosto_detectado": False,
            "rosto_centralizado": False,
            "olhos_detectados": False
        }