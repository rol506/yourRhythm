from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, HiddenField, PasswordField, RadioField, StringField, SubmitField, TextAreaField, TimeField, validators
from wtforms.validators import DataRequired, Email, EqualTo, Length

class User:
    def __init__(self, user_id: str):
        self._user_id: str = str(user_id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self) -> str:
        return self._user_id

class RegisterForm(FlaskForm):
    name = StringField("ФИО", validators=[DataRequired()])
    email = StringField("Электронная почта", validators=[Email()])
    pwd = PasswordField("Пароль", validators=[DataRequired(), Length(min=4)])
    pwdRepeat = PasswordField("Повторите пароль", validators=[EqualTo('pwd')])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Зарегистрироваться")

class LoginForm(FlaskForm):
    email = StringField("Электронная почта", validators=[Email()])
    pwd = PasswordField("Пароль", validators=[DataRequired(), Length(min=4)])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")

class AddTaskForm(FlaskForm):
    task = TextAreaField("Опишите задание:", validators=[DataRequired()])
    priority = RadioField("Приоритет:", choices=[('0', 'Низкий'), ('1','Средний'), ('2','Высокий')])
    deadlineDate = DateField("Укажите дедлайн:", validators=[DataRequired()])
    deadlineTime = TimeField("", validators=[DataRequired()])
    submit = SubmitField("Добавить задание")

class AddTaskAIForm(FlaskForm):
    task = TextAreaField("Опишите задание:", render_kw={"placeholder": "Например: В среду нужно вынести мусор."}, validators=[DataRequired()])
    priority = RadioField("Приоритет:", choices=[('0', 'Низкий'), ('1','Средний'), ('2','Высокий')])
    submit = SubmitField("Добавить задания")

class AddTaskForChild(FlaskForm):
    task = TextAreaField("Опишите задание:", validators=[DataRequired()])
    priority = RadioField("Приоритет:", choices=[('0', 'Низкий'), ('1','Средний'), ('2','Высокий')])
    deadlineDate = DateField("Укажите дедлайн:", validators=[DataRequired()])
    deadlineTime = TimeField("", validators=[DataRequired()])
    id = HiddenField("userID", render_kw={"id": "hidden"}, validators=[DataRequired()])
    submit = SubmitField("Добавить задание")

class AddTaskForChildAI(FlaskForm):
    task = TextAreaField("Опишите задание:", render_kw={"placeholder": "Например: В среду нужно вынести мусор."}, validators=[DataRequired()])
    priority = RadioField("Приоритет:", choices=[('0', 'Низкий'), ('1','Средний'), ('2','Высокий')])
    id = HiddenField("userID", render_kw={"id": "hiddenAI"}, validators=[DataRequired()])
    submit = SubmitField("Добавить задания")

