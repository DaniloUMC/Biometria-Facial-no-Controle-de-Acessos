import base64
import cv2
import numpy as np


def base64_para_gray(frame):
    if not frame or "," not in frame:
        return None

    frame = frame.split(",")[1]
    imagem_bytes = base64.b64decode(frame)

    np_arr = np.frombuffer(imagem_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (200, 200))

    return gray


def validar_variacao_frames(frames):
    try:
        if not frames or len(frames) < 3:
            return {
                "sucesso": False,
                "mensagem": "Amostras insuficientes"
            }

        imagens = []

        for frame in frames:
            gray = base64_para_gray(frame)

            if gray is not None:
                imagens.append(gray)

        if len(imagens) < 3:
            return {
                "sucesso": False,
                "mensagem": "Não foi possível processar os frames"
            }

        diferencas = []

        for i in range(len(imagens) - 1):
            diff = cv2.absdiff(imagens[i], imagens[i + 1])
            media = np.mean(diff)
            diferencas.append(media)

        media_variacao = float(np.mean(diferencas))

        if media_variacao < 1.5:
            return {
                "sucesso": False,
                "mensagem": "Imagem estática detectada. Movimente levemente o rosto"
            }

        if media_variacao > 35:
            return {
                "sucesso": False,
                "mensagem": "Movimento excessivo. Fique mais estável"
            }

        return {
            "sucesso": True,
            "mensagem": "Prova de vida validada",
            "variacao": media_variacao
        }

    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": "Erro na validação de prova de vida",
            "erro": str(e)
        }