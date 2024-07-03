# An edge between two nodes with typical graph-theoretic attributes,
# but we're adding semantics depending on org. ecosystems

from entity import Entity


class Link(Entity):
    # assume the edge is undirected (most common in org. networks):
    def __init__(self, link_id, label, directed=False, weight=1, **kwargs):
        super().__init__(link_id, label, **kwargs)
        self.__directed = directed
        self.__weight = weight

    @property
    def directed(self):
        return self.__directed

    @directed.setter
    def directed(self, is_directed):
        self.__directed = is_directed

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, edge_weight):
        self.__weight = edge_weight
        