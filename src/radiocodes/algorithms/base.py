# -*- coding: utf-8 -*-
"""
Base class and interface for radio code algorithms.

All brand algorithms inherit from BaseRadioAlgorithm and implement
validate_serial() and calculate().
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple
import re


@dataclass
class RadioInfo:
    """Information about a radio and its unlock code."""
    brand: str
    model: str
    serial: str
    code: str
    is_valid: bool
    error_message: Optional[str] = None


class BaseRadioAlgorithm(ABC):
    """
    Base class for all radio code algorithms.

    Subclass this for each brand/radio type.
    """

    # Display name of the brand
    brand_name: str = "Unknown"

    # List of supported model names for this brand
    supported_models: List[str] = []

    # How many digits the output code has
    code_length: int = 4

    # Regex pattern for validating serial numbers
    # Override in subclass with actual pattern
    serial_pattern: str = r""

    # Human-readable description of the serial format
    serial_format_hint: str = ""

    # Where to find the serial number on this radio
    serial_location: str = ""

    @abstractmethod
    def validate_serial(self, serial: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a serial number format.

        Args:
            serial: The serial number string from the user

        Returns:
            (is_valid, error_message)
            error_message is None if valid, or a string describing the error
        """
        pass

    @abstractmethod
    def calculate(self, serial: str) -> str:
        """
        Calculate the unlock code from a serial number.

        Args:
            serial: A validated serial number string

        Returns:
            The unlock code as a string of digits
        """
        pass

    def calculate_safe(self, serial: str) -> RadioInfo:
        """
        Safe wrapper around calculate() that handles validation and errors.

        Returns a RadioInfo dataclass instead of raising exceptions.
        """
        is_valid, error = self.validate_serial(serial)
        if not is_valid:
            return RadioInfo(
                brand=self.brand_name,
                model=self.supported_models[0] if self.supported_models else "Unknown",
                serial=serial,
                code="",
                is_valid=False,
                error_message=error,
            )

        try:
            code = self.calculate(serial)
            return RadioInfo(
                brand=self.brand_name,
                model=self.supported_models[0] if self.supported_models else "Unknown",
                serial=serial,
                code=code,
                is_valid=True,
            )
        except Exception as e:
            return RadioInfo(
                brand=self.brand_name,
                model=self.supported_models[0] if self.supported_models else "Unknown",
                serial=serial,
                code="",
                is_valid=False,
                error_message=f"Calculation error: {e}",
            )

    def format_serial(self, raw: str) -> str:
        """
        Normalize a serial by removing spaces, dashes, and converting to uppercase.
        """
        return re.sub(r"[\s\-]", "", raw).upper()

    def pad_serial(self, serial: str, length: int, fill_char: str = "0") -> str:
        """Pad serial with leading zeros to minimum length."""
        return serial.zfill(length)
