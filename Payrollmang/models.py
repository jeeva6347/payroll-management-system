from datetime import date
from decimal import Decimal

from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
# Create your models here.

class Department(models.Model):
    department_name=models.CharField(max_length=100)
    def __str__(self):
        return self.department_name

class Position(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position_name = models.CharField(max_length=100)
    def __str__(self):
        return self.position_name



class Employee(models.Model):
    employee_code=models.CharField(max_length=10,unique=True,null=True,blank=True)
    Firstname = models.CharField(max_length=100, validators=[RegexValidator(r'^[A-Z a-z]+$')])
    Lastname = models.CharField(max_length=100, validators=[RegexValidator(r'^[A-Z a-z]+$')],blank=True ,)
    employee_type = models.CharField(max_length=20,
    choices=[("Permanent", "Permanent"), ("Contract", "Contract")],default="Permanent",)
    DOB = models.DateField(null=True,blank=True)
    phone = models.CharField(max_length=10, validators=[RegexValidator(r'\d{10}$','Enter 10 digits')])
    email = models.EmailField(unique=True,blank=True,null=True)
    address = models.TextField()
    date_of_join = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    monthsalary = models.DecimalField(max_digits=10, decimal_places=2)
   
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.employee_code:
            self.employee_code = f"EMP{self.id:04d}"
            super().save(update_fields=['employee_code'])
    

    def __str__(self):
        return f"{self.employee_code} - {self.Firstname}"
    


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    payroll_month = models.DateField(default=timezone.now)

    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    house_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    da_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    other_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    pf = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    advance = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    loan = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    ot_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    working_days = models.IntegerField(default=30)
    absent_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
   


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "payroll_month"],
                name="unique_employee_payroll_month",
            )
        ]

    def clean(self):
        super().clean()

        if not self.employee_id:
            raise ValidationError({
                "employee": "Employee is required."
            })

        if Payroll.objects.filter(
            employee=self.employee,
            payroll_month__year=self.payroll_month.year,
            payroll_month__month=self.payroll_month.month,
        ).exclude(pk=self.pk).exists():
            raise ValidationError({
                "employee": "Payroll already exists for this employee for this month."
            })

    @property
    def total_salary(self):
        return round(
            self.basic_salary
            + self.house_allowance
            + self.da_allowance
            + self.other_allowance
            + self.ot_amount
        )

    @property
    def loss_of_pay(self):
        if self.working_days > 0:
            lop_base = (
                (self.basic_salary
                + self.house_allowance
                + self.da_allowance
                + self.other_allowance)
                / self.working_days
                * self.absent_days
            
            )
            return round(lop_base)
        return 0

    @property
    def total_deduction(self):
        return round(
            self.pf
            + self.advance
            + self.loan
            + self.loss_of_pay
        )

    @property
    def net_salary(self):
        return round(self.total_salary - self.total_deduction)

    def save(self, *args, **kwargs):
        if self.employee:
            self.basic_salary = self.employee.monthsalary
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.payroll_month.strftime('%B %Y')}"


class WeeklyPayroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    week_start = models.DateField(default=date.today)
    week_end = models.DateField(default=date.today)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Weekly Payroll"
        verbose_name_plural = "Weekly Payrolls"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "week_start", "week_end"],
                name="unique_employee_week_range",
            )
        ]

    def clean(self):
        super().clean()

        if not self.employee_id:
            raise ValidationError({"employee": "Employee is required."})

        if self.week_start and self.week_end and self.week_end < self.week_start:
            raise ValidationError({"week_end": "Week end must be greater than or equal to week start."})

        if self.employee_id and self.week_start and self.week_end:
            duplicate = WeeklyPayroll.objects.filter(
                employee=self.employee,
                week_start=self.week_start,
                week_end=self.week_end,
            ).exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError({"employee": "A weekly payroll already exists for this employee in the selected week."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def sync_items(self, item_data):
        self.items.all().delete()
        for item in item_data:
            label = (item.get("label") or "").strip()
            amount = (item.get("amount") or "").strip()
            if not label or not amount:
                continue
            WeeklyPayrollItem.objects.create(
                weekly_payroll=self,
                type=item.get("type", "Earning"),
                label=label,
                amount=amount,
            )

    @property
    def total_earnings(self):
        return sum((item.amount for item in self.items.filter(type="Earning")), Decimal("0.00"))

    @property
    def total_deductions(self):
        return sum((item.amount for item in self.items.filter(type="Deduction")), Decimal("0.00"))

    @property
    def net_salary(self):
        return self.total_earnings - self.total_deductions

    @property
    def week_display(self):
        return f"{self.week_start.strftime('%d %b %Y')} – {self.week_end.strftime('%d %b %Y')}"

    def __str__(self):
        return f"{self.employee} - {self.week_display}"


class WeeklyPayrollItem(models.Model):
    TYPE_CHOICES = [
        ("Earning", "Earning"),
        ("Deduction", "Deduction"),
    ]

    weekly_payroll = models.ForeignKey(
        WeeklyPayroll,
        on_delete=models.CASCADE,
        related_name="items",
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="Earning")
    label = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Weekly Payroll Item"
        verbose_name_plural = "Weekly Payroll Items"

    def __str__(self):
        return f"{self.type} - {self.label}"

