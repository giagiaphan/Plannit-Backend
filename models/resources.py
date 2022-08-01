from mongoengine import (EmbeddedDocument, 
                        StringField, 
                        BooleanField, 
                        IntField)


class Resources(EmbeddedDocument):
    business_id = StringField()
    resource_id = StringField()
    resource_name = StringField()
    quantity_available = IntField()
    quantity_not_available = IntField()
     
    available = BooleanField()
    about = StringField()