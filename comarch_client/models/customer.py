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


class CustomerSerializer:

    @staticmethod
    def to_comarch(customer: Customer):
        result = dict(
            login=customer.login,
            firstName=customer.first_name,
            lastName=customer.last_name,
            dateOfBirth=customer.birthdate.strftime("%d%m%Y"),
            address=[item.to_comarch() for item in customer.addresses],
            commPrefs=customer.communication_preferences.to_comarch(),
            extAttributes=[item.to_comarch() for item in customer.extended_attributes],
        )
        if customer.card_number:
            result['cardNumber'] = customer.card_number
        return result
