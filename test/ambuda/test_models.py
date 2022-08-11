import ambuda.database as db
from ambuda.queries import get_session


def _cleanup(session, *objects):
    for object in objects:
        session.delete(object)
    session.commit()


def test_user__set_and_check_password(client):
    session = get_session()
    user = db.User(username="test", email="test@ambuda.org")
    user.set_password("my-password")
    session.add(user)
    session.commit()

    assert user.check_password("my-password")
    assert not user.check_password("my-password2")

    _cleanup(session, user)


def test_user__set_and_check_role(client):
    session = get_session()
    user = db.User(username="test", email="test@ambuda.org")
    user.set_password("my-password")
    session.add(user)
    session.flush()

    p1 = session.query(db.Role).filter_by(name=db.SiteRole.P1.value).one()
    user.roles.append(p1)
    session.commit()

    assert user.is_proofreader
    assert not user.is_admin

    _cleanup(session, user)


def test_role__repr(client):
    role = db.Role(name="foo")
    assert repr(role) == "<Role(None, 'foo')>"
