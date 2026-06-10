const video = document.getElementById("video");
const statusFace = document.getElementById("statusFace");
const canvas = document.getElementById("canvas");

let processando = false;
let finalizado = false;
let tempoInicioValidacao = null;
let streamCamera = null;

const TEMPO_LIMITE_VALIDACAO = 20000;
const TEMPO_REINICIO = 2500;

const mensagensAdministracao = {
    camera_indisponivel: "Câmera indisponível. Procure a administração.",
    permissao_negada: "Permissão da câmera bloqueada. Procure a administração.",
    nao_reconhecido: "Não foi possível validar sua identidade automaticamente. Procure a administração do evento.",
    erro_biometria: "Erro na validação biométrica. Procure a administração.",
    evento_invalido: "Participante não autorizado para este evento. Procure a administração.",
    lgpd_pendente: "Consentimento LGPD pendente. Procure a administração.",
    sem_foto: "Biometria não encontrada. Procure a administração.",
    erro_sistema: "Erro no sistema de validação. Procure a administração."
};

iniciarCamera();

async function iniciarCamera() {
    try {
        resetarInterface();

        streamCamera = await navigator.mediaDevices.getUserMedia({
            video: {
                width: 640,
                height: 480
            }
        });

        video.srcObject = streamCamera;

        tempoInicioValidacao = Date.now();
        processando = false;
        finalizado = false;

        statusFace.innerText = "Câmera iniciada. Posicione o rosto na moldura.";

        setTimeout(iniciarValidacao, 1500);

    } catch (erro) {
        if (erro.name === "NotAllowedError" || erro.name === "PermissionDeniedError") {
            mostrarMensagemAdministracao(mensagensAdministracao.permissao_negada);
            return;
        }

        mostrarMensagemAdministracao(mensagensAdministracao.camera_indisponivel);
    }
}

function capturarFrame() {
    const ctx = canvas.getContext("2d");

    canvas.width = 400;
    canvas.height = 400;

    ctx.drawImage(video, 0, 0, 400, 400);

    return canvas.toDataURL("image/jpeg", 0.7);
}

async function iniciarValidacao() {
    if (processando || finalizado) return;

    if (tempoEsgotado()) {
        mostrarMensagemAdministracao(mensagensAdministracao.nao_reconhecido);
        reiniciarParaProximoParticipante();
        return;
    }

    processando = true;
    statusFace.innerText = "Validando presença real. Movimente levemente o rosto.";

    const frames = [];

    const intervalo = setInterval(() => {
        if (!finalizado && video.srcObject) {
            frames.push(capturarFrame());
        }
    }, 300);

    setTimeout(async () => {
        clearInterval(intervalo);

        if (finalizado) return;

        if (tempoEsgotado()) {
            processando = false;
            mostrarMensagemAdministracao(mensagensAdministracao.nao_reconhecido);
            reiniciarParaProximoParticipante();
            return;
        }

        try {
            const response = await fetch("/validar_liveness", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ frames: frames })
            });

            const resultado = await response.json();

            if (!resultado.sucesso) {
                statusFace.innerText = resultado.mensagem || "Não foi possível validar presença real.";
                processando = false;

                setTimeout(iniciarValidacao, TEMPO_REINICIO);
                return;
            }

            statusFace.innerText = "Presença real validada. Reconhecendo usuário...";
            await reconhecerEntrada();

        } catch (erro) {
            statusFace.innerText = "Erro ao validar presença real. Tentando novamente.";
            processando = false;

            setTimeout(iniciarValidacao, TEMPO_REINICIO);
        }

    }, 2500);
}

async function reconhecerEntrada() {
    if (finalizado) return;

    if (tempoEsgotado()) {
        processando = false;
        mostrarMensagemAdministracao(mensagensAdministracao.nao_reconhecido);
        reiniciarParaProximoParticipante();
        return;
    }

    const imagem = capturarFrame();

    try {
        const response = await fetch("/reconhecer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                imagem: imagem,
                evento_id: 1
            })
        });

        const resultado = await response.json();

        if (resultado.sucesso) {
            finalizado = true;

            statusFace.innerText = `Acesso permitido. Bem-vindo, ${resultado.nome}!`;

            setTimeout(() => {
                reiniciarParaProximoParticipante();
            }, 3000);

            return;
        }

        tratarFalhaReconhecimento(resultado);

    } catch (erro) {
        processando = false;
        mostrarMensagemAdministracao(mensagensAdministracao.erro_sistema);

        setTimeout(() => {
            reiniciarParaProximoParticipante();
        }, TEMPO_REINICIO);
    }
}

function tratarFalhaReconhecimento(resultado) {
    processando = false;

    const tipo = resultado.tipo || "NAO_RECONHECIDO";

    switch (tipo) {
        case "EVENTO_NAO_AUTORIZADO":
            mostrarMensagemAdministracao(mensagensAdministracao.evento_invalido);
            reiniciarParaProximoParticipante();
            break;

        case "LGPD_PENDENTE":
            mostrarMensagemAdministracao(mensagensAdministracao.lgpd_pendente);
            reiniciarParaProximoParticipante();
            break;

        case "SEM_FOTO_BIOMETRICA":
            mostrarMensagemAdministracao(mensagensAdministracao.sem_foto);
            reiniciarParaProximoParticipante();
            break;
        case "EVENTO_CANCELADO":
            mostrarMensagemAdministracao("Participação no evento cancelada. Procure a administração.");
            reiniciarParaProximoParticipante();
            break;

        case "ERRO_BIOMETRIA":
        case "ERRO_RECONHECIMENTO":
            mostrarMensagemAdministracao(mensagensAdministracao.erro_biometria);
            reiniciarParaProximoParticipante();
            break;

        case "SEM_CADASTROS":
            mostrarMensagemAdministracao(resultado.mensagem || "Nenhum cadastro localizado. Procure a administração.");
            reiniciarParaProximoParticipante();
            break;

        case "NAO_RECONHECIDO":
        default:
            statusFace.innerText = resultado.mensagem || mensagensAdministracao.nao_reconhecido;

            if (tempoEsgotado()) {
                mostrarMensagemAdministracao(mensagensAdministracao.nao_reconhecido);
                reiniciarParaProximoParticipante();
                return;
            }

            setTimeout(iniciarValidacao, TEMPO_REINICIO);
            break;
    }
}

function tempoEsgotado() {
    if (!tempoInicioValidacao) return false;

    return Date.now() - tempoInicioValidacao >= TEMPO_LIMITE_VALIDACAO;
}

function mostrarMensagemAdministracao(mensagem) {
    statusFace.innerText = "⚠️ " + mensagem;
}

function reiniciarParaProximoParticipante() {
    pararCamera();

    setTimeout(() => {
        processando = false;
        finalizado = false;
        tempoInicioValidacao = null;
        iniciarCamera();
    }, 2500);
}

function pararCamera() {
    if (streamCamera) {
        streamCamera.getTracks().forEach(track => track.stop());
        streamCamera = null;
    }

    if (video) {
        video.srcObject = null;
    }
}

function resetarInterface() {
    video.style.display = "block";

    const oval = document.querySelector(".oval-frame");
    const overlay = document.querySelector(".overlay");

    if (oval) oval.style.display = "block";
    if (overlay) overlay.style.display = "block";
}