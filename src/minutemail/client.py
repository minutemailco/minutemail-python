import base64
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests

from .errors import APIError, MinuteMailError, TransportError


class MinuteMailClient:
    """Client for the MinuteMail public API gateway."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.minutemail.co",
        timeout: float = 10.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        Create a client.

        Args:
            api_key: Tenant-scoped API key used for the Authorization header.
            base_url: Gateway origin (without the `/v1` prefix).
            timeout: Per-request timeout in seconds.
            session: Optional requests.Session to reuse connections.
        """
        if not api_key:
            raise MinuteMailError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    # --- Mailboxes ---

    def list_mailboxes(self, *, address: Optional[str] = None) -> Dict[str, Any]:
        """Return `{"items":[...]}` of active mailboxes.
        
        Args:
            address: Optional filter by exact email address.
        """
        params = {}
        if address:
            params["address"] = address
        return self._request("GET", "/v1/mailboxes", params=params)

    def create_mailbox(
        self,
        *,
        domain: str,
        expires_in: Optional[int] = None,
        recoverable: Optional[bool] = None,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a mailbox.
        
        Args:
            domain: Domain for the mailbox (e.g., 'minutemail.cc').
            expires_in: Mailbox lifetime in minutes (1-60).
            recoverable: Archive mailbox when it expires (allows reactivation later).
            tag: Tag for organizing archived mailboxes (required if recoverable=true).
        """
        if recoverable:
            cleaned_tag = (tag or "").strip()
            if not cleaned_tag:
                raise MinuteMailError("tag is required when recoverable is true")
            tag = cleaned_tag
        payload: Dict[str, Any] = {"domain": domain}
        if expires_in is not None:
            payload["expiresIn"] = expires_in
        if recoverable is not None:
            payload["recoverable"] = recoverable
        if tag:
            payload["tag"] = tag
        return self._request("POST", "/v1/mailboxes", json=payload, ok_status=(201,))

    def get_mailbox(self, mailbox_id: str) -> Dict[str, Any]:
        """Fetch a mailbox by id."""
        return self._request("GET", f"/v1/mailboxes/{mailbox_id}")

    def delete_mailbox(self, mailbox_id: str) -> None:
        """Delete a single mailbox."""
        self._request("DELETE", f"/v1/mailboxes/{mailbox_id}", ok_status=(204,))

    def delete_mailboxes(self, ids: List[str]) -> None:
        """Delete multiple mailboxes in a single request.
        
        Args:
            ids: Array of mailbox identifiers to delete.
            
        Note:
            Recoverable mailboxes will be archived, others will be permanently deleted.
            Operation is atomic - all mailboxes are validated before any deletion occurs.
        """
        if not ids:
            raise MinuteMailError("ids cannot be empty")
        payload = {"ids": ids}
        self._request("DELETE", "/v1/mailboxes", json=payload, ok_status=(204,))

    # --- Archived mailboxes ---

    def list_archived_mailboxes(self) -> Dict[str, Any]:
        """Return `{"items":[...]}` of archived mailboxes."""
        return self._request("GET", "/v1/archived-mailboxes")

    def get_archived_mailbox(self, archived_mailbox_id: str) -> Dict[str, Any]:
        """Fetch an archived mailbox by id."""
        return self._request("GET", f"/v1/archived-mailboxes/{archived_mailbox_id}")

    def reactivate_archived_mailbox(
        self, archived_mailbox_id: str, *, expires_in: Optional[int] = None
    ) -> Dict[str, Any]:
        """Reactivate an archived mailbox.
        
        Args:
            archived_mailbox_id: Archived mailbox identifier.
            expires_in: Lifetime in minutes (1-60) for reactivated mailbox.
        """
        payload: Dict[str, Any] = {}
        if expires_in is not None:
            payload["expiresIn"] = expires_in
        return self._request(
            "POST",
            f"/v1/archived-mailboxes/{archived_mailbox_id}/reactivate",
            json=payload if payload else None,
            ok_status=(201,),
        )

    def delete_archived_mailbox(self, archived_mailbox_id: str) -> None:
        """Delete a single archived mailbox permanently."""
        self._request(
            "DELETE",
            f"/v1/archived-mailboxes/{archived_mailbox_id}",
            ok_status=(204,),
        )

    def delete_archived_mailboxes(self, ids: List[str]) -> None:
        """Permanently delete multiple archived mailboxes in a single request.
        
        Args:
            ids: Array of archived mailbox identifiers to delete.
            
        Note:
            This action cannot be undone.
            Operation is atomic - all are validated before any deletion occurs.
        """
        if not ids:
            raise MinuteMailError("ids cannot be empty")
        payload = {"ids": ids}
        self._request("DELETE", "/v1/archived-mailboxes", json=payload, ok_status=(204,))

    # --- Mails ---

    def list_mails(self, mailbox_id: str) -> Dict[str, Any]:
        """Return `{"items":[...]}` of mails for a mailbox."""
        return self._request("GET", f"/v1/mailboxes/{mailbox_id}/mails")

    def get_mail(self, mailbox_id: str, mail_id: str) -> Dict[str, Any]:
        """Fetch a mail with body and attachment summaries."""
        return self._request("GET", f"/v1/mailboxes/{mailbox_id}/mails/{mail_id}")

    def delete_mail(self, mailbox_id: str, mail_id: str) -> None:
        """Delete a single mail."""
        self._request(
            "DELETE",
            f"/v1/mailboxes/{mailbox_id}/mails/{mail_id}",
            ok_status=(204,),
        )

    def delete_mails(self, mailbox_id: str, ids: List[str]) -> None:
        """Delete multiple mails from a mailbox in a single request.
        
        Args:
            mailbox_id: Mailbox identifier.
            ids: Array of mail identifiers to delete.
            
        Note:
            All attachments associated with the mails are also deleted.
            Operation is atomic - either all mails are deleted or none.
        """
        if not ids:
            raise MinuteMailError("ids cannot be empty")
        payload = {"ids": ids}
        self._request(
            "DELETE",
            f"/v1/mailboxes/{mailbox_id}/mails",
            json=payload,
            ok_status=(204,),
        )

    # --- Attachments ---

    def list_attachments(self, mailbox_id: str, mail_id: str) -> Dict[str, Any]:
        """Return `{"items":[...]}` of attachments for a mail."""
        return self._request(
            "GET",
            f"/v1/mailboxes/{mailbox_id}/mails/{mail_id}/attachments",
        )

    def get_attachment(
        self, mailbox_id: str, mail_id: str, attachment_id: str
    ) -> Dict[str, Any]:
        """Fetch an attachment (metadata plus base64 data)."""
        return self._request(
            "GET",
            f"/v1/mailboxes/{mailbox_id}/mails/{mail_id}/attachments/{attachment_id}",
        )

    def delete_attachment(
        self, mailbox_id: str, mail_id: str, attachment_id: str
    ) -> None:
        """Delete a single attachment."""
        self._request(
            "DELETE",
            f"/v1/mailboxes/{mailbox_id}/mails/{mail_id}/attachments/{attachment_id}",
            ok_status=(204,),
        )

    def delete_attachments(
        self, mailbox_id: str, mail_id: str, ids: List[str]
    ) -> None:
        """Delete multiple attachments from a mail in a single request.
        
        Args:
            mailbox_id: Mailbox identifier.
            mail_id: Mail identifier.
            ids: Array of attachment identifiers to delete.
            
        Note:
            Attachment summaries are automatically refreshed after deletion.
            Silently skips non-existent attachment IDs.
        """
        if not ids:
            raise MinuteMailError("ids cannot be empty")
        payload = {"ids": ids}
        self._request(
            "DELETE",
            f"/v1/mailboxes/{mailbox_id}/mails/{mail_id}/attachments",
            json=payload,
            ok_status=(204,),
        )

    # --- Health ---

    def health(self) -> Dict[str, Any]:
        """Liveness probe."""
        return self._request("GET", "/health", auth_required=False)

    def ready(self) -> Dict[str, Any]:
        """Readiness probe."""
        return self._request("GET", "/ready", auth_required=False)

    # --- Internals ---

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Any = None,
        files: Any = None,
        headers: Optional[Dict[str, str]] = None,
        ok_status: Sequence[int] = (200,),
        auth_required: bool = True,
    ) -> Any:
        url = f"{self.base_url}{path}"
        request_headers = {"Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        if auth_required and "Authorization" not in request_headers:
            request_headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=request_headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise TransportError(str(exc)) from exc

        if response.status_code not in ok_status:
            error_body = None
            error_code = None
            message = None
            try:
                error_body = response.json()
                if isinstance(error_body, dict):
                    error_code = error_body.get("error")
                    message = error_body.get("message")
            except ValueError:
                error_body = response.text
            raise APIError(
                response.status_code,
                error=error_code,
                message=message,
                response_text=response.text,
            )

        if response.status_code == 204:
            return None
        if not response.content:
            return None

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except ValueError:
                return response.text
        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def _encode_attachment_data(data: Any) -> Tuple[str, Optional[int]]:
        """
        Base64-encode attachment data and return (encoded, computed_size_bytes).
        Strings are UTF-8 encoded prior to base64.
        """
        raw = MinuteMailClient._coerce_attachment_bytes(data)[0]
        encoded = base64.b64encode(raw).decode("ascii")
        return encoded, len(raw)

    @staticmethod
    def _coerce_attachment_bytes(data: Any) -> Tuple[bytes, int]:
        """
        Convert supported attachment data into bytes and return (bytes, size_bytes).
        """
        if isinstance(data, str):
            raw = data.encode("utf-8")
        elif isinstance(data, (bytes, bytearray, memoryview)):
            raw = bytes(data)
        else:
            raise MinuteMailError(
                "data must be bytes, bytearray, memoryview, or str"
            )
        return raw, len(raw)
