# mongo-engine packages
from mongoengine import Document, StringField, ListField, ReferenceField

from models.users import Users

class Post(Document):
    title = StringField(max_length=120, required=True)
    author = ReferenceField(Users, reverse_delete_rule=CASCADE)
    tags = ListField(StringField(max_length=30))
    meta = {'allow_inheritance': True}

class TextPost(Post):
    content = StringField()

class ImagePost(Post):
    image_path = StringField()

class LinkPost(Post):
    link_url = StringField()