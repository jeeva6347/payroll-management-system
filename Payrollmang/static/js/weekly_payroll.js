document.addEventListener("DOMContentLoaded", function () {

    const earningRows = document.getElementById("earning-rows");
    const deductionRows = document.getElementById("deduction-rows");

    const addEarningBtn = document.getElementById("add-earning-row");
    const addDeductionBtn = document.getElementById("add-deduction-row");

    const totalEarnings = document.getElementById("id_total_earnings");
    const totalDeduction = document.getElementById("id_total_deduction");
    const netSalary = document.getElementById("id_net_salary");

    // Added: escape user-entered text before inserting it into innerHTML.
    // Without this, a label containing a double-quote or angle bracket
    // (e.g. `John "The Boss" <script>`) could break the markup or inject
    // HTML into the page.
    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
    }

    function createEarningRow(label = "", hp = "", quantity = "", amount = "") {

        const row = document.createElement("div");

        row.className = "row g-2 mb-2 align-items-center";

        row.innerHTML = `
            <div class="col-md-3">
                <input
                    type="text"
                    class="form-control"
                    name="earning_label[]"
                    placeholder="Label"
                    value="${escapeHtml(label)}">
            </div>

            <div class="col-md-2">
                <input
                    type="number"
                    step="0.01"
                    class="form-control hp-field"
                    name="earning_hp[]"
                    placeholder="HP"
                    value="${escapeHtml(hp)}">
            </div>

            <div class="col-md-2">
                <input
                    type="number"
                    step="1"
                    min="1"
                    class="form-control qty-field"
                    name="earning_quantity[]"
                    placeholder="Qty"
                    value="${escapeHtml(quantity)}">
            </div>

            <div class="col-md-3">
                <input
                    type="number"
                    step="0.01"
                    class="form-control amount-field"
                    name="earning_amount[]"
                    placeholder="Amount"
                    value="${escapeHtml(amount)}">
            </div>

            <div class="col-md-2">
                <button
                    type="button"
                    class="btn btn-outline-danger btn-sm remove-row">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        return row;
    }

    function createDeductionRow(label = "", amount = "") {

        const row = document.createElement("div");

        row.className = "row g-2 mb-2 align-items-center";

        row.innerHTML = `
            <div class="col-md-7">
                <input
                    type="text"
                    class="form-control"
                    name="deduction_label[]"
                    placeholder="Label"
                    value="${escapeHtml(label)}">
            </div>

            <div class="col-md-3">
                <input
                    type="number"
                    step="0.01"
                    class="form-control amount-field"
                    name="deduction_amount[]"
                    placeholder="Amount"
                    value="${escapeHtml(amount)}">
            </div>

            <div class="col-md-2">
                <button
                    type="button"
                    class="btn btn-outline-danger btn-sm remove-row">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        return row;
    }

    function updateTotals() {

        let earnings = 0;
        let deductions = 0;

        document.querySelectorAll('input[name="earning_amount[]"]').forEach(function (input) {
            earnings += parseFloat(input.value) || 0;
        });

        document.querySelectorAll('input[name="deduction_amount[]"]').forEach(function (input) {
            deductions += parseFloat(input.value) || 0;
        });

        if (totalEarnings)
            totalEarnings.value = earnings.toFixed(2);

        if (totalDeduction)
            totalDeduction.value = deductions.toFixed(2);

        if (netSalary)
            netSalary.value = (earnings - deductions).toFixed(2);
    }

    if (addEarningBtn) {

        addEarningBtn.addEventListener("click", function () {

            earningRows.appendChild(createEarningRow());

        });

    }

    if (addDeductionBtn) {

        addDeductionBtn.addEventListener("click", function () {

            deductionRows.appendChild(createDeductionRow());

        });

    }

    document.addEventListener("click", function (e) {

        const btn = e.target.closest(".remove-row");

        if (btn) {

            btn.closest(".row").remove();

            updateTotals();

        }

    });

    document.addEventListener("input", function (e) {

        if (
            e.target.classList.contains("hp-field") ||
            e.target.classList.contains("qty-field")
        ) {

            const row = e.target.closest(".row");

            const hp = parseFloat(row.querySelector(".hp-field").value) || 0;
            const qty = parseFloat(row.querySelector(".qty-field").value) || 0;

            row.querySelector(".amount-field").value = (hp * qty).toFixed(2);

        }

        if (
            e.target.classList.contains("hp-field") ||
            e.target.classList.contains("qty-field") ||
            e.target.classList.contains("amount-field")
        ) {

            updateTotals();

        }

    });

    const initialData = document.getElementById("initial-data");

    if (initialData) {

        const rows = JSON.parse(initialData.dataset.rows || "[]");

        rows.forEach(function (item) {

            if (item.type === "Earning") {

                earningRows.appendChild(
                    createEarningRow(
                        item.label ?? "",
                        item.hp ?? "",
                        item.quantity ?? "",
                        item.amount ?? ""
                    )
                );

            } else {

                deductionRows.appendChild(
                    createDeductionRow(
                        item.label ?? "",
                        item.amount ?? ""
                    )
                );

            }

        });

    }

    updateTotals();

});