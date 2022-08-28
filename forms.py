from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, URL, Length, Optional, InputRequired, Regexp
import re


# Constant Variables
#  ----------------------------------------------------------------

genre_options = [
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Swing', 'Swing'),
            ('Other', 'Other'),
        ]

state_options = [
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]

# Shows Form
#  ----------------------------------------------------------------

class ShowForm(Form):
    artist_id = StringField(
        'artist_id', validators=[InputRequired()],
    )
    venue_id = StringField(
        'venue_id', validators=[InputRequired()],
    )
    start_time = DateTimeField(
        'start_time',
        validators=[InputRequired()],
        default= datetime.today()
    )

# Venues Form
#  ----------------------------------------------------------------

class VenueForm(Form):
    name = StringField(
        'name', validators=[InputRequired()]
    )
    city = StringField(
        'city', validators=[InputRequired(), Length(max=50)]
    )
    state = SelectField(
        'state', validators=[InputRequired(), Length(max=50)],
        choices = state_options
    )
    address = StringField(
        'address', validators=[InputRequired(), Length(max=150)]
    )
    phone = StringField(
        'phone', validators=[InputRequired(), Regexp(regex=r"^\d{4}[-]{1}\d{3}[-]{1}\d{4}$",
        message="Valid phone number format is xxxx-xxx-xxxx")]
    )
    image_link = StringField(
        'image_link', validators=[InputRequired(), URL()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[InputRequired()],
        choices = genre_options
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Length(max=500), Optional()]
    )
    website_link = StringField(
        'website_link', validators=[URL(), Length(max=500), Optional()]
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = TextAreaField(
        'seeking_description', validators=[InputRequired(), Length(max=500)]
    )

    # # Custom validation funtions
    # def validate_phone(form, field):
    #     if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data):
    #         raise ValidationError("Invalid phone number.")

# Artists Form
#  ----------------------------------------------------------------

class ArtistForm(Form):
    name = StringField(
        'name', validators=[InputRequired()]
    )
    city = StringField(
        'city', validators=[InputRequired(), Length(max=50)]
    )
    state = SelectField(
        'state', validators=[InputRequired(), Length(max=50)],
        choices = state_options 
    )
    phone = StringField( 
        'phone', validators=[InputRequired(), Regexp(regex=r"^\d{4}[-]{1}\d{3}[-]{1}\d{4}$",
        message="Valid phone number format is xxxx-xxx-xxxx")]
    )
    image_link = StringField(
        'image_link', validators=[URL(), DataRequired()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices = genre_options
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL(), Length(max=500), Optional()]
     )

    website_link = StringField(
        'website_link', validators=[URL(), Length(max=500), Optional()]
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = TextAreaField(
            'seeking_description', validators=[Optional(), Length(max=500)]
     )

    # Custom validation funtions
    def validate_phone(form, field):
        if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data):
            raise ValidationError("Invalid phone number.")
