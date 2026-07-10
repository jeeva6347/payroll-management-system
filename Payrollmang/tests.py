from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .admin import WeeklyPayrollAdmin
from .models import Department, Employee, Position, WeeklyPayroll


class WeeklyPayrollAdminTests(TestCase):
    def test_weekly_payroll_admin_includes_dynamic_row_script(self):
        self.assertEqual(WeeklyPayrollAdmin.Media.js, ("js/weekly_payroll.js",))

    def test_weekly_payroll_admin_employee_field_only_lists_contract_employees(self):
        department = Department.objects.create(department_name="Finance")
        position = Position.objects.create(department=department, position_name="Accountant")

        contract_employee = Employee.objects.create(
            Firstname="Alice",
            Lastname="Smith",
            phone="9876543211",
            email="alice@example.com",
            address="Main Street",
            department=department,
            position=position,
            monthsalary=Decimal("40000.00"),
            employee_type="Contract",
        )
        permanent_employee = Employee.objects.create(
            Firstname="Bob",
            Lastname="Jones",
            phone="9876543212",
            email="bob@example.com",
            address="Main Street",
            department=department,
            position=position,
            monthsalary=Decimal("45000.00"),
        )

        form = WeeklyPayrollAdmin.form
        self.assertIn(contract_employee, form.base_fields["employee"].queryset)
        self.assertNotIn(permanent_employee, form.base_fields["employee"].queryset)


class WeeklyPayrollModelTests(TestCase):
    def setUp(self):
        department = Department.objects.create(department_name="Finance")
        position = Position.objects.create(department=department, position_name="Accountant")
        self.employee = Employee.objects.create(
            Firstname="John",
            Lastname="Doe",
            phone="9876543210",
            email="john@example.com",
            address="Main Street",
            department=department,
            position=position,
            monthsalary=Decimal("50000.00"),
        )

    def test_sync_items_saves_earning_and_deduction_rows(self):
        weekly_payroll = WeeklyPayroll.objects.create(
            employee=self.employee,
            week_start=date(2026, 7, 6),
            week_end=date(2026, 7, 12),
        )

        weekly_payroll.sync_items([
            {"type": "Earning", "label": "Bonus", "amount": "1500.50"},
            {"type": "Deduction", "label": "Loan", "amount": "300.00"},
        ])

        self.assertEqual(weekly_payroll.items.count(), 2)
        earning = weekly_payroll.items.get(type="Earning")
        deduction = weekly_payroll.items.get(type="Deduction")
        self.assertEqual(earning.label, "Bonus")
        self.assertEqual(earning.amount, Decimal("1500.50"))
        self.assertEqual(deduction.label, "Loan")
        self.assertEqual(deduction.amount, Decimal("300.00"))

    def test_weekly_payroll_rejects_invalid_week_range(self):
        weekly_payroll = WeeklyPayroll(employee=self.employee, week_start=date(2026, 7, 13), week_end=date(2026, 7, 6))

        with self.assertRaises(ValidationError):
            weekly_payroll.clean()

    def test_weekly_payroll_rejects_non_contract_employee(self):
        permanent_employee = Employee.objects.create(
            Firstname="Jane",
            Lastname="Doe",
            phone="9876543213",
            email="jane@example.com",
            address="Main Street",
            department=self.employee.department,
            position=self.employee.position,
            monthsalary=Decimal("55000.00"),
            employee_type="Permanent",
        )

        weekly_payroll = WeeklyPayroll(
            employee=permanent_employee,
            week_start=date(2026, 7, 6),
            week_end=date(2026, 7, 12),
        )

        with self.assertRaises(ValidationError):
            weekly_payroll.clean()

    def test_weekly_payroll_rejects_duplicate_week_range_for_same_employee(self):
        WeeklyPayroll.objects.create(
            employee=self.employee,
            week_start=date(2026, 7, 6),
            week_end=date(2026, 7, 12),
        )

        duplicate = WeeklyPayroll(employee=self.employee, week_start=date(2026, 7, 6), week_end=date(2026, 7, 12))

        with self.assertRaises(ValidationError):
            duplicate.clean()
