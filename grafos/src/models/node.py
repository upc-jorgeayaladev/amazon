from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class NodeType(Enum):
    SHELF = "shelf"
    ZONE = "zone"
    DOCK = "dock"
    PICKING_STATION = "picking_station"
    CROSS_DOCK = "cross_dock"

@dataclass
class Node:
    id: str
    type: NodeType
    x: float
    y: float
    capacity: int = 0
    current_load: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def can_store(self, quantity: int = 1) -> bool:
        return self.current_load + quantity <= self.capacity
    
    def add_load(self, quantity: int = 1) -> bool:
        if self.can_store(quantity):
            self.current_load += quantity
            return True
        return False
    
    def remove_load(self, quantity: int = 1) -> bool:
        if self.current_load >= quantity:
            self.current_load -= quantity
            return True
        return False
    
    def __repr__(self):
        return f"Node({self.id}, {self.type.value}, pos=({self.x},{self.y}))"
