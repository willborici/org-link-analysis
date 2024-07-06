# Model a node entity with attributes customizable for
# diverse organizational ecosystems, hence the **kwargs
from entity import Entity


class Node(Entity):
    def __init__(self, label, **kwargs):
        super().__init__(label, **kwargs)
