from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from comarch_client.models import ExtendedAttribute, CommunicationPreferences, Address


@dataclass
class Customer:
    """ Customer model

    Minimalistic, just enough to enroll (create) a new one via SOAP API.
    """

    # Fields have pretty much self-descriptive names so no docstrings here yet.
    login: str
    first_name: str
    last_name: str
    birthdate: date
    addresses: List[Address]
    communication_preferences: CommunicationPreferences
    extended_attributes: List[ExtendedAttribute]

    # loyalty card number belonging to this customer (may be None for enroll - Comarch will assign it)
    card_number: Optional[str] = None

    def to_comarch(self):
        result = dict(
            login=self.login,
            firstName=self.first_name,
            lastName=self.last_name,
            dateOfBirth=self.birthdate.strftime("%d%m%Y"),
            address=[item.to_comarch() for item in self.addresses],
            commPrefs=self.communication_preferences.to_comarch(),
            extAttributes=[item.to_comarch() for item in self.extended_attributes],
        )
        if self.card_number:
            result['cardNumber'] = self.card_number
        return result
