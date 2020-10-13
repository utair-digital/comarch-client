from dataclasses import dataclass
from typing import Optional


@dataclass
class Address:
    """Customer's address"""

    # Indicates whether this address is default.
    default_address: bool

    # Default address: H – home, B – business. Regards
    # address fields listed below. By default H - home.
    address_type: str

    # Street with house and flat numbers
    address_line_1: str

    # 3 letter country code (ISO 3166-1 alpha-3)
    country: str

    # City name
    city: str

    # Zip code (post code)
    zip_code: str

    # Member’s email address, used as a login.
    email: str

    # Street with house and flat numbers
    address_line_2: Optional[str] = None

    # Street with house and flat numbers
    address_line_3: Optional[str] = None

    # State name
    state: Optional[str] = None

    def to_comarch(self) -> dict:
        return dict(
            defaultAddress=self.default_address,
            addressType=self.address_type,
            addressLine1=self.address_line_1,
            addressLine2=self.address_line_2,
            addressLine3=self.address_line_3,
            country=self.country,
            state=self.state,
            city=self.city,
            zipCode=self.zip_code,
            email=self.email
        )
