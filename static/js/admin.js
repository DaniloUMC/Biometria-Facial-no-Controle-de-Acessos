document.addEventListener("DOMContentLoaded", function () {

    const dadosJson = document.getElementById("dadosGrafico");

    if (!dadosJson) return;

    const dados = JSON.parse(dadosJson.textContent);

    const labels = dados.labels.reverse();
    const valores = dados.valores.reverse();

    const canvas = document.getElementById("graficoAcessos");

    if (!canvas) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Acessos",
                    data: valores
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

});