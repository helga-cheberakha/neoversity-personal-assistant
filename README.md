# Personal Assistant

`backend-project`

Contact and note models, JSON storage, and a FastAPI API.

`frontend-project`

Console client that communicates with the backend over HTTP.

Python 3.11 or newer is required.

## Run the project

From the project root, open a terminal and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./backend-project -e ./frontend-project
```

### Run the backend

```bash
source .venv/bin/activate
python -m uvicorn personal_assistant.main:app --reload --host 127.0.0.1 --port 8000
```

### Run the frontend

Open a second terminal and run:

```bash
source .venv/bin/activate
personal-assistant
```

API documentation: http://127.0.0.1:8000/docs.
The default backend URL is `http://127.0.0.1:8000`.
To change it, set `ASSISTANT_API_URL` before starting the frontend:

```bash
export ASSISTANT_API_URL=http://127.0.0.1:8000
```

## Command format

Enter one command at a time in the assistant prompt.
Put arguments containing spaces in double quotation marks, such as
`"Michael Peterson"` or `"Buy a birthday gift"`.
Close every quotation mark before submitting a command.

In the syntax below, `<value>` means a required argument and `[value]` means
an optional argument. Do not type the angle brackets or square brackets.
Command names are case-insensitive. Use lowercase field names with `edit`.

## Contacts book

A contact has a required name and phone number, plus an optional email,
postal address, and birthday. A contact can have multiple phone numbers,
but only one email, address, and birthday.

### Data formats

| Field | Expected data | Example |
| --- | --- | --- |
| Name | Non-empty text. Use quotes if it contains spaces. Names are unique without case sensitivity. | `Michael` or `"Michael Peterson"` |
| Phone | Exactly 10 digits, without spaces, hyphens, or a country-code prefix. | `0671234567` |
| Email | A simple email address containing a local part, `@`, and a domain with a dot. Spaces are not allowed. | `michael.peterson@example.com` |
| Address | Non-empty free text. Use quotes if it contains spaces. | `"6366 McGowen St, Birmingham"` |
| Birthday | A valid calendar date in `DD.MM.YYYY` format. | `25.10.1990` |


### 1. Add a contact or another phone number

Syntax: `add <name> <phone>`

Creates a contact with a name and phone number. If the name already exists,
adds the number to that contact. The same number is not added twice to one
contact.

```text
add "Michael Peterson" 0671234567
add "Michael Peterson" 0501234567
```

Use `edit` to add the optional email, address, and birthday afterwards.

### 2. Edit a contact field

Syntax: `edit <name> <field> <value>`

Updates one field of an existing contact. Supported field names are `name`,
`email`, `address`, and `birthday`. Values must follow the formats above.

```text
edit "Michael Peterson" email michael.peterson@example.com
edit "Michael Peterson" address "6366 McGowen St, Birmingham"
edit "Michael Peterson" birthday 25.10.1990
```

To rename a contact, provide a non-empty name that is not used by another
contact. Use the new name in subsequent commands:

```text
edit "Michael Peterson" name "Michael Newname"
show "Michael Newname"
```

Use an empty quoted string to clear an optional field:

```text
edit "Michael Newname" email ""
edit "Michael Newname" address ""
edit "Michael Newname" birthday ""
```

The name cannot be cleared.

### 3. Show a contact

Syntax: `show <name>`

Displays the contact name, all phone numbers, email, address, and birthday.
Fields without a value are shown as `-`. The contact must exist.

```text
show "Michael Peterson"
```

### 4. Delete a contact

Syntax: `delete <name>`

Deletes an existing contact, including all phone numbers and optional fields.
The deletion is saved immediately.

```text
delete "Michael Peterson"
```

### 5. List all contacts

Syntax: `all`

Displays all contacts with their phone numbers and optional fields.
Takes no arguments. Displays `No contacts found.` if the book is empty.

```text
all
```

### 6. Search contacts

Syntax: `search <text>`

Finds contacts by a partial name, phone number, email, or postal address.
Search is case-insensitive. Put a search phrase containing spaces in quotes.
An empty query (`search ""`) returns all contacts.

```text
search "Michael"
search "Birmingham"
search "example.com"
search "067"
```

### 7. Change a phone number

Syntax: `change-phone <name> <old_phone> <new_phone>`

Replaces one existing phone number. Both numbers must contain exactly
10 digits. The contact and old number must exist. The new number must not
already belong to this contact.

```text
change-phone "Michael Peterson" 0501234567 0931234567
```

### 8. Show phone numbers

Syntax: `phone <name>`

Displays all phone numbers for an existing contact, separated by commas.

```text
phone "Michael Peterson"
```

### 9. Add or update a birthday

Syntax: `add-birthday <name> <DD.MM.YYYY>`

Sets the birthday of an existing contact. Replaces the previous birthday
if one is already set. Use a valid calendar date. For example, `31.02.1990`
is invalid. This command has the same effect as editing the `birthday` field.

```text
add-birthday "Michael Peterson" 25.10.1990
```

### 10. Show a birthday

Syntax: `show-birthday <name>`

Displays the birthday of an existing contact in `DD.MM.YYYY` format.
Displays `No birthday set.` if the contact has no birthday.

```text
show-birthday "Michael Peterson"
```

### 11. List upcoming birthdays

Syntax: `birthdays [days]`

Lists contacts whose next birthday falls between today and the specified
number of days from today. `days` must be a whole number from
0 to 366. The default is 7. Use 0 to select today birthdays.

```text
birthdays
birthdays 7
birthdays 30
birthdays 0
```

The output shows each contact name and congratulation date. Weekend
congratulations move to Monday. February 29 birthdays use March 1 in
non-leap years. The congratulation date may fall outside the selected
interval because selection uses the birthday date.

## Notes

Notes contain non-empty text and have automatically assigned positive
integer IDs.
Use the ID returned by `add-note` or displayed by `notes`.

### 1. Add a note

Syntax: `add-note <text>`

Creates a note and displays its ID. Put text containing spaces in quotes.
Empty text and text containing only whitespace are rejected.

```text
add-note "Buy a birthday gift"
```

Example response for the first note: `Note added. ID: 1`.

### 2. Edit a note

Syntax: `edit-note <id> <text>`

Replaces the entire text of an existing note. The ID must be a positive
integer belonging to an existing note. The new text cannot be empty or
contain only whitespace.

```text
edit-note 1 "Buy a book"
```

### 3. Delete a note

Syntax: `delete-note <id>`

Deletes an existing note by its positive integer ID. The deletion is saved
immediately. The deleted ID will not be reused.

```text
delete-note 1
```

### 4. List all notes

Syntax: `notes`

Displays every note with its ID and text. Takes no arguments.
Displays `No notes found.` if there are no notes.

```text
notes
```

Example output:

```text
1: Buy a birthday gift
2: Call the dentist
```

### 5. Search notes

Syntax: `search-notes <text>`

Finds notes containing the supplied text. Search is case-insensitive.
Put phrases containing spaces in quotes. An empty query returns all notes.
Results include IDs and note text.

```text
search-notes "gift"
search-notes "birthday gift"
```

## General commands

### 1. Display a greeting

Syntax: `hello`

Displays `How can I help you?`. Takes no arguments.

```text
hello
```

### 2. Display help

Syntax: `help`

Displays the available commands and usage examples. Takes no arguments.

```text
help
```

### 3. Exit the assistant

Syntax: `exit` or `close`

Closes the console client. Both commands take no arguments.

```text
exit
```

## Data storage

The backend stores `contacts.json` and `notes.json` in `~/.personal_assistant/`.
The directory is created automatically on the first save.

To change the directory, set this variable before starting the backend:

```bash
export ASSISTANT_DATA_DIR="$HOME/.personal_assistant"
```

A missing or empty file starts a new collection.
