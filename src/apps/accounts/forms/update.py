"""Form to update user information."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class UpdateInfoForm(UserCreationForm):
    """Form to update user information."""

    class Meta:
        """Meta class for UpdateInfoForm."""

        model = get_user_model()
        fields = ("first_name", "last_name", "email")

    def __init__(self, user: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        del self.fields["password1"]
        del self.fields["password2"]

    def save(self, commit: bool = True) -> Any:
        """Save the updated user information."""
        self.user.email = self.cleaned_data["email"]
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        if commit:
            self.user.save()
        return self.user
