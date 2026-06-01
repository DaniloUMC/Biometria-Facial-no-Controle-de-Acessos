from services.liveness_service import validar_variacao_frames


def test_liveness_sem_frames():
    resultado = validar_variacao_frames([])

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Amostras insuficientes"


def test_liveness_frames_invalidos():
    frames = [
        "imagem_invalida",
        "imagem_invalida",
        "imagem_invalida"
    ]

    resultado = validar_variacao_frames(frames)

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Não foi possível processar os frames"