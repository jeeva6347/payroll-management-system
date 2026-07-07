
document.addEventListener("DOMContentLoaded", function () {

    const earningRows = document.getElementById("earning-rows");
    const deductionRows = document.getElementById("deduction-rows");

    const addEarningBtn = document.getElementById("add-earning-row");
    const addDeductionBtn = document.getElementById("add-deduction-row");

    const totalEarnings = document.getElementById("id_total_earnings");
    const totalDeduction = document.getElementById("id_total_deduction");
    const netSalary = document.getElementById("id_net_salary");

    function createRow(type, label = "", amount = "") {

        const row = document.createElement("div");

        row.className = "row g-2 mb-2 align-items-center";

        row.innerHTML = `
            <div class="col-md-6">
                <input
                    type="text"
                    class="form-control"
                    name="${type}_label[]"
                    placeholder="Label"
                    value="${label}">
            </div>

            <div class="col-md-4">
                <input
                    type="number"
                    step="0.01"
                    class="form-control amount-field"
                    name="${type}_amount[]"
                    placeholder="0.00"
                    value="${amount}">
            </div>

            <div class="col-md-2">
                <button
                    type="button"
                    class="btn btn-outline-danger btn-sm remove-row"
                    title="Remove row"
                    aria-label="Remove row">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        return row;
    }

    function updateTotals() {

        let earnings = 0;
        let deductions = 0;

        document.querySelectorAll('input[name="earning_amount[]"]').forEach(function(input){

            earnings += parseFloat(input.value) || 0;

        });

        document.querySelectorAll('input[name="deduction_amount[]"]').forEach(function(input){

            deductions += parseFloat(input.value) || 0;

        });

        if(totalEarnings)
            totalEarnings.value = earnings.toFixed(2);

        if(totalDeduction)
            totalDeduction.value = deductions.toFixed(2);

        if(netSalary)
            netSalary.value = (earnings - deductions).toFixed(2);

    }

    if(addEarningBtn){

        addEarningBtn.addEventListener("click", function(){

            earningRows.appendChild(createRow("earning"));

            updateTotals();

        });

    }

    if(addDeductionBtn){

        addDeductionBtn.addEventListener("click", function(){

            deductionRows.appendChild(createRow("deduction"));

            updateTotals();

        });

    }

    document.addEventListener("click", function(e){

        const removeButton = e.target.closest(".remove-row");

        if(removeButton){

            removeButton.closest(".row").remove();

            updateTotals();

        }

    });

    document.addEventListener("input", function(e){

        if(e.target.classList.contains("amount-field")){

            updateTotals();

        }

    });

    // Load existing rows
    const initialData = document.getElementById("initial-data");

    if(initialData){

        const rows = JSON.parse(initialData.dataset.rows || "[]");

        rows.forEach(function(item){

            if(item.type === "Earning"){

                earningRows.appendChild(
                    createRow(
                        "earning",
                        item.label,
                        item.amount
                    )
                );

            }

            else{

                deductionRows.appendChild(
                    createRow(
                        "deduction",
                        item.label,
                        item.amount
                    )
                );

            }

        });

    }

    updateTotals();

});