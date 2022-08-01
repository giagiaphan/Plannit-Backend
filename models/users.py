# mongo-engine packages
from mongoengine import (Document,
                         EmbeddedDocument,
                         EmbeddedDocumentField,
                         ListField,
                         StringField,
                         EmailField,
                         BooleanField,
                         ReferenceField,
                         IntField,
                         FloatField)

# flask packages
from flask_bcrypt import generate_password_hash, check_password_hash

# project resources
from models.plans import Plans

# external packages
import re


class Access(EmbeddedDocument):
    """
    Custom EmbeddedDocument to set user authorizations.
    :param user: boolean value to signify if user is a user
    :param admin: boolean value to signify if user is an admin
    """
    user = BooleanField(default=True)
    admin = BooleanField(default=False)


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


class Users(Document):


    #user general data
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=6, regex=None)
    access = EmbeddedDocumentField(Access, default=Access(user=True, admin=False))
    saved_plans = ListField(ReferenceField(Plans))
    username = StringField(unique=False)
    phone = PhoneField(required=True)

    #user review/rating data
    review_count = IntField()
    planning_since = StringField()
    userful = IntField()
    funny = IntField()
    cool = IntField()
    friends = ListField(StringField())
    followers = IntField()
    average_stars = FloatField()
    compliment_hot = IntField()
    compliment_more = IntField()
    compliment_profile = IntField()
    compliment_cute = IntField()
    compliment_list = IntField()
    compliment_note = IntField()
    compliment_plain = IntField()
    compliment_cool = IntField()
    compliment_funny = IntField()
    compliment_writer = IntField()
    compliment_photos = IntField()


    def generate_pw_hash(self):
        self.password = generate_password_hash(password=self.password).decode('utf-8')
    # Use documentation from BCrypt for password hashing
    generate_pw_hash.__doc__ = generate_password_hash.__doc__

    def check_pw_hash(self, password: str) -> bool:
        return check_password_hash(pw_hash=self.password, password=password)
    # Use documentation from BCrypt for password hashing
    check_pw_hash.__doc__ = check_password_hash.__doc__

    def save(self, *args, **kwargs):
        # Overwrite Document save method to generate password hash prior to saving
        self.generate_pw_hash()
        super(Users, self).save(*args, **kwargs)