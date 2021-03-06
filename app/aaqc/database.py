from sqlalchemy.orm.session import Session
from sqlalchemy import insert
from . import models


def fetch_user(db: Session, ident: str):
    return db.query(models.User).filter(models.User.email == ident).one_or_none()


def get_user_by_id(db: Session, id: int):
    return db.query(models.User).get(id)


def create_group(
    db: Session,
    name: str,
    user_id: int,
):
    cursor = db.execute(insert(models.Group).values(name=name))
    db.execute(
        insert(models.UserGroups).values(
            user=user_id, group=cursor.inserted_primary_key[0], admin=True
        )
    )
    db.commit()

    return cursor.inserted_primary_key[0]
