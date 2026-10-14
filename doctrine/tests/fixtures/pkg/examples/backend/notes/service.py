"""Notes slice: the service owns every rule about notes."""
from dataclasses import dataclass
from typing import List

MAX_TITLE = 80


class TitleTooLong(Exception):
    """Raised when a note title exceeds the limit."""


@dataclass(frozen=True)
class Note:
    title: str


class NoteService:
    def __init__(self) -> None:
        self._notes: List[Note] = []

    def add(self, title: str) -> Note:
        if len(title) > MAX_TITLE:
            raise TitleTooLong(title)
        note = Note(title=title)
        self._notes.append(note)
        return note
