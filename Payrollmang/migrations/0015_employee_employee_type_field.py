from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Payrollmang", "0014_weeklypayroll_week_range"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="employee_type",
            field=models.CharField(choices=[("Permanent", "Permanent"), ("Contract", "Contract")], default="Permanent", max_length=20),
        ),
    ]
