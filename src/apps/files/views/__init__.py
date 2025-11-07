"""Initialization file for files views module."""

from .tinymce_image_upload import tinymce_image_upload
from .upload import upload

__all__ = [
    "upload",
    "tinymce_image_upload",
]
