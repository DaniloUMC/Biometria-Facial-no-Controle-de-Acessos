const video = document.getElementById("video");
const statusFace = document.getElementById("statusFace");
const canvas = document.getElementById("canvas");

let processando = false;
let finalizado = false;

navigator.mediaDevices.getUserMedia({
    video: {
        width: 640,
        height: 480
    }
})
.then(stream => {
    video.srcObject = stream;
    setTimeout(iniciarValidacao, 1500);
})
.catch(() => {
    statusFace.innerText = "Não foi possível acessar a câmera";
});

function capturarFrame() {
    const ctx = canvas.getContext("2d");

    canvas.width = 400;
    canvas.height = 400;

    ctx.drawImage(video, 0, 0, 400, 400);

    return canvas.toDataURL("image/jpeg", 0.7);
}

async function iniciarValidacao() {
    if (processando || finalizado) return;

    processando = true;
    statusFace.innerText = "Movimente levemente o rosto para validar presença real";

    const frames = [];

    const intervalo = setInterval(() => {
        frames.push(capturarFrame());
    }, 300);

    setTimeout(async () => {
        clearInterval(intervalo);

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
                statusFace.innerText = resultado.mensagem;
                processando = false;

                setTimeout(iniciarValidacao, 2500);
                return;
            }

            statusFace.innerText = "Presença real validada. Reconhecendo usuário...";

            reconhecerEntrada();

        } catch (e) {
            statusFace.innerText = "Erro ao validar presença real";
            processando = false;
        }

    }, 2500);
}

async function reconhecerEntrada() {
    const imagem = capturarFrame();

    try {
        const response = await fetch("/reconhecer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ imagem: imagem })
        });

        const resultado = await response.json();

        if (resultado.sucesso) {
            finalizado = true;

            statusFace.innerText = `Acesso permitido. Bem-vindo, ${resultado.nome}!`;

            const tracks = video.srcObject.getTracks();
            tracks.forEach(track => track.stop());

            video.style.display = "none";

            const oval = document.querySelector(".oval-frame");
            const overlay = document.querySelector(".overlay");

            if (oval) oval.style.display = "none";
            if (overlay) overlay.style.display = "none";

            return;
        }

        statusFace.innerText = resultado.mensagem;
        processando = false;

        setTimeout(iniciarValidacao, 2500);

    } catch (e) {
        statusFace.innerText = "Erro ao tentar reconhecer usuário";
        processando = false;
    }
}