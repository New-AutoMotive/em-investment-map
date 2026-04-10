"""
Data validation schemas using Pydantic
"""

from typing import Optional, Literal, List, Tuple
from pydantic import BaseModel, Field, field_validator


class Location(BaseModel):
    """Geographic location"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class CountryStats(BaseModel):
    """Country statistics model"""
    id: str = Field(..., min_length=3, max_length=3, description="ISO 3166-1 alpha-3 country code")
    name: str = Field(..., min_length=1, description="Country name")
    chargingDensity: float = Field(..., ge=0, description="Charging points per 100km²")
    evMarketShare: float = Field(..., ge=0, le=100, description="BEV market share percentage (2025)")
    description: Optional[str] = Field(default="", description="Optional country description")
    
    @field_validator('id')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Ensure country code is uppercase"""
        return v.upper()
    
    class Config:
        extra = 'forbid'  # Don't allow extra fields


class ManufacturingSite(BaseModel):
    """Manufacturing site model"""
    id: str = Field(..., min_length=1, description="Unique site identifier")
    name: str = Field(..., min_length=1, description="Site name")
    countryId: str = Field(..., min_length=3, max_length=3, description="ISO 3166-1 alpha-3 country code")
    type: Literal['battery', 'ev'] = Field(..., description="Site type: battery or ev")
    manufacturer: str = Field(..., min_length=1, description="Manufacturer/company name")
    location: Location = Field(..., description="Geographic coordinates")
    
    # Optional fields
    city: Optional[str] = Field(default=None, description="City name")
    description: Optional[str] = Field(default=None, description="Site description")
    produces: Optional[str] = Field(default=None, description="What is produced at this site")
    brands: Optional[str] = Field(default=None, description="Brands manufactured")
    evConversionPlans: Optional[str] = Field(default=None, description="EV conversion plans")
    investmentAmount: Optional[str] = Field(default=None, description="Investment amount")
    source: Optional[str] = Field(default=None, description="Source name")
    sourceUrl: Optional[str] = Field(default=None, description="Source URL")
    
    @field_validator('countryId')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Ensure country code is uppercase"""
        return v.upper()
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure ID doesn't have special characters that could cause issues"""
        # Allow alphanumeric, hyphens, underscores
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError(f"ID contains invalid characters: {v}")
        return v
    
    class Config:
        extra = 'forbid'  # Don't allow extra fields


def validate_country(data: dict) -> CountryStats:
    """
    Validate country data
    
    Args:
        data: Dictionary with country data
        
    Returns:
        Validated CountryStats model
        
    Raises:
        ValidationError: If data doesn't match schema
    """
    return CountryStats(**data)


def validate_site(data: dict) -> ManufacturingSite:
    """
    Validate manufacturing site data
    
    Args:
        data: Dictionary with site data
        
    Returns:
        Validated ManufacturingSite model
        
    Raises:
        ValidationError: If data doesn't match schema
    """
    return ManufacturingSite(**data)


def validate_batch_countries(data_list: List[dict]) -> Tuple[List[CountryStats], List[dict]]:
    """
    Validate multiple countries, separating valid and invalid records
    
    Args:
        data_list: List of country data dictionaries
        
    Returns:
        Tuple of (valid_countries, invalid_records_with_errors)
    """
    valid = []
    invalid = []
    
    for idx, data in enumerate(data_list):
        try:
            country = validate_country(data)
            valid.append(country)
        except Exception as e:
            invalid.append({
                'row': idx + 1,
                'data': data,
                'error': str(e)
            })
    
    return valid, invalid


def validate_batch_sites(data_list: List[dict]) -> Tuple[List[ManufacturingSite], List[dict]]:
    """
    Validate multiple manufacturing sites, separating valid and invalid records
    
    Args:
        data_list: List of site data dictionaries
        
    Returns:
        Tuple of (valid_sites, invalid_records_with_errors)
    """
    valid = []
    invalid = []
    
    for idx, data in enumerate(data_list):
        try:
            site = validate_site(data)
            valid.append(site)
        except Exception as e:
            invalid.append({
                'row': idx + 1,
                'data': data,
                'error': str(e)
            })
    
    return valid, invalid
