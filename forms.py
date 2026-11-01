from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime, timedelta

class TaskForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(message="Название не может быть пустым")])
    description = TextAreaField('Описание')
    deadline = DateTimeLocalField('Дедлайн', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    priority = SelectField('Приоритет', choices=[
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий')
    ], default='medium')
    submit = SubmitField('Сохранить')
    def validate_deadline(self, field):
        if field.data < datetime.now() - timedelta(minutes=1):
            raise ValidationError('Дедлайн не может быть в прошлом')