from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from comarch_client.models import ExtendedAttribute, CommunicationPreferences, Address, PhoneData


@dataclass
class Customer:
    """Customer model

    Minimalistic, just enough to enroll (create) an active account via SOAP API.
    """

    # Fields have pretty much self-descriptive names so no docstrings here yet.
    # Phones and title may be omitted for quick enrollment.
    # But they are still required to make account active.
    login: str
    first_name: str
    last_name: str
    birthdate: date
    phones: List[PhoneData]
    addresses: List[Address]
    communication_preferences: CommunicationPreferences
    extended_attributes: List[ExtendedAttribute]

    title: Optional[str] = None
    gender: Optional[str] = None

    # loyalty card number belonging to this customer (may be None for enroll - Comarch will assign it)
    card_number: Optional[str] = None

    def to_comarch(self):
        result = dict(
            login=self.login,
            firstName=self.first_name,
            lastName=self.last_name,
            dateOfBirth=self.birthdate.strftime("%d%m%Y"),
            phones=[item.to_comarch() for item in self.phones],
            address=[item.to_comarch() for item in self.addresses],
            commPrefs=self.communication_preferences.to_comarch(),
            extAttributes=[item.to_comarch() for item in self.extended_attributes],
        )
        optionals = {
            "title": self.title,
            "gender": self.gender,
            "cardNumber": self.card_number,
        }
        result.update({k: v for k, v in optionals.items() if v})
        return result
