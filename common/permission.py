# from rest_framework import permissions
#
#
# class IsStaffOrDoctor(permissions.BasePermission):
#     """
#     Allows access only to Doctors or Receptionists for POST/PUT/DELETE.
#     """
#
#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False
#
#         # Check profile role
#         user_role = getattr(request.user.profile, 'role', None)
#         return user_role in ['DOCTOR', 'RECEPTIONIST']
#
#
# class IsOwnerOrStaff(permissions.BasePermission):
#     """
#     Patients can only see their own data. Staff/Doctors see everything.
#     """
#
#     def has_object_permission(self, request, view, obj):
#         user_role = getattr(request.user.profile, 'role', None)
#         if user_role in ['DOCTOR', 'RECEPTIONIST']:
#             return True
#         # If the object is an Appointment, check if it belongs to the patient
#         return obj.patient.profile.user == request.user