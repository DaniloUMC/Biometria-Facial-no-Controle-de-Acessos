import base64
import numpy as np
import cv2


def validar_face(imagem):

    try:

        if not imagem:
            return {
                "sucesso": False,
                "erro": "Imagem não enviada"
            }

        if "," not in imagem:
            return {
                "sucesso": False,
                "erro": "Formato de imagem inválido"
            }

        try:
            imagem = imagem.split(",")[1]
            imagem_bytes = base64.b64decode(imagem)

        except Exception:
            return {
                "sucesso": False,
                "erro": "Erro ao decodificar imagem"
            }

        np_arr = np.frombuffer(imagem_bytes, np.uint8)

        if np_arr.size == 0:
            return {
                "sucesso": False,
                "erro": "Imagem vazia"
            }

        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return {
                "sucesso": False,
                "erro": "Imagem inválida"
            }

        altura, largura = img.shape[:2]

        if largura < 300 or altura < 300:
            return {
                "sucesso": False,
                "erro": "Qualidade da câmera insuficiente"
            }

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        brilho = np.mean(gray)

        if brilho < 40:
            return {
                "sucesso": False,
                "erro": "Ambiente com pouca iluminação"
            }

        if brilho > 220:
            return {
                "sucesso": False,
                "erro": "Excesso de iluminação"
            }

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml'
        )
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=6,
            minSize=(120, 120)
        )

        if len(faces) == 0:
            return {
                "sucesso": False,
                "erro": "Nenhum rosto detectado"
            }

        if len(faces) > 1:
            return {
                "sucesso": False,
                "erro": "Mais de um rosto detectado"
            }

        h, w = gray.shape

        for (x, y, fw, fh) in faces:

            area_rosto = fw * fh
            area_total = w * h

            proporcao = area_rosto / area_total

            if proporcao < 0.08:
                return {
                    "sucesso": False,
                    "erro": "Aproxime o rosto da câmera"
                }

            if proporcao > 0.60:
                return {
                    "sucesso": False,
                    "erro": "Afaste o rosto da câmera"
                }

            centro_x = x + fw // 2
            centro_y = y + fh // 2

            tela_x = w // 2
            tela_y = h // 2

            margem_x = w * 0.15
            margem_y = h * 0.20

            if (
                abs(centro_x - tela_x) > margem_x or
                abs(centro_y - tela_y) > margem_y
            ):
                return {
                    "sucesso": False,
                    "erro": "Centralize o rosto"
                }

            roi_gray = gray[y:y + fh, x:x + fw]

            altura_rosto = roi_gray.shape[0]
            regiao_olhos = roi_gray[0:int(altura_rosto * 0.55), :]

            olhos = eye_cascade.detectMultiScale(
                regiao_olhos,
                scaleFactor=1.1,
                minNeighbors=10,
                minSize=(25, 25)
            )

            if len(olhos) < 2:
                return {
                    "sucesso": False,
                    "erro": "Mantenha os olhos abertos e visíveis"
            }

            return {
                "sucesso": True,
                "rosto_detectado": True,
                "rosto_centralizado": True,
                "olhos_detectados": True
            }

        return {
            
            "erro": "Falha inesperada na validação facial"
        }

    except cv2.error:
        return {
            "sucesso": False,
            "erro": "Erro interno do OpenCV"
        }

    except MemoryError:
        return {
            "sucesso": False,
            "erro": "Memória insuficiente para processamento"
        }

    except Exception:
        return {
            "sucesso": False,
            "erro": "Erro interno no processamento biométrico"
        }