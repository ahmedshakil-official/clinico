# from rest_framework import generics
#
# from bill.serializers import BillingSerializer
# from common.models import Billing
# from common.permission import IsStaffOrDoctor
#
#
# class BillingListView(generics.ListAPIView):
#     serializer_class = BillingSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         if user.profile.role == 'PATIENT':
#             return Billing.objects.filter(appointment__patient__profile__user=user)
#         return Billing.objects.all()
#
#
# class BillingUpdateView(generics.RetrieveUpdateAPIView):
#     queryset = Billing.objects.all()
#     serializer_class = BillingSerializer
#     permission_classes = [IsStaffOrDoctor]