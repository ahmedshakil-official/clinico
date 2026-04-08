import django_filters

from bill.models import Bill


class BillFilter(django_filters.FilterSet):
    created_at_after = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
    )
    created_at_before = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
    )

    appointment_date_after = django_filters.DateFilter(
        field_name="appointment__appointment_date",
        lookup_expr="gte",
    )
    appointment_date_before = django_filters.DateFilter(
        field_name="appointment__appointment_date",
        lookup_expr="lte",
    )

    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    discount_min = django_filters.NumberFilter(field_name="discount", lookup_expr="gte")
    discount_max = django_filters.NumberFilter(field_name="discount", lookup_expr="lte")

    tax_min = django_filters.NumberFilter(field_name="tax", lookup_expr="gte")
    tax_max = django_filters.NumberFilter(field_name="tax", lookup_expr="lte")

    total_amount_min = django_filters.NumberFilter(field_name="total_amount", lookup_expr="gte")
    total_amount_max = django_filters.NumberFilter(field_name="total_amount", lookup_expr="lte")

    class Meta:
        model = Bill
        fields = [
            "payment_status",
            "payment_method",
            "appointment",
        ]