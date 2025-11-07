""""Tests for Theme model relations and QuerySet helpers."""

from __future__ import annotations

from django.test import TestCase

from apps.accounts.models import PytitionUser
from apps.organizations.models import Organization
from apps.theming.models import Theme
from apps.theming.tests.common import RegistrySettingsMixin, make_pytition_user


class ThemeRelationsQuerysetTests(RegistrySettingsMixin, TestCase):
    """Tests for GenericRelation access and QuerySet helpers."""

    def test_generic_relation_reverse_access(self) -> None:
        """PytitionUser and Organization expose `.themes` via GenericRelation."""
        p_user = make_pytition_user("bob")
        org = Organization.objects.create(name="Acme")
        creator = make_pytition_user("creator")

        t1 = Theme(
            name="U",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-body-bg": "#fff"}},
        )
        t1.set_owner(p_user)
        t1.full_clean()
        t1.save()

        t2 = Theme(
            name="O",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-body-bg": "#000"}},
        )
        t2.set_owner(org)
        t2.full_clean()
        t2.save()

        self.assertEqual(p_user.themes.count(), 1)
        self.assertEqual(org.themes.count(), 1)
        self.assertSetEqual(set(p_user.themes.values_list("name", flat=True)), {"U"})
        self.assertSetEqual(set(org.themes.values_list("name", flat=True)), {"O"})

    def test_queryset_helpers_for_owner(self) -> None:
        """for_owner / for_owner_model filter correctly."""
        p_user = make_pytition_user("zoe")
        org = Organization.objects.create(name="Acme")
        creator = make_pytition_user("creator")

        ta = Theme(
            name="A",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-body-bg": "#fff"}},
        )
        ta.set_owner(p_user)
        ta.full_clean()
        ta.save()

        tb = Theme(
            name="B",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-body-bg": "#000"}},
        )
        tb.set_owner(org)
        tb.full_clean()
        tb.save()

        self.assertSetEqual(
            set(Theme.objects.for_owner(p_user).values_list("name", flat=True)), {"A"}
        )
        self.assertSetEqual(
            set(Theme.objects.for_owner(org).values_list("name", flat=True)), {"B"}
        )
        self.assertSetEqual(
            set(
                Theme.objects.for_owner_model(PytitionUser).values_list(
                    "name", flat=True
                )
            ),
            {"A"},
        )
        self.assertSetEqual(
            set(
                Theme.objects.for_owner_model(Organization).values_list(
                    "name", flat=True
                )
            ),
            {"B"},
        )
