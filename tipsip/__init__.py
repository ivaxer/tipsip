from statistics import Statistics
stats = Statistics()

from storage import MemoryStorage, RedisStorage
from presence import PresenceService, Status

presence_service = PresenceService(MemoryStorage())

