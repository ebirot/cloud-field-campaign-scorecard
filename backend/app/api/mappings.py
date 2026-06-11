"""
Mappings API
Manage Country→OU and Product→Cloud mappings for Email parser
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import json
from pathlib import Path

router = APIRouter()

# Paths to store mappings
MAPPINGS_DIR = Path(__file__).parent.parent.parent.parent / 'data' / 'mappings'
COUNTRY_MAPPING_FILE = MAPPINGS_DIR / 'country_to_ou.json'
PRODUCT_MAPPING_FILE = MAPPINGS_DIR / 'product_to_cloud.json'

# Ensure mappings directory exists
MAPPINGS_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/country")
async def get_country_mappings() -> Dict[str, str]:
    """Get current Country → OU mappings"""
    try:
        if COUNTRY_MAPPING_FILE.exists():
            with open(COUNTRY_MAPPING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return defaults from email_parser
            from app.services.email_parser import EmailParser
            return EmailParser.DEFAULT_COUNTRY_TO_OU
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading country mappings: {str(e)}")


@router.post("/country")
async def save_country_mappings(mappings: Dict[str, str]):
    """Save Country → OU mappings"""
    try:
        with open(COUNTRY_MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=2, ensure_ascii=False)

        return {
            "status": "success",
            "message": f"Saved {len(mappings)} country mappings",
            "count": len(mappings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving country mappings: {str(e)}")


@router.get("/product")
async def get_product_mappings() -> Dict[str, str]:
    """Get current Product → Cloud mappings"""
    try:
        if PRODUCT_MAPPING_FILE.exists():
            with open(PRODUCT_MAPPING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return defaults from email_parser
            from app.services.email_parser import EmailParser
            return EmailParser.DEFAULT_PRODUCT_TO_CLOUD
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading product mappings: {str(e)}")


@router.post("/product")
async def save_product_mappings(mappings: Dict[str, str]):
    """Save Product → Cloud mappings"""
    try:
        with open(PRODUCT_MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=2, ensure_ascii=False)

        return {
            "status": "success",
            "message": f"Saved {len(mappings)} product mappings",
            "count": len(mappings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving product mappings: {str(e)}")


@router.post("/reload")
async def reload_mappings():
    """Reload mappings in email parser (force refresh)"""
    try:
        from app.services.email_parser import email_parser

        # Reload mappings from files using the parser's own load methods
        email_parser.COUNTRY_TO_OU = email_parser._load_country_mappings()
        email_parser.PRODUCT_TO_CLOUD = email_parser._load_product_mappings()

        return {
            "status": "success",
            "message": "Mappings reloaded successfully",
            "country_count": len(email_parser.COUNTRY_TO_OU),
            "product_count": len(email_parser.PRODUCT_TO_CLOUD)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading mappings: {str(e)}")
