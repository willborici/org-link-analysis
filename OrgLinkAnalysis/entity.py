# Superclass for nodes and links:

class Entity:

    # at min., we need a label, but allow for other named attributes
    # depending on organizational needs (**kwargs)
    def __init__(self, label, **kwargs):
        self.__label = label
        self.__attributes = kwargs

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, new_label):
        self.__label = new_label

    def set_attribute(self, key, value):
        self.__attributes[key] = value

    def get_attribute(self, key):
        return self.__attributes.get(key)
