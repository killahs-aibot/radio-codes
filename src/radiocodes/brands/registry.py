# -*- coding: utf-8 -*-
"""
Brand registry — maps brand names to algorithm instances.
"""

from typing import Dict, Type, List, Optional
from dataclasses import dataclass

from radiocodes.algorithms.base import BaseRadioAlgorithm


@dataclass
class BrandInfo:
    """Metadata about a supported brand."""
    name: str  # Display name
    algorithm: Optional[BaseRadioAlgorithm]  # None = coming soon
    icon: str  # Emoji or icon name
    serial_hint: str  # Where to find serial
    serial_format: str  # Human-readable format description
    code_length: int  # Number of digits in output code
    status: str  # "working" or "coming_soon"


# Import all algorithm modules
# Fill in real implementations as research finds them
from radiocodes.algorithms.ford_m import FordMAlgorithm
from radiocodes.algorithms.ford_v import FordVAlgorithm
from radiocodes.algorithms.renault import RenaultAlgorithm
from radiocodes.algorithms.vw_rcd import VWRCDAlgorithm
from radiocodes.algorithms.vauxhall import VauxhallAlgorithm
from radiocodes.algorithms.peugeot import PeugeotAlgorithm
from radiocodes.algorithms.fiat import FiatAlgorithm
from radiocodes.algorithms.nissan import NissanAlgorithm
from radiocodes.algorithms.honda import HondaAlgorithm
from radiocodes.algorithms.toyota import ToyotaAlgorithm
from radiocodes.algorithms.alfa import AlfaAlgorithm
from radiocodes.algorithms.chrysler import ChryslerAlgorithm
from radiocodes.algorithms.jaguar import JaguarAlgorithm


# Registry of all brands
BRAND_REGISTRY: Dict[str, BrandInfo] = {
    "ford": BrandInfo(
        name="Ford",
        algorithm=FordMAlgorithm(),  # Default to M series, user picks model
        icon="🚗",
        serial_hint="Look for a label on the radio casing or press preset 1 & 6 together",
        serial_format="6-digit serial (e.g. 123456)",
        code_length=4,
        status="working",
    ),
    "renault": BrandInfo(
        name="Renault / Dacia",
        algorithm=RenaultAlgorithm(),
        icon="🏎️",
        serial_hint="Radio shows 'PRE-CODE' followed by 4 characters, or check label",
        serial_format="1 letter + 3 digits (e.g. D123)",
        code_length=4,
        status="working",
    ),
    "vw": BrandInfo(
        name="VW / Audi / Seat",
        algorithm=VWRCDAlgorithm(),
        icon="🇩🇪",
        serial_hint="Serial printed on label or shown on screen with CODE",
        serial_format="14-character serial (e.g. VWZ1Z2E12345678)",
        code_length=4,
        status="working",
    ),
    "vauxhall": BrandInfo(
        name="Vauxhall / Opel",
        algorithm=VauxhallAlgorithm(),
        icon="🇬🇧",
        serial_hint="Serial on label or enter 0000 to display serial",
        serial_format="4-6 character serial",
        code_length=4,
        status="working",
    ),
    "peugeot": BrandInfo(
        name="Peugeot / Citroën",
        algorithm=PeugeotAlgorithm(),
        icon="🇫🇷",
        serial_hint="Serial on label, RT3/RT4: enter SETUP or SETTINGS to find serial",
        serial_format="4-6 character serial",
        code_length=4,
        status="working",
    ),
    "fiat": BrandInfo(
        name="Fiat / Alfa",
        algorithm=FiatAlgorithm(),
        icon="🇮🇹",
        serial_hint="Serial on label or check the radio casing",
        serial_format="4-6 character serial",
        code_length=4,
        status="working",
    ),
    "nissan": BrandInfo(
        name="Nissan",
        algorithm=NissanAlgorithm(),
        icon="🇯🇵",
        serial_hint="12-character serial, serial 5 on the radio label",
        serial_format="12 characters",
        code_length=4,
        status="working",
    ),
    "honda": BrandInfo(
        name="Honda",
        algorithm=HondaAlgorithm(),
        icon="🏁",
        serial_hint="Serial on label on the radio casing",
        serial_format="5-10 character serial",
        code_length=5,
        status="coming_soon",
    ),
    "toyota": BrandInfo(
        name="Toyota / Lexus",
        algorithm=ToyotaAlgorithm(),
        icon="�️",
        serial_hint="16-character ERC code found on radio label",
        serial_format="16-character alphanumeric",
        code_length=5,
        status="coming_soon",
    ),
    "alfa": BrandInfo(
        name="Alfa Romeo",
        algorithm=AlfaAlgorithm(),
        icon="🐍",
        serial_hint="Serial on radio label or check vehicle documents",
        serial_format="4-6 character serial",
        code_length=4,
        status="coming_soon",
    ),
    "chrysler": BrandInfo(
        name="Chrysler / Dodge / Jeep",
        algorithm=ChryslerAlgorithm(),
        icon="🇺🇸",
        serial_hint="Serial on Uconnect label or check vehicle documents",
        serial_format="4-6 character serial",
        code_length=4,
        status="coming_soon",
    ),
    "jaguar": BrandInfo(
        name="Jaguar / Land Rover",
        algorithm=JaguarAlgorithm(),
        icon="🦁",
        serial_hint="InControl serial found on radio or in vehicle settings",
        serial_format="5-8 character serial",
        code_length=4,
        status="coming_soon",
    ),
}


def get_brand(key: str) -> Optional[BrandInfo]:
    """Get brand info by key."""
    return BRAND_REGISTRY.get(key.lower())


def get_all_brands() -> List[BrandInfo]:
    """Get all registered brands sorted by status (working first)."""
    brands = list(BRAND_REGISTRY.values())
    return sorted(brands, key=lambda b: (b.status != "working", b.name))


def get_working_brands() -> List[BrandInfo]:
    """Get only brands with working algorithms."""
    return [b for b in BRAND_REGISTRY.values() if b.status == "working"]
