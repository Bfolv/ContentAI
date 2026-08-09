from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def buscar_videos(self, nicho, quantidade):
        pass