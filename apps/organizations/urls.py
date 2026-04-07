from django.urls import path
from .views import OrganizationCreateView, InviteMemberView, InvitationListView, AcceptInvitationView, ValidateInvitationView, OrganizationMembersView


urlpatterns = [
    path("", OrganizationCreateView.as_view(), name="organization-create"),
    path("invite/", InviteMemberView.as_view()),
    path("invitations/", InvitationListView.as_view()),
    path("invitations/accept/", AcceptInvitationView.as_view()),
    path("invitations/validate/", ValidateInvitationView.as_view()),
    path('members/', OrganizationMembersView.as_view()),
]