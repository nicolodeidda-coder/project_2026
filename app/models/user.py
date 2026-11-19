"""Modello ORM per la tabella `user`."""

import re

from pydantic import field_validator
from sqlmodel import Field, SQLModel

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserBase(SQLModel):
    """Campi comuni all'utente, con le regole di validazione dell'input."""

    username: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=200)

    @field_validator("username", "name")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """Rifiuta i campi composti da soli spazi e rimuove quelli superflui."""
        value = value.strip()
        if not value:
            raise ValueError("il campo non puo' essere vuoto")
        return value

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        """Verifica che l'email abbia un formato plausibile."""
        value = value.strip()
        if not EMAIL_REGEX.match(value):
            raise ValueError("formato email non valido")
        return value


class User(UserBase, table=True):
    """Utente registrato nel sistema.

    La chiave primaria e' lo `username`, scelto alla creazione.
    """

    username: str = Field(primary_key=True, max_length=50)


class UserCreate(UserBase):
    """Dati accettati in input per creare un utente o registrarlo a un evento."""
