from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from wtforms import Field, widgets
import models

class TagListField(Field):
    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.data = []

    def process_formdata(self, valuelist):
        data = []
        if valuelist:
            data = [x.strip() for x in valuelist[0].split(",")]

            if not isinstance(self.data, list):
                self.data = []

            for tag_name in data:
                tag = models.Tag.query.filter_by(name=tag_name).first()
                if tag and tag not in self.data:
                    self.data.append(tag)
                elif not tag:
                    new_tag = models.Tag(name=tag_name)
                    models.db.session.add(new_tag)
                    self.data.append(new_tag)

    def _value(self):
        if self.data:
            return ", ".join([tag.name for tag in self.data])
        else:
            return ""


BaseNoteForm = model_form(
    models.Note, base_class=FlaskForm, exclude=["created_date", "updated_date"], db_session=models.db.session
)

class NoteForm(BaseNoteForm):
    tags = TagListField("Tag")
