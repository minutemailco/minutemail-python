# MinuteMail Python SDK

Python client for the MinuteMail public API gateway (`/v1`). It handles auth headers, request wiring, and attachment encoding so you can focus on product logic.

**Resources:**
- [Official Documentation](https://docs.minutemail.co/en/sdk/getting-started/)
- [MinuteMail Platform](https://minutemail.co)

## Installation

```bash
pip install minutemail-sdk
```

Or for development:
```bash
pip install -e .
```

Requirements: Python 3.9+ and `requests>=2.31.0`.

## Authentication

Every authenticated call sends `Authorization: Bearer <api-key>`. Pass your tenant-scoped API key when constructing the client:

```python
from minutemail import MinuteMailClient

client = MinuteMailClient(api_key="your-api-key")
```

## Usage examples

### Create and use a mailbox

```python
from minutemail import MinuteMailClient, APIError

client = MinuteMailClient(api_key="your-api-key")

try:
    mailbox = client.create_mailbox(
        domain="minutemail.cc",
        recoverable=True,
        tag="onboarding",
        expires_in="20m",
    )
    print("Mailbox address:", mailbox["address"])

except APIError as exc:
    print("Request failed:", exc)
```

## Client classes

- `MinuteMailClient`: Production-safe surface for managing mailboxes, reading mail, and deleting data.

### Constructor parameters

- `api_key` (str, required): Tenant-scoped API key used for all authenticated calls.
- `timeout` (float, default `10.0`): Per-request timeout in seconds.
- `session` (requests.Session, optional): Provide to reuse connections/custom adapters.

### MinuteMailClient methods (production)

**Mailboxes**
- `list_mailboxes()` → dict `{items:[...]}`; returns active mailboxes sorted by `createdAt`. Auth required.
- `create_mailbox(domain, recoverable=None, tag=None, expires_in=None)` → mailbox dict (201).  
  - `domain` (str, required): Domain to use.  
  - `recoverable` (bool, optional): When `True`, mailbox is archived on delete/expiry.  
  - `tag` (str, optional): Required when `recoverable=True`.  
  - `expires_in` (str, optional): TTL like `"20m"` or `"2h"`.
- `get_mailbox(mailbox_id)` → mailbox dict.  
  - `mailbox_id` (str, required).
- `delete_mailbox(mailbox_id)` → `None` (204).  
  - `mailbox_id` (str, required).

**Archived mailboxes**
- `list_archived_mailboxes()` → dict `{items:[...]}` of archived mailbox records.
- `get_archived_mailbox(archived_mailbox_id)` → archived mailbox dict.  
  - `archived_mailbox_id` (str).
- `reactivate_archived_mailbox(archived_mailbox_id, expires_in=None)` → newly created mailbox dict (201).  
  - `expires_in` (str, optional): TTL for the new mailbox; defaults to service TTL.
- `delete_archived_mailbox(archived_mailbox_id)` → `None` (204).

**Mails**
- `list_mails(mailbox_id)` → dict `{items:[...]}` newest-first.  
  - `mailbox_id` (str).
- `get_mail(mailbox_id, mail_id)` → mail dict including `attachments` summaries and `hasAttachments`.  
  - `mail_id` (str).
- `delete_mail(mailbox_id, mail_id)` → `None` (204).

**Attachments**
- `list_attachments(mailbox_id, mail_id)` → dict `{items:[...]}` metadata only.  
  - `mail_id` (str).
- `get_attachment(mailbox_id, mail_id, attachment_id)` → metadata + base64 `data`.  
  - `attachment_id` (str).
- `delete_attachment(mailbox_id, mail_id, attachment_id)` → `None` (204).

## Errors

- Network/timeouts raise `TransportError`.
- Non-2xx responses raise `APIError` with `status_code`, `error`, `message`, and a stringified response preview.

Example:

```python
from minutemail import APIError

try:
    client.delete_mailbox("missing-id")
except APIError as exc:
    print(exc.status_code, exc.error, exc.message)
```

## Configuration notes

- `expires_in` mirrors the API: Go-style durations like `15m`, `2h`, or integer minutes.
- Attachments: strings are UTF-8 encoded then base64 encoded; override `size_bytes` if the decoded size is already known.

## Development

1. Create a virtualenv and install dependencies: `pip install -e .`
2. Run your scripts/tests using your API key.

Planned: unit tests against a mocked gateway; semantic versioning for releases.
