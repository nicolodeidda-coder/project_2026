"""Modello ORM per la tabella `event`."""

from datetime import datetime, timezone

from pydantic import NaiveDatetime, field_validator
from sqlmodel import Field, SQLModel


class EventBase(SQLModel):
    """Campi comuni all'evento, con le regole di validazione dell'input."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    # NaiveDatetime: la data viene salvata senza fuso orario, come richiesto
    # dalle versioni recenti di SQLModel per le colonne di tipo datetime.
    date: NaiveDatetime
    location: str = Field(min_length=1, max_length=200)

    @field_validator("title", "location")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """Rifiuta i campi composti da soli spazi e rimuove quelli superflui."""
        value = value.strip()
        if not value:
            raise ValueError("il campo non puo' essere vuoto")
        return value

    @field_validator("date", mode="before")
    @classmethod
    def normalizza_data(cls, value: object) -> object:
        """Accetta anche le date con fuso orario, convertendole in UTC e togliendolo.

        Il form del frontend invia date senza fuso (es. 2026-11-19T22:14), mentre
        la documentazione delle API mostra date con la Z finale (UTC): questo
        metodo fa in modo che entrambe le forme vengano accettate. I valori non
        riconosciuti vengono lasciati passare, cosi' e' Pydantic a produrre
        l'errore 422 di validazione.
        """
        if isinstance(value, str):
            testo = value.strip()
            if testo.endswith(("Z", "z")):
                testo = testo[:-1] + "+00:00"
            try:
                value = datetime.fromisoformat(testo)
            except ValueError:
                return value

        if isinstance(value, datetime) and value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)

        return value


class Event(EventBase, table=True):
    """Evento memorizzato nel database; l'`id` e' assegnato automaticamente."""

    id: int | None = Field(default=None, primary_key=True)


class EventCreate(EventBase):
    """Dati accettati in input per creare o aggiornare un evento."""
