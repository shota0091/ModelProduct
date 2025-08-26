from app.repositories.memory_profile import InMemoryProfileRepository
from app.models.profile import Profile

def test_upsert_get_delete():
    repo = InMemoryProfileRepository()

    p = Profile(user_id=123, name="A", comment="hi")
    repo.upsert(p)

    got = repo.get(123)
    assert got is not None
    assert got.name == "A"

    repo.set_message_id(123, 999)
    assert repo.get_message_id(123) == 999

    repo.delete(123)
    assert repo.get(123) is None
    assert repo.get_message_id(123) is None

