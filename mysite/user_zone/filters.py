from django_filters import FilterSet
from .models import GeneralData

class GeneralDataFilter(FilterSet):
    class Meta:
        model = GeneralData
        fields = ["user", "name", "surname", "company_name"]
