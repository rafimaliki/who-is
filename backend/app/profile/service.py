from app.shared.store import store

from .types import ProfileResponse


def get_profile(profile_id: str) -> ProfileResponse | None:
    return store.profiles.get(profile_id)
