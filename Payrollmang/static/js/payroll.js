$(document).ready(function () {
    $('#id_basic_salary').prop('readonly', true);

    $('#id_employee').change(function () {
        let employeeId = $(this).val();
        if (!employeeId) {
            return;
        }

        $.ajax({
            url: '/get-salary/',
            data: {
                employee_id: employeeId
            },
            success: function (data) {
                $('#id_basic_salary').val(data.salary);
            }
        });
    });
});
