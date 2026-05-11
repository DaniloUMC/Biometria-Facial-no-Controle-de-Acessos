const video = document.getElementById('video');

let contadorAtivo = false;
let tempo = 3;


navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    });


    


setInterval(async () => {

    if (!video.srcObject) return;

    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    ctx.drawImage(video, 0, 0, 300, 200);
    const dataURL = canvas.toDataURL('image/png');

    const response = await fetch("/validar_rosto", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ imagem: dataURL })
    });

    const result = await response.json();

    const status = document.getElementById("statusFace");


    if (!result.rosto_detectado) {
        status.innerText = "🔴 Nenhum rosto detectado";
        resetarContagem();
        return;
    }

    
    if (!result.rosto_centralizado) {
        status.innerText = "⚠️ Centralize o rosto na moldura";
        resetarContagem();
        return;
    }

    if (!result.olhos_detectados) {
        status.innerText = " Abraa os olhos";
        resetarContagem();
        return;
    }

    
    status.innerText = "🟢 Rosto válido";

    if (!contadorAtivo) iniciarContagem();

}, 1000);




function iniciarContagem() {

    contadorAtivo = true;
    tempo = 3;

    const contadorEl = document.getElementById("contador");

    const interval = setInterval(() => {

        contadorEl.innerText = `📸 Capturando em ${tempo}...`;

        tempo--;

        if (tempo < 0) {
            clearInterval(interval);
            capturarFinal();
        }

    
        if (!contadorAtivo) {
            clearInterval(interval);
        }

    }, 1000);
}

function resetarContagem() {
    contadorAtivo = false;
    document.getElementById("contador").innerText = "";
}


function capturarFinal() {

    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    ctx.drawImage(video, 0, 0, 300, 200);

    const dataURL = canvas.toDataURL('image/png');
    document.getElementById("imagem").value = dataURL;

    document.getElementById("statusFace").innerText = "✅ Capturado!";

    // DESLIGA CÂMERA
    const stream = video.srcObject;
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }

    // ESCONDE ÁREA DA CÂMERA
    document.getElementById("cameraArea").style.display = "none";
}



document.getElementById("cep").addEventListener("blur", function () {

    let cep = this.value.replace(/\D/g, '');

    if (cep.length !== 8) return;

    fetch(`https://viacep.com.br/ws/${cep}/json/`)
        .then(res => res.json())
        .then(data => {

            if (data.erro) {
                alert("CEP não encontrado. Preencha manualmente.");
                return;
            }

            document.getElementById("rua").value = data.logradouro || "";
            document.getElementById("bairro").value = data.bairro || "";
            document.getElementById("cidade").value = data.localidade || "";
            document.getElementById("estado").value = data.uf || "";

        })
        .catch(() => {
            alert("Erro ao buscar CEP. Preencha manualmente.");
        });

});



function validarFormulario() {

    const cpf = document.getElementById("cpf").value;
    const ano = document.getElementById("ano").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;
    const confirmar = document.getElementById("confirmarSenha").value;

    if (!validarCPF(cpf)) {
        alert("CPF inválido!");
        return false;
    }

    if (!validarAno(ano)) {
        alert("Ano inválido! (1920 até atual)");
        return false;
    }

      
    if (!email.includes("@") || !email.includes(".")) {
        alert("Email inválido!");
        return false;
    }

    if (senha.length < 6) {
        alert("A sennha deve ter no mínimo 6 caracteres");
        return false;
    }

    if (senha !== confirmar) {
        alert("As senhas não coincideem");
        return false;
    }

    return true;
}

// CPF
function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g,'');

    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;

    let soma = 0;
    for (let i = 0; i < 9; i++)
        soma += parseInt(cpf.charAt(i)) * (10 - i);

    let resto = (soma * 10) % 11;
    if (resto == 10 || resto == 11) resto = 0;
    if (resto != parseInt(cpf.charAt(9))) return false;

    soma = 0;
    for (let i = 0; i < 10; i++)
        soma += parseInt(cpf.charAt(i)) * (11 - i);

    resto = (soma * 10) % 11;
    if (resto == 10 || resto == 11) resto = 0;

    return resto == parseInt(cpf.charAt(10));
}

// ANO (1920 até atual)
function validarAno(ano) {
    const atual = new Date().getFullYear();
    return ano >= 1920 && ano <= atual;
}