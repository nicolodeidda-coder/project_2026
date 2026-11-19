"""API per la gestione delle registrazioni utente-evento."""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.data.db import SessionDep
from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.get("", response_model=list[Registration])
def list_registrations(session: SessionDep) -> list[Registration]:
    """Restituisce la lista di tutte le registrazioni presenti nel database."""
    return list(session.exec(select(Registration)).all())


@router.delete("")
def delete_registration(
    username: str, event_id: int, session: SessionDep
) -> dict[str, str]:
    """(opzionale) Elimina la registrazione identificata da username ed event_id.

    Restituisce 404 se l'utente, l'evento o la registrazione non esistono.
    """
    if session.get(User, username) is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    if session.get(Event, event_id) is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    registration = session.get(Registration, (username, event_id))
    if registration is None:
        raise HTTPException(status_code=404, detail="Registrazione non trovata")

    session.delete(registration)
    session.commit()
    return {"detail": "Registrazione eliminata"}
