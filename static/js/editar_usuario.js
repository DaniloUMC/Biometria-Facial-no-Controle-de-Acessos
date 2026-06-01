const formEditar = document.getElementById("formEditarUsuario");
const cepInput = document.getElementById("cep");
const emailInput = document.getElementById("email");
const nomeInput = document.getElementById("nome");
const ruaInput = document.getElementById("rua");
const numeroInput = document.getElementById("numero");
const bairroInput = document.getElementById("bairro");
const cidadeInput = document.getElementById("cidade");
const estadoInput = document.getElementById("estado");

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const btnCapturarFoto = document.getElementById("btnCapturarFoto");
const btnTirarOutra = document.getElementById("btnTirarOutra");
const statusFoto = document.getElementById("statusFoto");
const previewFoto = document.getElementById("previewFoto");
const imagemCapturada = document.getElementById("imagemCapturada");

let streamAtual = null;
let novaImagem = null;

function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function marcarInvalido(campo) {
    campo.classList.add("is-invalid");
    campo.classList.remove("is-valid");
}

function marcarValido(campo) {
    campo.classList.remove("is-invalid");
    campo.classList.add("is-valid");
}

function campoVazio(campo) {
    return !campo.value || campo.value.trim() === "";
}

function validarCampoObrigatorio(campo) {
    if (campoVazio(campo)) {
        marcarInvalido(campo);
        return false;
    }

    marcarValido(campo);
    return true;
}

function validarFormularioEdicao() {
    let valido = true;

    const camposObrigatorios = [
        nomeInput,
        emailInput,
        cepInput,
        ruaInput,
        numeroInput,
        bairroInput,
        cidadeInput,
        estadoInput
    ];

    camposObrigatorios.forEach(campo => {
        if (!validarCampoObrigatorio(campo)) {
            valido = false;
        }
    });

    if (!validarEmail(emailInput.value)) {
        marcarInvalido(emailInput);
        valido = false;
    } else {
        marcarValido(emailInput);
    }

    if (!valido) {
        alert("Preencha todos os campos obrigatórios corretamente.");
    }

    return valido;
}

async function buscarCep() {
    const cep = cepInput.value.replace(/\D/g, "");

    if (cep.length !== 8) return;

    try {
        const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
        const data = await response.json();

        if (data.erro) {
            alert("CEP não encontrado. Preencha o endereço manualmente.");
            return;
        }

        ruaInput.value = data.logradouro || "";
        bairroInput.value = data.bairro || "";
        cidadeInput.value = data.localidade || "";
        estadoInput.value = data.uf || "";

        validarCampoObrigatorio(ruaInput);
        validarCampoObrigatorio(bairroInput);
        validarCampoObrigatorio(cidadeInput);
        validarCampoObrigatorio(estadoInput);

    } catch (e) {
        alert("Erro ao buscar CEP. Preencha manualmente.");
    }
}

async function iniciarCamera() {
    try {
        streamAtual = await navigator.mediaDevices.getUserMedia({
            video: {
                width: 640,
                height: 480
            }
        });

        video.srcObject = streamAtual;
        video.style.display = "block";
        previewFoto.style.display = "none";
        btnCapturarFoto.style.display = "inline-block";
        btnTirarOutra.style.display = "none";
        statusFoto.innerText = "Posicione o rosto para atualizar a imagem.";

    } catch (e) {
        statusFoto.innerText = "Não foi possível acessar a câmera.";
    }
}

function pararCamera() {
    if (streamAtual) {
        streamAtual.getTracks().forEach(track => track.stop());
        streamAtual = null;
    }

    video.srcObject = null;
}

btnCapturarFoto.addEventListener("click", function () {
    const ctx = canvas.getContext("2d");

    canvas.width = 400;
    canvas.height = 400;

    ctx.drawImage(video, 0, 0, 400, 400);

    novaImagem = canvas.toDataURL("image/jpeg", 0.7);
    imagemCapturada.value = novaImagem;

    pararCamera();

    previewFoto.src = novaImagem;
    previewFoto.style.display = "block";
    video.style.display = "none";
    btnCapturarFoto.style.display = "none";
    btnTirarOutra.style.display = "inline-block";
    statusFoto.innerText = "Nova imagem capturada. Clique em Salvar Alterações para confirmar.";
});

btnTirarOutra.addEventListener("click", function () {
    novaImagem = null;
    imagemCapturada.value = "";
    previewFoto.src = "";
    iniciarCamera();
});

if (cepInput) {
    cepInput.addEventListener("blur", buscarCep);
}

if (emailInput) {
    emailInput.addEventListener("input", function () {
        if (validarEmail(this.value)) {
            marcarValido(this);
        } else {
            marcarInvalido(this);
        }
    });
}

[
    nomeInput,
    cepInput,
    ruaInput,
    numeroInput,
    bairroInput,
    cidadeInput,
    estadoInput
].forEach(campo => {
    if (campo) {
        campo.addEventListener("input", function () {
            validarCampoObrigatorio(this);
        });
    }
});

if (formEditar) {
    formEditar.addEventListener("submit", function (e) {
        if (!validarFormularioEdicao()) {
            e.preventDefault();
            return;
        }

        imagemCapturada.value = novaImagem || "";
    });
}

iniciarCamera();