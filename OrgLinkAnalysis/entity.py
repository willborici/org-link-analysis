# Superclass for nodes and links:

class Entity:
    used_ids = {}  # quality check to ensure unique IDs

    @classmethod
    def ensure_unique_id(cls, entity_type, entity_id):
        if entity_type not in cls.used_ids:
            cls.used_ids[entity_type] = set()  # type = node or link

        if entity_id in cls.used_ids[entity_type]:
            suggested_id = max(cls.used_ids[entity_type]) + 1
            prompt = input(f"{entity_type.capitalize()} ID '{entity_id}' already exists. "
                           f"Accept suggested {entity_type} ID '{suggested_id}' (y/n)? ")
            if prompt.lower() == 'y':
                entity_id = suggested_id
            else:
                raise ValueError(f"Retry with a valid and unique {entity_type} ID")

        cls.used_ids[entity_type].add(entity_id)

        return entity_id

    # at min., we need an ID and a label, but allow for other attributes
    # depending on organizational needs (**kwargs)
    def __init__(self, entity_id, label, **kwargs):
        self.__entity_id = self.ensure_unique_id(self.__class__.__name__.lower(), entity_id)
        self.__label = label
        self.__attributes = kwargs

    @property
    def entity_id(self):
        return self.__entity_id

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
