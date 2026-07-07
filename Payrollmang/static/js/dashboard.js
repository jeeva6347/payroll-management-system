document.addEventListener("DOMContentLoaded", function () {

    function createBarChart(canvasId, title, color) {

        const canvas = document.getElementById(canvasId);

        if (!canvas) return;

        const labels = JSON.parse(canvas.dataset.labels || "[]");
        const values = JSON.parse(canvas.dataset.values || "[]");

        new Chart(canvas, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{
                    label: title,
                    data: values,

                    backgroundColor: color,
                    hoverBackgroundColor: color,

                    borderRadius: 8,
                    borderSkipped: false,

                    maxBarThickness: 45,
                    barPercentage: 0.7,
                    categoryPercentage: 0.7,

                }]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                animation: {
                    duration: 1200,
                    easing: "easeOutQuart"
                },

                plugins: {

                    legend: {
                        display: false
                    },

                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 18,
                            weight: "bold"
                        },
                        color: "#333",
                        padding: {
                            bottom: 20
                        }
                    },

                    tooltip: {

                        backgroundColor: "#222",

                        titleColor: "#fff",

                        bodyColor: "#fff",

                        callbacks: {

                            label: function (context) {

                                return "₹ " + Number(context.raw).toLocaleString("en-IN");

                            }

                        }

                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        },

                        ticks: {
                            color: "#666",
                            font: {
                                size: 12
                            }
                        }

                    },

                    y: {

                        beginAtZero: true,

                        grid: {
                            color: "#eeeeee"
                        },

                        ticks: {

                            color: "#666",

                            callback: function (value) {

                                return "₹ " + Number(value).toLocaleString("en-IN");

                            }

                        }

                    }

                }

            }

        });

    }


    createBarChart(
        "monthlyChart",
        "Monthly Salary Spend",
        "#2563eb"
    );


    createBarChart(
        "yearlyChart",
        "Yearly Salary Spend",
        "#22c55e"
    );

});