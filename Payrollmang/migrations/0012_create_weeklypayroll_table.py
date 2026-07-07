from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Payrollmang", "0011_weeklypayroll_weeklypayrollitem"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS "Payrollmang_weeklypayroll" (
                "id" SERIAL PRIMARY KEY,
                "payroll_date" date NOT NULL,
                "created_date" timestamp NOT NULL,
                "employee_id" bigint NOT NULL REFERENCES "Payrollmang_employee" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS \"Payrollmang_weeklypayroll\";",
        )
    ]
