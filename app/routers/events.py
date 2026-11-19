"""API per la gestione degli eventi."""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.data.db import SessionDep
from app.models.event import Event, EventCreate
from app.models.registration import Registration
from app.models.user import User, UserCreate

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[Event])
def list_events(session: SessionDep) -> list[Event]:
    """Restituisce la lista di tutti gli eventi presenti nel database."""
    return list(session.exec(select(Event)).all())


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, session: SessionDep) -> Event:
    """Crea un nuovo evento a partire dai dati validati ricevuti nel corpo della richiesta."""
    db_event = Event(**event.model_dump())
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router.delete("")
def delete_all_events(session: SessionDep) -> dict[str, str]:
    """(opzionale) Elimina tutti gli eventi presenti nel database."""
    for event in session.exec(select(Event)).all():
        session.delete(event)
    session.commit()
    return {"detail": "Tutti gli eventi sono stati eliminati"}


@router.get("/{event_id}", response_model=Event)
def get_event(event_id: int, session: SessionDep) -> Event:
    """Restituisce l'evento con l'id indicato, oppure 404 se non esiste."""
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event


@router.put("/{event_id}", response_model=Event)
def update_event(event_id: int, data: EventCreate, session: SessionDep) -> Event:
    """Aggiorna tutti i campi dell'evento indicato, oppure 404 se non esiste."""
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    for field, value in data.model_dump().items():
        setattr(event, field, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}")
def delete_event(event_id: int, session: SessionDep) -> dict[str, str]:
    """(opzionale) Elimina l'evento indicato e, a cascata, le sue registrazioni."""
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    registrations = session.exec(
        select(Registration).where(Registration.event_id == event_id)
    ).all()
    for registration in registrations:
        session.delete(registration)

    session.delete(event)
    session.commit()
    return {"detail": f"Evento {event_id} eliminato"}


@router.post("/{event_id}/register", response_model=Registration)
def register_user(event_id: int, data: UserCreate, session: SessionDep) -> Registration:
    """Registra un utente all'evento indicato.

    Se l'utente non esiste ancora viene creato automaticamente nella tabella
    `user`. Se la registrazione esiste gia' viene restituita quella esistente,
    senza creare duplicati. Restituisce 404 se l'evento non esiste.
    """
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento non trovato")

    if session.get(User, data.username) is None:
        session.add(User(**data.model_dump()))

    registration = session.get(Registration, (data.username, event_id))
    if registration is None:
        registration = Registration(username=data.username, event_id=event_id)
        session.add(registration)

    session.commit()
    session.refresh(registration)
    return registration
