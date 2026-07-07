from django.urls import path
from .views import get_salary
from . import views



urlpatterns=[
    path('get-salary/', get_salary, name='get_salary'),
    path("salary-slip/<int:pk>/",views.salary_slip,name="salary_slip"),
    path("weekly-salary-slip/<int:pk>/", views.weekly_salary_slip, name="weekly_salary_slip"),
    path("employee/salary-history/print/<int:employee_id>/",views.employee_salary_history_print,name="employee_salary_history_print",),
    path("contract-employees/",views.contract_employees,name="contract_employees",
),
]
