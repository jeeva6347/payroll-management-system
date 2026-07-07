from datetime import date

from django.db import migrations, models
import django.utils.timezone


def populate_week_fields(apps, schema_editor):
    WeeklyPayroll = apps.get_model("Payrollmang", "WeeklyPayroll")
    for payroll in WeeklyPayroll.objects.all():
        payroll.week_start = payroll.payroll_date or date.today()
        payroll.week_end = payroll.payroll_date or date.today()
        payroll.save(update_fields=["week_start", "week_end"])


class Migration(migrations.Migration):

    dependencies = [
        ("Payrollmang", "0013_fix_weeklypayrollitem_schema"),
    ]

    operations = [
        migrations.AddField(
            model_name="weeklypayroll",
            name="week_start",
            field=models.DateField(default=date.today),
        ),
        migrations.AddField(
            model_name="weeklypayroll",
            name="week_end",
            field=models.DateField(default=date.today),
        ),
        migrations.RunPython(populate_week_fields, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="weeklypayroll",
            name="payroll_date",
        ),
        migrations.AddConstraint(
            model_name="weeklypayroll",
            constraint=models.UniqueConstraint(fields=("employee", "week_start", "week_end"), name="unique_employee_week_range"),
        ),
    ]
