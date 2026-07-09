from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    """
    Lets someone log in with either their email or their phone number in
    the "username" field — both are required, unique fields on the account
    (see accounts.models.User), so both should work as a login identifier.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(Q(email__iexact=username) | Q(phone_number=username))
        except User.DoesNotExist:
            # Run the hasher anyway to keep timing consistent with the
            # "user exists but password is wrong" case.
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
