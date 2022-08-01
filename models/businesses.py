# mongo-engine packages
from mongoengine import (Document, 
                        StringField, 
                        FloatField, 
                        IntField, 
                        ListField, 
                        EmbeddedDocumentField, 
                        EmbeddedDocument)

from models.reviews import Reviews

class PhoneField(StringField):
    """
    Custom StringField to verify Phone numbers.
    # Modification of http://regexlib.com/REDetails.aspx?regexp_id=61
    #
    # US Phone number that accept a dot, a space, a dash, a forward slash, between the numbers.
    # Will Accept a 1 or 0 in front. Area Code not necessary
    """
    REGEX = re.compile(r"((\(\d{3}\)?)|(\d{3}))([-\s./]?)(\d{3})([-\s./]?)(\d{4})")

    def validate(self, value):
        # Overwrite StringField validate method to include regex phone number check.
        if not PhoneField.REGEX.match(string=value):
            self.error(f"ERROR: `{value}` Is An Invalid Phone Number.")
        super(PhoneField, self).validate(value=value)

class Business(Document):
    #business general data
    #business_id = StringField()
    business_name = StringField(required=True)
    descripition = StringField()
    categories = ListField(StringField())
    phone = PhoneField()
    #hours
    
    #business location data
    address = FloatField(required=True)
    city = StringField(required=True)
    state = StringField()
    postal_code = StringField(required=True)
    country = StringField()
    latitude = FloatField(required=True)
    longtitude = FloatField(required=True)
    
    #business metadata
    is_open = IntField()
    #attributes = 
    tags = ListField(StringField())
    
    #business rating & review data
    stars = FloatField()
    review_count = IntField()
    reviews = ListField(EmbeddedDocumentField(Reviews))

class attributes(EmbeddedDocument):


class Hour(EmbeddedDocument):


