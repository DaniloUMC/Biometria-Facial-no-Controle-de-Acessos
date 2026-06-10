document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("formCadastro");

    const cpfInput = document.getElementById("cpf");
    const anoInput = document.getElementById("ano");
    const cepInput = document.getElementById("cep");
    const emailInput = document.getElementById("email");
    const lgpdInput = document.getElementById("consentimento_lgpd");

    if (cpfInput) {
        cpfInput.addEventListener("input", function () {
            const cpf = this.value;

            if (cpf.length >= 11) {
                alternarValidacao(this, validarCPF(cpf));
            } else {
                limparValidacao(this);
            }
        });
    }

    if (anoInput) {
        anoInput.addEventListener("input", function () {
            const ano = this.value;

            if (ano.length === 4) {
                alternarValidacao(this, validarAno(ano));
            } else {
                limparValidacao(this);
            }
        });
    }

    if (emailInput) {
        emailInput.addEventListener("input", function () {
            const email = this.value;

            if (email.length > 5) {
                alternarValidacao(this, validarEmail(email));
            } else {
                limparValidacao(this);
            }
        });
    }

    if (cepInput) {
        cepInput.addEventListener("blur", buscarCepComContingencia);
    }

    if (form) {
        form.addEventListener("submit", function (e) {

            const cpf = cpfInput.value;
            const ano = anoInput.value;
            const email = emailInput.value;
            const senha = document.getElementById("senha").value;

            if (!validarCPF(cpf)) {
                e.preventDefault();
                alert("CPF inválido.");
                return;
            }

            if (!validarAno(ano)) {
                e.preventDefault();
                alert("Idade inválida.");
                return;
            }

            if (!validarEmail(email)) {
                e.preventDefault();
                alert("Email inválido.");
                return;
            }

            if (!validarSenha(senha)) {
                e.preventDefault();
                alert("A senha deve possuir no mínimo 8 caracteres.");
                return;
            }

            if (lgpdInput && !lgpdInput.checked) {
                e.preventDefault();
                alert("É necessário aceitar o termo de consentimento LGPD para continuar.");
                return;
            }
        });
    }
});

async function buscarCepComContingencia() {
    const cepInput = document.getElementById("cep");
    const cep = cepInput.value.replace(/\D/g, "");

    if (cep.length !== 8) {
        return;
    }

    try {
        bloquearEndereco(true);

        const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);

        if (!response.ok) {
            throw new Error("API de CEP indisponível.");
        }

        const data = await response.json();

        if (data.erro) {
            throw new Error("CEP não encontrado.");
        }

        preencherEndereco(data);
        bloquearEndereco(false);

    } catch (erro) {
        console.log("Falha ao consultar CEP:", erro.message);

        limparEndereco();
        liberarEnderecoManual();

        alert(
            "Não foi possível consultar o CEP automaticamente. " +
            "Preencha o endereço manualmente para continuar."
        );
    }
}

function preencherEndereco(data) {
    const rua = document.getElementById("rua");
    const bairro = document.getElementById("bairro");
    const cidade = document.getElementById("cidade");
    const estado = document.getElementById("estado");

    if (rua) rua.value = data.logradouro || "";
    if (bairro) bairro.value = data.bairro || "";
    if (cidade) cidade.value = data.localidade || "";
    if (estado) estado.value = data.uf || "";
}

function limparEndereco() {
    const campos = ["rua", "bairro", "cidade", "estado"];

    campos.forEach(function (id) {
        const campo = document.getElementById(id);

        if (campo) {
            campo.value = "";
        }
    });
}

function bloquearEndereco(bloquear) {
    const campos = ["rua", "bairro", "cidade", "estado"];

    campos.forEach(function (id) {
        const campo = document.getElementById(id);

        if (campo) {
            campo.readOnly = bloquear;
            campo.disabled = false;
        }
    });
}

function liberarEnderecoManual() {
    const campos = ["rua", "bairro", "cidade", "estado"];

    campos.forEach(function (id) {
        const campo = document.getElementById(id);

        if (campo) {
            campo.readOnly = false;
            campo.disabled = false;
            campo.classList.remove("is-invalid");
            campo.classList.remove("is-valid");
        }
    });
}

function alternarValidacao(campo, valido) {
    if (valido) {
        campo.classList.remove("is-invalid");
        campo.classList.add("is-valid");
    } else {
        campo.classList.add("is-invalid");
        campo.classList.remove("is-valid");
    }
}

function limparValidacao(campo) {
    campo.classList.remove("is-invalid");
    campo.classList.remove("is-valid");
}

function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, "");

    if (cpf.length !== 11) return false;
    if (/^(\d)\1+$/.test(cpf)) return false;

    let soma = 0;

    for (let i = 0; i < 9; i++) {
        soma += parseInt(cpf.charAt(i)) * (10 - i);
    }

    let resto = (soma * 10) % 11;

    if (resto === 10 || resto === 11) resto = 0;

    if (resto !== parseInt(cpf.charAt(9))) {
        return false;
    }

    soma = 0;

    for (let i = 0; i < 10; i++) {
        soma += parseInt(cpf.charAt(i)) * (11 - i);
    }

    resto = (soma * 10) % 11;

    if (resto === 10 || resto === 11) resto = 0;

    return resto === parseInt(cpf.charAt(10));
}

function validarAno(ano) {
    const anoAtual = new Date().getFullYear();
    const idade = anoAtual - parseInt(ano);

    return idade >= 18 && idade <= 100;
}

function validarSenha(senha) {
    return senha.length >= 8;
}

function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return regex.test(email);
}