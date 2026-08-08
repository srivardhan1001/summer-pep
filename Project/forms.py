from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp


class CitySearchForm(FlaskForm):
    
    city = StringField(
        'City',
        validators=[
            DataRequired(message='Please enter a city name.'),
            Length(min=2, max=100, message='City name must be between 2 and 100 characters.'),
            Regexp(
                r'^[A-Za-z\s\-\',\.]+$',
                message='City name may only contain letters, spaces, hyphens, apostrophes, commas, and periods.'
            ),
        ],
        render_kw={
            'placeholder': 'Enter city name (e.g. London, Tokyo, Paris)...',
            'autocomplete': 'off',
            'class': 'form-control border-0 bg-transparent fs-5 text-body hero-input',
            'id': 'heroSearchInput',
        }
    )
    submit = SubmitField(
        'Search',
        render_kw={'class': 'btn btn-primary btn-lg rounded-pill px-4 shadow-sm fw-bold'}
    )


class AddFavoriteForm(FlaskForm):
    
    city = HiddenField(
        'City',
        validators=[
            DataRequired(message='City is required.'),
            Length(max=100),
        ]
    )
    country = HiddenField(
        'Country',
        validators=[Length(max=10)]
    )
    submit = SubmitField(
        'Add to Favorites',
        render_kw={'class': 'btn btn-warning btn-sm rounded-pill px-3 fw-semibold'}
    )


class ClearHistoryForm(FlaskForm):
    
    submit = SubmitField(
        'Clear All History',
        render_kw={
            'class': 'btn btn-outline-danger rounded-pill btn-sm px-3',
            'id': 'clearHistoryBtn',
        }
    )


class DeleteHistoryItemForm(FlaskForm):
    
    pass
