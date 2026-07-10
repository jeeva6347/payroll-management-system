from datetime import date
from decimal import Decimal

from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
# Create your models here.

class Department(models.Model):
    department_name=models.CharField(max_length=100)
    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.department_name

class Position(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position_name = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Designation"
        verbose_name_plural = "Designations"

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
        self.full_clean()

        super().save(*args, **kwargs)

        if not self.employee_code:
            self.employee_code = f"EMP{self.id:04d}"
            super().save(update_fields=["employee_code"])

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
    

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
        verbose_name = "Monthly Payroll"
        verbose_name_plural = "Monthly Payroll"
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

        if self.employee.employee_type != "Permanent":
            raise ValidationError({
                "employee": "Monthly payroll can only be created for Permanent employees."
            })

        if Payroll.objects.filter(
            employee=self.employee,
            payroll_month__year=self.payroll_month.year,
            payroll_month__month=self.payroll_month.month,
        ).exclude(pk=self.pk).exists():

            raise ValidationError({
                "employee":
                "Payroll already exists for this employee for this month."
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
            self.basic_salary = self.employee.monthsalary or 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.payroll_month.strftime('%B %Y')}"


class WeeklyPayroll(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="weekly_payrolls"
    )

    week_start = models.DateField(default=date.today)
    week_end = models.DateField(default=date.today)

    description = models.TextField(
        blank=True,
        null=True
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True,null=True,blank=True)

    class Meta:
        verbose_name = "Weekly Payroll"
        verbose_name_plural = "Weekly Payroll"
        ordering = ["-week_start"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "week_start",
                    "week_end",
                ],
                name="unique_employee_weekly_payroll",
            )
        ]

    def clean(self):

        super().clean()

        if not self.employee_id:
            raise ValidationError({
                "employee": "Employee is required for weekly payroll."
            })

        if self.employee.employee_type != "Contract":
            raise ValidationError({
                "employee":
                "Weekly payroll can only be created for Contract employees."
            })

        if not self.week_start or not self.week_end:
            raise ValidationError({
                "__all__":
                "Week Start and Week End are required."
            })

        if self.week_end < self.week_start:
            raise ValidationError({
                "week_end":
                "Week End cannot be before Week Start."
            })

        duplicate_exists = WeeklyPayroll.objects.filter(
            employee=self.employee,
            week_start=self.week_start,
            week_end=self.week_end,
        ).exclude(pk=self.pk).exists()

        if duplicate_exists:
            raise ValidationError({
                "__all__":
                "A weekly payroll for this employee and week range already exists."
            })

    @property
    def total_earnings(self):

        return sum(
            (
                item.amount
                for item in self.items.filter(type="Earning")
            ),
            Decimal("0.00")
        )

    @property
    def total_deductions(self):

        return sum(
            (
                item.amount
                for item in self.items.filter(type="Deduction")
            ),
            Decimal("0.00")
        )

    @property
    def earnings(self):
        return self.items.filter(type="Earning")

    @property
    def deductions(self):
        return self.items.filter(type="Deduction")

    @property
    def net_salary(self):

        return self.total_earnings - self.total_deductions

    @property
    def week_display(self):

        return (
            f"{self.week_start.strftime('%d-%m-%Y')} "
            f"to "
            f"{self.week_end.strftime('%d-%m-%Y')}"
        )

    def sync_items(self, item_data):

        self.items.all().delete()

        for item in item_data:

            label = (
                item.get("label") or ""
            ).strip()

            if not label:
                continue

            WeeklyPayrollItem.objects.create(

                weekly_payroll=self,

                type=item.get(
                    "type",
                    "Earning"
                ),

                label=label,

                hp=item.get(
                    "hp",
                    0
                ),

                quantity=item.get(
                    "quantity",
                    1
                ),

                amount=item.get(
                    "amount",
                    0
                ),

            )

    def __str__(self):

        return (
            f"{self.employee.employee_code}"
            f" - "
            f"{self.week_display}"
        )


class WeeklyPayrollItem(models.Model):

    TYPE_CHOICES = (
        ("Earning", "Earning"),
        ("Deduction", "Deduction"),
    )

    weekly_payroll = models.ForeignKey(
        WeeklyPayroll,
        on_delete=models.CASCADE,
        related_name="items",
    )

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="Earning",
    )

    label = models.CharField(
        max_length=100
    )

    hp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=True,
    )

    quantity = models.PositiveIntegerField(
        default=1,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    class Meta:
        ordering = [
            "id"
        ]

    def clean(self):

        super().clean()

        if self.type == "Earning":

            if self.hp < 0:
                raise ValidationError(
                    {
                        "hp":
                        "HP cannot be negative."
                    }
                )

            if self.quantity < 1:
                raise ValidationError(
                    {
                        "quantity":
                        "Quantity must be at least 1."
                    }
                )

    def save(self, *args, **kwargs):

        if self.type == "Earning":

            self.amount = (
                Decimal(self.hp)
                *
                Decimal(self.quantity)
            )

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return (
            f"{self.type}"
            f" - "
            f"{self.label}"
        )
