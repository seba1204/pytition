from django.apps import apps
from django.db.models import Model


def get_model(label: str) -> type[Model]:
    """Get a model class from its label."""
    # label is from model_ref, e.g. "signatures.Signature"
    # split into app_label and model_name
    app_label, model_name = label.split(".")
    model = apps.get_model(app_label, model_name)
    if model is None:
        raise ValueError(f"Model {label} not found")
    return model
