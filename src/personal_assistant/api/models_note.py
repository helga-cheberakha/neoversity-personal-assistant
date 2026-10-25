from collections import UserDict

# Handle note record.
class NoteRecord:
    def __init__(self, id: int, text: str):
        self.id = id
        self.set_text(text)

    def set_text(self, text: str):
        text = text.strip()
        if not text:
            raise ValueError('Note text is required and cannot be empty.')
        
        self.text = text

class NoteBook(UserDict):
    def __init__(self):
        super().__init__()
        self.next_id = 1

    # Find a note record by its id.
    def find_record(self, id: int) -> NoteRecord:
        if id not in self.data:
            raise ValueError('Note not found.')
    
        return self.data[id]

    # Adds a new note record.
    def add_record(self, text: str) -> NoteRecord:
        note = NoteRecord(self.next_id, text)
        self.data[note.id] = note
        self.next_id += 1
        
        return note

    # Delete a contact record by its id.
    def delete_record(self, id: int) -> None:
        note = self.find_record(id)
        if note is not None:
            del self.data[note.id]

    # Search notes by some keywords.
    def search(self, keywords: str) -> list[NoteRecord]:
        keywords = keywords.strip().casefold()
        return [
            note for note in self.data.values()
            if keywords in note.text.casefold()
        ]
