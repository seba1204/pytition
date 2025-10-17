from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy


class PytitionUser(models.Model):
    """
    Application-level profile linked to AUTH_USER_MODEL.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pytitionuser",
    )
    # Temporary strings for cross-app FKs (resolved after orgs/petitions split)
    invitations = models.ManyToManyField(
        "petition.Organization",
        related_name="invited",
        blank=True,
    )
    default_template = models.ForeignKey(
        "petition.PetitionTemplate",
        blank=True,
        null=True,
        to_field="id",
        related_name="+",
        verbose_name=gettext_lazy("Default petition template"),
        on_delete=models.SET_NULL,
    )
    moderated = models.BooleanField(default=False)

    class Meta:
        # Keep the existing table, no schema change at this step
        db_table = "petition_pytitionuser"

    def drop(self):
        """
        Delete the user profile and cleanup owned objects.
        """

        with transaction.atomic():
            orgs = list(self.user.organization_set.all())
            petitions = list(self.user.petition_set.all())
            templates = list(self.user.petitiontemplate_set.all())
            self.delete()
            for org in orgs:
                if org.members.count() == 0:
                    org.delete()
            for petition in petitions:
                petition.delete()
            for template in templates:
                template.delete()

    @property
    def is_authenticated(self):
        return True

    @property
    def username(self):
        return self.user.username

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    @property
    def get_full_name(self):
        return self.user.get_full_name()

    @property
    def kind(self):
        return "user"

    def __str__(self):
        return self.get_full_name or self.username

    def __repr__(self):
        return f"<{self.__str__()}>"
