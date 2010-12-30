from storage import MemoryStorage, RedisStorage
from presence import PresenceService, Status
from statistics import Statistics

statistics = Statistics()
presence_service = PresenceService(MemoryStorage())

