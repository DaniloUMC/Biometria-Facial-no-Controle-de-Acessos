const video = document.getElementById('video');
const imagemInput = document.getElementById('imagem');
const statusFace = document.getElementById('statusFace');
const contador = document.getElementById('contador');

let contadorAtivo = false;
let tempo = 3;
let capturaRealizada = false;

navigator.mediaDevices.getUserMedia({
    video: {
        width: 640,
        height: 480
    }
})
.then(stream => {
    video.srcObject = stream;
})
.catch(() => {
    statusFace.innerText = "❌ Não foi possível acessar a câmera";
});


async function validarRosto() {

    if (capturaRealizada) return;

    const canvas = document.createElement("canvas");
    canvas.width = 400;
    canvas.height = 400;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(video, 0, 0, 400, 400);

    const imagem = canvas.toDataURL("image/jpeg", 0.6);
    try {

        const response = await fetch("/validar_rosto", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                imagem: imagem
            })
        });

        const resultado = await response.json();

        if (!resultado.sucesso) {

            contadorAtivo = false;
            tempo = 3;
            contador.innerText = "";

            statusFace.innerText = "❌ " + resultado.erro;

            return;
        }

        statusFace.innerText = "✅ Rosto validado";

        iniciarContagem(imagem);

    } catch (e) {

        statusFace.innerText = "❌ Erro ao validar biometria";

        contadorAtivo = false;
        tempo = 3;
        contador.innerText = "";
    }
}


function iniciarContagem(imagem) {

    if (contadorAtivo || capturaRealizada) return;

    contadorAtivo = true;

    const interval = setInterval(() => {

        contador.innerText = `📸 Capturando em ${tempo}...`;

        tempo--;

        if (tempo < 0) {

            clearInterval(interval);

            imagemInput.value = imagem;

            capturaRealizada = true;

            contador.innerText = "✅ Captura realizada";

            statusFace.innerText = "✅ Biometria validada com sucesso";

            const tracks = video.srcObject.getTracks();

            tracks.forEach(track => track.stop());

            video.style.display = "none";

            document.querySelector(".oval-frame").style.display = "none";

            document.querySelector(".overlay").style.display = "none";
        }

    }, 1000);
}


setInterval(() => {

    validarRosto();

}, 1500);