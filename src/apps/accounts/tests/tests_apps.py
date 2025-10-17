import importlib

from django.test import TestCase


class AccountsAppImportTest(TestCase):
    def test_accounts_app_importable(self):
        module = importlib.import_module("apps.accounts")
        self.assertIsNotNone(module)
