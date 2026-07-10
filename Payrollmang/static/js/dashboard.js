document.addEventListener("DOMContentLoaded", function () {

    function buildBarOptions(title) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1200,
                easing: "easeOutQuart"
            },
            plugins: {
                legend: {
                    display: true,
                    position: "top",
                    onClick: null,
                    labels: {
                        color: "#333",
                        usePointStyle: true,
                        pointStyle: "rectRounded"
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
        };
    }

    function createBarChart(canvasId, title, color, labels, values) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const datasets = [{
            label: title,
            type: "bar",
            data: values,
            backgroundColor: color,
            hoverBackgroundColor: color,
            borderRadius: 8,
            borderSkipped: false,
            maxBarThickness: 45,
            barPercentage: 0.7,
            categoryPercentage: 0.7,
        }];

        return new Chart(canvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: datasets
            },
            options: buildBarOptions(title)
        });
    }

    function createToggleChart(canvasId, selectId, monthlyTitle, weeklyTitle, monthlyColor, weeklyColor) {
        const canvas = document.getElementById(canvasId);
        const select = document.getElementById(selectId);
        if (!canvas || !select) return;

        const labels = JSON.parse(canvas.dataset.labels || "[]");
        const monthlyValues = JSON.parse(canvas.dataset.values || "[]");
        const weeklyValues = JSON.parse(canvas.dataset.weeklyValues || "[]");

        const summaryLabel = document.querySelector('.spend-card-label');
        const summaryAmount = document.querySelector('.spend-card-amount');
        const summaryBadge = document.querySelector('.spend-card-badge');

        const chart = createBarChart(canvasId, monthlyTitle, monthlyColor, labels, monthlyValues);
        if (!chart) return;

        const cardHeader = canvas.closest('.card')?.querySelector('h5.mb-0');
        if (cardHeader) {
            cardHeader.textContent = monthlyTitle;
        }

        select.addEventListener("change", function () {
            const isWeekly = select.value === "weekly";
            chart.data.datasets[0].label = isWeekly ? weeklyTitle : monthlyTitle;
            chart.data.datasets[0].data = isWeekly ? weeklyValues : monthlyValues;
            chart.data.datasets[0].backgroundColor = isWeekly ? weeklyColor : monthlyColor;
            if (cardHeader) {
                cardHeader.textContent = isWeekly ? weeklyTitle : monthlyTitle;
            }
            if (summaryLabel && summaryAmount && summaryBadge) {
                summaryLabel.textContent = isWeekly ? "Weekly Spend" : "Monthly Spend";
                const totalValue = Number(isWeekly ? summaryAmount.dataset.weeklyTotal : summaryAmount.dataset.monthlyTotal) || 0;
                summaryAmount.textContent = formatIndianCurrency(totalValue);
                summaryBadge.textContent = isWeekly ? "Weekly Total" : "Current Month";
            }
            chart.update();
        });
    }

    function formatIndianCurrency(value) {
        return "₹ " + Number(value).toLocaleString("en-IN");
    }

    createToggleChart(
        "toggleChart",
        "chartPeriodSelect",
        "Monthly Salary Spend",
        "Weekly Payroll Spend",
        "#2563eb",
        "#f97316"
    );

    createBarChart(
        "yearlyChart",
        "Yearly Salary Spend",
        "#22c55e",
        JSON.parse(document.getElementById("yearlyChart").dataset.labels || "[]"),
        JSON.parse(document.getElementById("yearlyChart").dataset.values || "[]")
    );

});