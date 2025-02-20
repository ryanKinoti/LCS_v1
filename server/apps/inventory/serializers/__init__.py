from .base import (
    DeviceMinimalSerializer,
    DevicePartMinimalSerializer
)
from .detailed import (
    DeviceDetailSerializer,
    DevicePartDetailSerializer,
    DeviceCreateSerializer,
    DevicePartCreateSerializer,
    PartMovementCreateSerializer,
    DeviceRepairHistoryCreateSerializer,
    DeviceRepairHistoryDetailSerializer
)

__all__ = [
    'DeviceMinimalSerializer',
    'DevicePartMinimalSerializer',

    'DeviceCreateSerializer',
    'DevicePartCreateSerializer',
    'PartMovementCreateSerializer',
    'DeviceRepairHistoryCreateSerializer',

    'DeviceDetailSerializer',
    'DevicePartDetailSerializer',
    'DeviceRepairHistoryDetailSerializer'
]
