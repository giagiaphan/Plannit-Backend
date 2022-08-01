# mongo-engine packages
from mongoengine import (Document, 
                        StringField, 
                        FloatField, 
                        IntField, 
                        EmbeddedDocumentField, 
                        ListField)

from models.resources import Resources

class Plans(Document):
    #plan general data
    user_id = StringField()
    plan_id = StringField()
    plan_name = StringField(required=True)
    duration = StringField()
    pricey = IntField()
    resources_used = ListField(EmbeddedDocumentField(Resources))