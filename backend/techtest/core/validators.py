import re
from typing import List, Optional


class FieldValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_name(name: str, field_name: str, min_length: int = 2, max_length: int = 100) -> List[str]:
        """Validate name fields (first_name, last_name, etc.)"""
        errors = []
        
        if not name or not name.strip():
            errors.append(f"{field_name} is required")
            return errors
            
        name = name.strip()
        
        if len(name) < min_length:
            errors.append(f"{field_name} must be at least {min_length} characters")
        
        if len(name) > max_length:
            errors.append(f"{field_name} must be less than {max_length} characters")
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            errors.append(f"{field_name} must contain only letters, spaces, hyphens, and apostrophes")
        
        return errors
    
    @staticmethod
    def validate_region_code(code: str) -> List[str]:
        """Validate region code format"""
        errors = []
        
        if not code or not code.strip():
            errors.append("Region code is required")
            return errors
        
        code = code.strip().upper()
        
        if len(code) != 2:
            errors.append("Region code must be exactly 2 characters")
        
        if not code.isalpha():
            errors.append("Region code must contain only letters")
        
        return errors
    
    @staticmethod
    def validate_text_content(text: str, field_name: str, min_length: int = 1, max_length: Optional[int] = None) -> List[str]:
        """Validate text content fields"""
        errors = []
        
        if not text or not text.strip():
            errors.append(f"{field_name} is required")
            return errors
        
        text = text.strip()
        
        if len(text) < min_length:
            errors.append(f"{field_name} must be at least {min_length} characters")
        
        if max_length and len(text) > max_length:
            errors.append(f"{field_name} must be less than {max_length} characters")
        
        return errors
    
    @staticmethod
    def validate_id_list(ids: List[int], field_name: str) -> List[str]:
        """Validate list of IDs"""
        errors = []
        
        if not isinstance(ids, list):
            errors.append(f"{field_name} must be a list")
            return errors
        
        for i, id_value in enumerate(ids):
            if not isinstance(id_value, int) or id_value <= 0:
                errors.append(f"{field_name}[{i}] must be a positive integer")
        
        return errors