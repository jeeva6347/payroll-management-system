from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Payrollmang", "0012_create_weeklypayroll_table"),
    ]

    operations = [
        migrations.RunSQL(
            sql="SELECT 1",  # No-op migration
            reverse_sql="SELECT 1",
        )
    ]
