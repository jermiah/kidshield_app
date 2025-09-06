"""Schémas simplifiés pour l'API Guardian Layer"""

from typing import Optional
from pydantic import BaseModel, Field

class ContentRequest(BaseModel):
    """Schéma de requête simplifié pour l'analyse de contenu"""
    content: str = Field(..., description="Contenu à analyser (texte ou image base64)")
    content_type: str = Field(..., description="Type de contenu: 'text' ou 'image'")
    user_id: Optional[str] = Field(None, description="Identifiant utilisateur optionnel")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello, how are you?",
                "content_type": "text",
                "user_id": "user123"
            }
        }

class SimpleRequest(BaseModel):
    """Schéma encore plus simple avec détection automatique"""
    content: str = Field(..., description="Contenu à analyser")
    user_id: Optional[str] = Field(None, description="Identifiant utilisateur optionnel")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello, how are you?",
                "user_id": "user123"
            }
        }
