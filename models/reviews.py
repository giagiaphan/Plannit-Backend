from mongoengine import EmbeddedDocument, StringField, IntField

class Reviews(EmbeddedDocument):
    #review general data
    review_id = StringField()
    user_id = StringField()
    business_id = StringField()

    #review rating data
    stars = IntField()
    userful = IntField()
    funny = IntField()
    cool = IntField()
    review_content = StringField()
    date = StringField()