from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class Product:
    id: str
    name: str
    sku: str
    weight: float
    volume: float
    category: str
    dimensions: Dict[str, float]
    demand_frequency: int = 0
    location_id: Optional[str] = None
    expiration_date: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def assign_location(self, node_id: str):
        self.location_id = node_id
    
    def __repr__(self):
        return f"Product({self.sku}: {self.name})"
