from django import forms
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import (Employee, Department, Position, Payroll, WeeklyPayroll)
from django.http import HttpResponse
import csv
import json
from django.urls import reverse, path
from django.db.models import Sum, Q
from django.utils import timezone
from django.db.models.functions import ExtractMonth, ExtractYear
from calendar import month_abbr
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse

# Register your models




@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin-forms.css',)
        }

    list_display = (
        'employee_code',
        'Firstname',
        'employee_type',
        'phone',
        'department',
        'position',
        'monthsalary',
        'salary_history_button',
    )
    search_fields = (
    "employee_code",
    "Firstname",
    "Lastname",
    "phone",
    "email",
)
   

    list_per_page = 10
    ordering = ("employee_code",)

    actions = ['export_csv']

    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=employees.csv'

        writer = csv.writer(response)

        writer.writerow([
            'Employee Code',
            'First Name',
            'Phone',
            'Email',
            'Department',
            'Position',
            'Salary',
        ])

        for emp in queryset:
            writer.writerow([
                emp.employee_code,
                emp.Firstname,
                emp.phone,
                emp.email,
                emp.department,
                emp.position,
                emp.monthsalary,
            ])

        return response

    export_csv.short_description = "Export Selected Employees"

    def salary_history_button(self, obj):
       
        if getattr(obj, 'employee_type', None) == 'Contract':
            url = f"weekly-history/{obj.id}/"
        else:
            url = f"salary-history/{obj.id}/"

        return format_html(
            '<a class="btn btn-primary btn-sm" href="{}">Report</a>',
            url,
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "salary-history/<int:employee_id>/",
                self.admin_site.admin_view(self.salary_history_view),
                name="employee_salary_history",
            ),
            path(
                "weekly-history/<int:employee_id>/",
                self.admin_site.admin_view(self.salary_weekly_history_view),
                name="employee_weekly_history",
            ),
        ]
        return custom_urls + urls

    def salary_history_view(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)

        payrolls = Payroll.objects.filter(employee=employee).order_by("-payroll_month")

        total_basic = sum(p.basic_salary for p in payrolls)
        total_salary = sum(p.total_salary for p in payrolls)
        total_deduction = sum(p.total_deduction for p in payrolls)
        total_net = sum(p.net_salary for p in payrolls)

        context = {
            **self.admin_site.each_context(request),
            'employee': employee,
            'payrolls': payrolls,
            'total_basic': total_basic,
            'total_salary': total_salary,
            'total_deduction': total_deduction,
            'total_net': total_net,
        }

        return render(request, "Payrollmang/salary_history.html", context)

    def salary_weekly_history_view(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)

        weekly_payrolls = WeeklyPayroll.objects.filter(employee=employee).order_by("-week_start")

        total_earnings = sum((wp.total_earnings or 0) for wp in weekly_payrolls)
        total_deductions = sum((wp.total_deductions or 0) for wp in weekly_payrolls)
        total_net = sum((wp.net_salary or 0) for wp in weekly_payrolls)

        context = {
            **self.admin_site.each_context(request),
            'employee': employee,
            'weekly_payrolls': weekly_payrolls,
            'total_earnings': total_earnings,
            'total_deductions': total_deductions,
            'total_net': total_net,
        }

        return render(request, "Payrollmang/weekly_history.html", context)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name',)
    list_per_page = 10


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('department', 'position_name')
    list_per_page = 10


class PayrollAdminForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        if "employee" in self.fields:
            self.fields["employee"].queryset = Employee.objects.filter(
                employee_type="Permanent"
            ).order_by("Firstname")


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    form = PayrollAdminForm
    change_form_template = "Payrollmang/payroll/change_form.html"

    class Media:
        css = {
            "all": ("css/admin.css",)
        }
        js = (
            "js/payroll.js",
            "js/salary.js",
        )

    list_display = (
        'employee_code',
        'employee_name',
        'payroll_month',
        'basic_salary_display',
        'total_salary_display',
        'total_deduction_display',
        'net_salary_display',
        'salary_print_button',
    )
    search_fields = (
    "employee__employee_code",
    "employee__Firstname",
)
   
    list_per_page = 10
    ordering = ("-payroll_month",)

    def employee_name(self, obj):
        return obj.employee.Firstname

    employee_name.short_description = "Employee"

    def employee_code(self, obj):
        return obj.employee.employee_code

    employee_code.short_description = "Employee ID"

    def salary_print_button(self, obj):
        if not obj or not obj.pk:
            return "N/A"

        url = reverse(
            'salary_slip',
            kwargs={'pk': obj.pk}
        )

        return mark_safe(
            f'<a class="button" '
            f'style="background-color:#417690;'
            f'color:white;'
            f'padding:5px 10px;'
            f'text-decoration:none;'
            f'border-radius:3px;" '
            f'href="{url}" target="_blank"><i class="fas fa-print"></i> Print</a>'
        )

    salary_print_button.short_description = "Salary Slip"

    def basic_salary_display(self, obj):
        return f"₹ {obj.basic_salary:.2f}"

    basic_salary_display.short_description = "Basic Salary"

    def total_salary_display(self, obj):
        return f"₹ {obj.total_salary:.2f}"

    total_salary_display.short_description = "Total Salary"

    def total_deduction_display(self, obj):
        return f"₹ {obj.total_deduction:.2f}"

    total_deduction_display.short_description = "Total Deduction"

    def net_salary_display(self, obj):
        return f"₹ {obj.net_salary:.2f}"

    net_salary_display.short_description = "Net Salary"


class WeeklyPayrollAdminForm(forms.ModelForm):
    class Meta:
        model = WeeklyPayroll
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].queryset = Employee.objects.filter(
            employee_type="Contract"
        ).order_by("Firstname")


@admin.register(WeeklyPayroll)
class WeeklyPayrollAdmin(admin.ModelAdmin):

    form = WeeklyPayrollAdminForm
    change_form_template = "Payrollmang/weeklypayroll/change_form.html"
    list_display = (
        "employee_code",
        "employee_name",
        "week_start",
        "week_end",
        "total_earnings_display",
        "total_deductions_display",
        "net_salary_display",
        "print_payslip",
    )
    search_fields = (
    "employee__employee_code",
    "employee__Firstname",
    
)
   
    list_per_page = 10
    ordering = ("-week_start",)

    class Media:
        js = (
            "js/weekly_payroll.js",
        )

    def employee_code(self, obj):
        return obj.employee.employee_code

    employee_code.short_description = "Employee Code"

    def employee_name(self, obj):
        return obj.employee.Firstname

    employee_name.short_description = "Employee Name"

    def total_earnings_display(self, obj):
        return f"₹ {obj.total_earnings:.2f}"

    total_earnings_display.short_description = "Total Earnings"

    def total_deductions_display(self, obj):
        return f"₹ {obj.total_deductions:.2f}"

    total_deductions_display.short_description = "Total Deductions"

    def net_salary_display(self, obj):
        return f"₹ {obj.net_salary:.2f}"

    net_salary_display.short_description = "Net Salary"

    def print_payslip(self, obj):
        if not obj or not obj.pk:
            return "N/A"
        url = reverse("weekly_salary_slip", kwargs={"pk": obj.pk})
        return mark_safe(
            f'<a class="button" style="background-color:#417690;color:white;'
            f'padding:5px 10px;text-decoration:none;border-radius:3px;" '
            f'href="{url}" target="_blank"><i class="fas fa-print"></i> Print</a>'
        )

    print_payslip.short_description = "Print Payslip"

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)

        item_data = []

        earning_labels = request.POST.getlist("earning_label[]")
        earning_amounts = request.POST.getlist("earning_amount[]")
        earning_hp = request.POST.getlist("earning_hp[]")
        earning_quantity = request.POST.getlist("earning_quantity[]")
        for label, hp, quantity, amount in zip(
            earning_labels,
            earning_hp,
            earning_quantity,
            earning_amounts
        ):
            item_data.append({
                "type": "Earning",
                "label": label,
                "hp": hp,
                "quantity": quantity,
                "amount": amount,
            })

        deduction_labels = request.POST.getlist("deduction_label[]")
        deduction_amounts = request.POST.getlist("deduction_amount[]")

        for label, amount in zip(deduction_labels, deduction_amounts):
            item_data.append({
                "type": "Deduction",
                "label": label,
                "amount": amount,
            })

        obj.sync_items(item_data)

    def render_change_form(self, request, context, *args, **kwargs):

        obj = context.get("original")

        rows = []

        if obj:
            for item in obj.items.all():
                rows.append({
                    "type": item.type,
                    "label": item.label,
                    "hp": float(item.hp),
                    "quantity": int(item.quantity),
                    "amount": float(item.amount),
                })

      
        context["initial_rows"] = json.dumps(rows)

        return super().render_change_form(
            request,
            context,
            *args,
            **kwargs
        )


def custom_index(request, extra_context=None):

    today = timezone.now()

    context = admin.site.each_context(request)

    employee_count = Employee.objects.count()
    department_count = Department.objects.count()
    position_count = Position.objects.count()
    payroll_count = Payroll.objects.count()

    monthly_salary = (
        Payroll.objects.filter(
            payroll_month__year=today.year,
            payroll_month__month=today.month,
        ).aggregate(total=Sum("basic_salary"))["total"] or 0
    )

    yearly_salary = (
        Payroll.objects.filter(
            payroll_month__year=today.year
        ).aggregate(total=Sum("basic_salary"))["total"] or 0
    )

    monthly_chart = (
        Payroll.objects.filter(
            payroll_month__year=today.year
        )
        .annotate(month=ExtractMonth("payroll_month"))
        .values("month")
        .annotate(total=Sum("basic_salary"))
        .order_by("month")
    )

    monthly_weekly_chart = (
        WeeklyPayroll.objects.filter(
            week_start__year=today.year
        )
        .annotate(month=ExtractMonth("week_start"))
        .values("month")
        .annotate(
            total_earnings=Sum(
                "items__amount",
                filter=Q(items__type="Earning")
            ),
            total_deductions=Sum(
                "items__amount",
                filter=Q(items__type="Deduction")
            )
        )
        .order_by("month")
    )

    yearly_chart = (
        Payroll.objects
        .annotate(year=ExtractYear("payroll_month"))
        .values("year")
        .annotate(total=Sum("basic_salary"))
        .order_by("year")
    )

    monthly_labels = []
    monthly_values = []
    monthly_weekly_values = []
    yearly_labels = []
    yearly_values = []

    monthly_totals = {}

    for item in monthly_chart:
        monthly_totals[item["month"]] = {
            "payroll": float(item["total"]),
            "weekly": 0.0,
        }

    for item in monthly_weekly_chart:
        payroll_month = item["month"]
        earnings = item["total_earnings"] or 0
        deductions = item["total_deductions"] or 0
        weekly_total = float(earnings - deductions)

        if payroll_month not in monthly_totals:
            monthly_totals[payroll_month] = {
                "payroll": 0.0,
                "weekly": weekly_total,
            }
        else:
            monthly_totals[payroll_month]["weekly"] = weekly_total

    for month in sorted(monthly_totals):
        monthly_labels.append(month_abbr[month])
        monthly_values.append(monthly_totals[month]["payroll"])
        monthly_weekly_values.append(monthly_totals[month]["weekly"])

    weekly_salary = sum(monthly_totals[month]["weekly"] for month in monthly_totals)

    for item in yearly_chart:
        yearly_labels.append(str(item["year"]))
        yearly_values.append(float(item["total"]))

    recent_payrolls = (
        Payroll.objects.select_related("employee")
        .order_by("-payroll_month")[:10]
    )

    top_salary_employees = (
        Employee.objects.order_by("-monthsalary")[:5]
    )

    latest_employees = (
        Employee.objects.order_by("-id")[:5]
    )

    if extra_context:
        context.update(extra_context)

    context.update({
        "employee_count": employee_count,
        "department_count": department_count,
        "position_count": position_count,
        "payroll_count": payroll_count,

        "monthly_salary": monthly_salary,
        "yearly_salary": yearly_salary,
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_values": json.dumps(monthly_values),
        "monthly_weekly_values": json.dumps(monthly_weekly_values),
        "weekly_salary": weekly_salary,
        "yearly_labels": json.dumps(yearly_labels),
        "yearly_values": json.dumps(yearly_values),

        "recent_payrolls": recent_payrolls,
        "top_salary_employees": top_salary_employees,
        "latest_employees": latest_employees,
    })

    return TemplateResponse(
        request,
        "Payrollmang/dashboard.html",
        context,
    )


admin.site.index = custom_index
admin.site.index_template = "Payrollmang/dashboard.html"