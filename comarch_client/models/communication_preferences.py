from dataclasses import dataclass


@dataclass
class CommunicationPreferences:
    """Customer communication preferences."""

    # preferred contact language
    language: str

    # Preferred channel for receiving statements. S –
    # SMS(text message), E – email.
    statement: str

    # Indicates if communication with member thru Call
    # Center is permitted or not
    permission_call_center: bool

    # Indicates if communication with member thru
    # email is permitted or not
    permission_email: bool

    def to_comarch(self) -> dict:
        return dict(
            preferredLanguage=self.language,
            statementPreference=self.statement,
            commPermissionCc=self.permission_call_center,
            commPermissionEmail=self.permission_email
        )
