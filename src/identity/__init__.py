"""Identity and face-recognition adapter package."""

from .compreface import CompreFaceAdapter, IdentityResult, crop_person_region

__all__ = ["CompreFaceAdapter", "IdentityResult", "crop_person_region"]
