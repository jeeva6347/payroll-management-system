from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Employee, Payroll, WeeklyPayroll
from django.db.models import Sum

def get_salary(request):
    employee_id = request.GET.get('employee_id')
    employee = Employee.objects.get(id=employee_id)
    return JsonResponse({
        'salary': str(employee.monthsalary)
    })


def salary_slip(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)

    return render(
        request,
        'Payrollmang/salary_slip.html',
        {'payroll': payroll}
    )



def employee_salary_history_print(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    payrolls = Payroll.objects.filter(
        employee=employee
    ).order_by("payroll_month")

    context = {
        "employee": employee,
        "payrolls": payrolls,
        "total_basic": sum(p.basic_salary for p in payrolls),
        "total_salary": sum(p.total_salary for p in payrolls),
        "total_deduction": sum(p.total_deduction for p in payrolls),
        "total_net": sum(p.net_salary for p in payrolls),
    }

    return render(
        request,
        "Payrollmang/employee_salary_history_print.html",
        context,
    )



def weekly_salary_slip(request, pk):
    weekly_payroll = get_object_or_404(WeeklyPayroll, pk=pk)
    return render(request, "Payrollmang/weekly_salary_slip.html", {"weekly_payroll": weekly_payroll})


def contract_employees(request):
    employees = Employee.objects.filter(employee_type="Contract").order_by("Firstname")

    data = [
        {"id": emp.id, "text": f"{emp.employee_code} - {emp.Firstname}"}
        for emp in employees
    ]

    return JsonResponse(data, safe=False)



