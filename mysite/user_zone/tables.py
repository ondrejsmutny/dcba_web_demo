from django_tables2 import Table
from .models import GeneralData

class GeneralDataTable(Table):
    class Meta:
        model = GeneralData
        template_name = "django_tables2/bootstrap4.html"