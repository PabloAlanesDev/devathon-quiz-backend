from mongoengine import StringField, Document


class Topic(Document):
    name = StringField(max_length=20, required=True, unique=True)
    description = StringField(max_length=200, required=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description
        }
