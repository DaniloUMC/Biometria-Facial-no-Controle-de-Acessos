document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("formCadastro");

    const cpfInput = document.getElementById("cpf");
    const anoInput = document.getElementById("ano");
    const cepInput = document.getElementById("cep");
    const emailInput = document.getElementById("email");

    if (cpfInput) {

        cpfInput.addEventListener("input", function () {

            const cpf = this.value;

            if (cpf.length >= 11) {

                if (!validarCPF(cpf)) {

                    this.classList.add("is-invalid");
                    this.classList.remove("is-valid");

                } else {

                    this.classList.remove("is-invalid");
                    this.classList.add("is-valid");
                }

            } else {

                this.classList.remove("is-invalid");
                this.classList.remove("is-valid");
            }

        });

    }

    if (anoInput) {

        anoInput.addEventListener("input", function () {

            const ano = this.value;

            if (ano.length === 4) {

                if (!validarAno(ano)) {

                    this.classList.add("is-invalid");
                    this.classList.remove("is-valid");

                } else {

                    this.classList.remove("is-invalid");
                    this.classList.add("is-valid");
                }

            } else {

                this.classList.remove("is-invalid");
                this.classList.remove("is-valid");
            }

        });

    }

    if (emailInput) {

        emailInput.addEventListener("input", function () {

            const email = this.value;

            if (email.length > 5) {

                if (!validarEmail(email)) {

                    this.classList.add("is-invalid");
                    this.classList.remove("is-valid");

                } else {

                    this.classList.remove("is-invalid");
                    this.classList.add("is-valid");
                }

            } else {

                this.classList.remove("is-invalid");
                this.classList.remove("is-valid");
            }

        });

    }

    if (cepInput) {

        cepInput.addEventListener("blur", async function () {

            let cep = this.value.replace(/\D/g, '');

            if (cep.length !== 8) return;

            try {

                const response = await fetch(
                    `https://viacep.com.br/ws/${cep}/json/`
                );

                const data = await response.json();

                if (data.erro) {

                    alert("CEP não encontrado.");

                    return;
                }

                document.getElementById("rua").value =
                    data.logradouro || "";

                document.getElementById("bairro").value =
                    data.bairro || "";

                document.getElementById("cidade").value =
                    data.localidade || "";

                document.getElementById("estado").value =
                    data.uf || "";

            } catch (e) {

                alert("Erro ao buscar CEP.");
            }

        });

    }

    if (form) {

        form.addEventListener("submit", function (e) {

            const cpf = cpfInput.value;
            const ano = anoInput.value;
            const email = emailInput.value;

            const senha =
                document.getElementById("senha").value;

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

                alert(
                    "A senha deve possuir no mínimo 8 caracteres."
                );

                return;
            }

        });

    }

});

function validarCPF(cpf) {

    cpf = cpf.replace(/[^\d]+/g, '');

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

    const regex =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return regex.test(email);
}