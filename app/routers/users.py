"""API per la gestione degli utenti."""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.data.db import SessionDep
from app.models.registration import Registration
from app.models.user import User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[User])
def list_users(session: SessionDep) -> list[User]:
    """Restituisce la lista di tutti gli utenti presenti nel database."""
    return list(session.exec(select(User)).all())


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: SessionDep) -> User:
    """Crea un nuovo utente.

    Restituisce 409 Conflict se esiste gia' un utente con lo stesso username.
    """
    if session.get(User, user.username) is not None:
        raise HTTPException(status_code=409, detail="Username gia' esistente")

    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("")
def delete_all_users(session: SessionDep) -> dict[str, str]:
    """(opzionale) Elimina tutti gli utenti presenti nel database."""
    for user in session.exec(select(User)).all():
        session.delete(user)
    session.commit()
    return {"detail": "Tutti gli utenti sono stati eliminati"}


@router.get("/{username}", response_model=User)
def get_user(username: str, session: SessionDep) -> User:
    """Restituisce l'utente con lo username indicato, oppure 404 se non esiste."""
    user = session.get(User, username)
    if user is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return user


@router.delete("/{username}")
def delete_user(username: str, session: SessionDep) -> dict[str, str]:
    """(opzionale) Elimina l'utente indicato e, a cascata, le sue registrazioni."""
    user = session.get(User, username)
    if user is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    registrations = session.exec(
        select(Registration).where(Registration.username == username)
    ).all()
    for registration in registrations:
        session.delete(registration)

    session.delete(user)
    session.commit()
    return {"detail": f"Utente {username} eliminato"}
