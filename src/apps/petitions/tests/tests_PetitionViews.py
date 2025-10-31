from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import PytitionUser
from apps.consents.routes import ConsentRoute
from apps.core.tests.utils import add_default_data
from apps.organizations.models import Organization
from apps.petitions.models import Petition
from apps.petitions.routes import PetitionsRoute


class PetitionViewTest(TestCase):
    """Test index view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def tearDown(self) -> None:
        # Clean up run after every test method.
        pass

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def test_petition_detail(self) -> None:
        """Every body should see the petition, even when not logged in."""

        petition = Petition.objects.filter(user__user__username="julia").first()

        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        response = self.client.get(reverse(PetitionsRoute.DETAIL, args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["petition"], petition)
        self.assertTemplateUsed(response, "petitions/detail.html")

        self.assertContains(
            response, text='<meta property="og:site_name" content="testserver" />'
        )
        self.assertContains(
            response,
            text=f'<meta property="og:url" content="http://testserver/petition/{petition.id}/" />',
        )

    def test_petition_success_msg(self) -> None:
        """Test that the success modal is there when signing and confirming."""
        petition = Petition.objects.filter(published=True).first()
        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        data = {
            "first_name": "test first name",
            "last_name": "test last name",
            "phone": "0123456789",
            "email": "toto@toto.com",
        }
        # First, let's sign the petition
        response = self.client.post(
            reverse("create_signature", args=[petition.id]), data, follow=True
        )
        self.assertRedirects(response, petition.url)
        self.assertContains(
            response,
            text="""<script type="text/javascript">$("#show_sign_success").modal("show");</script>""",
        )
        self.assertContains(
            response, text='<div class="modal fade" id="show_sign_success">'
        )
        self.assertNotContains(response, text="show_confirm_success")
        # Now, let's confirm our signature
        signature = petition.signature_set.first()
        self.assertIsNotNone(signature, "Signature should not be None.")
        if signature is None:
            return
        self.assertFalse(signature.confirmed)
        response = self.client.post(
            reverse(
                ConsentRoute.CONFIRM, args=[petition.id, signature.confirmation_hash]
            ),
            follow=True,
        )
        self.assertRedirects(response, petition.url)
        signature.refresh_from_db()
        self.assertTrue(signature.confirmed)
        self.assertContains(
            response,
            text="""<script type="text/javascript">$("#show_confirm_success").modal("show");</script>""",
        )
        self.assertContains(
            response, text='<div class="modal fade" id="show_confirm_success">'
        )
        self.assertNotContains(response, text="show_sign_success")

    def test_petition_publish(self) -> None:
        self.logout()
        petition = Petition.objects.filter(user__user__username="julia").first()
        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        petition.published = False
        petition.save()
        self.assertEqual(petition.published, False)
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[petition.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, False)
        self.login("julia")
        # Logged in with same user
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        petition.refresh_from_db()
        self.assertEqual(petition.published, True)
        # Petition for another user
        john = PytitionUser.objects.get(user__username="john")
        p2 = Petition.objects.create(title="Pas content", user=john)
        self.assertEqual(p2.published, False)
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[p2.id]))
        p2.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p2.published, False)
        # Petition from another organisation
        greenpeace = Organization.objects.get(name="Greenpeace")
        p3 = Petition.objects.create(title="Sauver la planete", org=greenpeace)
        self.assertEqual(p3.published, False)
        p3.refresh_from_db()
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[p3.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p3.published, False)

    def test_petition_unpublish(self) -> None:
        petition = Petition.objects.filter(user__user__username="julia").first()
        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        self.assertEqual(petition.published, True)
        self.logout()
        response = self.client.get(
            reverse(PetitionsRoute.UNPUBLISH, args=[petition.id])
        )
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, True)
        # Test to unpublish from wrong user
        self.login("max")
        response = self.client.get(
            reverse(PetitionsRoute.UNPUBLISH, args=[petition.id])
        )
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(petition.published, True)
        self.login("julia")
        response = self.client.get(
            reverse(PetitionsRoute.UNPUBLISH, args=[petition.id])
        )
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petition.published, False)

    def test_user_petition_delete(self) -> None:
        petitions = Petition.objects.filter(user__user__username="julia")
        petition = petitions.first()
        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        nb_julia_petitions = petitions.count()
        self.assertEqual(petitions.count(), nb_julia_petitions)
        response = self.client.get(reverse(PetitionsRoute.DELETE, args=[petition.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petitions.count(), nb_julia_petitions)
        self.login("julia")
        response = self.client.get(reverse(PetitionsRoute.DELETE, args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petitions.count(), nb_julia_petitions - 1)

    def test_org_petition_delete(self) -> None:
        self.logout()
        petitions = Petition.objects.filter(org__name="Attac")
        petition = petitions.first()
        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        nb_attac_petitions = petitions.count()
        response = self.client.get(
            reverse(PetitionsRoute.DELETE, args=[petition.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("login")
            + "?next="
            + reverse(PetitionsRoute.DELETE, args=[petition.id]),
        )
        self.assertEqual(petitions.count(), nb_attac_petitions)
        self.login("john")
        response = self.client.get(reverse(PetitionsRoute.DELETE, args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petitions.count(), nb_attac_petitions - 1)

    def test_user_slug_show_petition(self) -> None:
        petition = Petition.objects.filter(user__user__username="julia").first()
        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        slugmodel = petition.slugmodel_set.first()
        self.assertIsNotNone(slugmodel, "SlugModel should not be None.")
        if slugmodel is None:
            return
        slug = slugmodel.slug
        user = petition.user
        self.assertIsNotNone(user, "User should not be None.")
        if user is None:
            return

        response = self.client.get(
            reverse("slug_show_petition", args=[user.username, slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petitions/detail.html")

    def pending_org_slug_show_petition(self) -> None:
        # Problem here
        org = Organization.objects.first()
        petition = Petition.objects.create(title="NON NON NON", org=org)
        slugmodel = petition.slugmodel_set.first()
        self.assertIsNotNone(slugmodel, "SlugModel should not be None.")
        if slugmodel is None:
            return
        slug = slugmodel.slug
        org = petition.org
        self.assertIsNotNone(org, "Organization should not be None.")
        if org is None:
            return
        response = self.client.get(
            reverse("slug_show_petition", args=[org.slugname, slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petitions/detail.html")

    def test_petition_publish_org(self) -> None:
        self.logout()
        petition = Petition.objects.filter(org__name="Les Amis de la Terre").first()
        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        petition.published = False
        petition.save()
        self.assertEqual(petition.published, False)
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[petition.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, False)
        self.login("julia")
        # Logged in with same user
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        petition.refresh_from_db()
        self.assertEqual(petition.published, True)
        # Petition from your org
        at = Organization.objects.get(name="Les Amis de la Terre")
        p2 = Petition.objects.create(title="Pas content", org=at)
        self.assertEqual(p2.published, False)
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[p2.id]))
        p2.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(p2.published, True)
        # Petition from your org, but with no right
        p2.published = False
        p2.save()
        self.logout()
        self.login("max")
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[p2.id]))
        p2.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p2.published, False)
        # Petition from another organisation
        greenpeace = Organization.objects.get(name="Greenpeace")
        p3 = Petition.objects.create(title="Sauver la planete", org=greenpeace)
        self.assertEqual(p3.published, False)
        p3.refresh_from_db()
        response = self.client.get(reverse(PetitionsRoute.PUBLISH, args=[p3.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p3.published, False)

    def test_petition_unpublish_org(self) -> None:
        petition = Petition.objects.filter(org__name="Les Amis de la Terre").first()
        self.assertIsNotNone(petition, "Petition should not be None.")
        if petition is None:
            return
        petition.published = True
        petition.save()
        self.logout()
        response = self.client.get(
            reverse(PetitionsRoute.UNPUBLISH, args=[petition.id])
        )
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(petition.published, True)
        self.login("julia")
        response = self.client.get(
            reverse(PetitionsRoute.UNPUBLISH, args=[petition.id])
        )
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(petition.published, False)
        petition.published = True
        petition.save()
        self.logout()
        self.login("max")
        response = self.client.get(
            reverse(PetitionsRoute.UNPUBLISH, args=[petition.id])
        )
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(petition.published, True)
        self.logout()
        self.login("sarah")
        response = self.client.get(
            reverse(PetitionsRoute.UNPUBLISH, args=[petition.id])
        )
        petition.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(petition.published, True)
