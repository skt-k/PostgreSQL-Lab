from flask import Flask, render_template, redirect, url_for, request
from models import db, Note, Tag
from forms import NoteForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

# Initialize the app with the db
db.init_app(app)


@app.route("/")
def index():
    notes = db.session.execute(
        db.select(Note).order_by(Note.title)
    ).scalars()
    return render_template("index.html", notes=notes)


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return render_template("notes-create.html", form=form)

    note = Note()
    form.populate_obj(note)
    note.tags = []

    for tag_name in form.tags.data:
        if isinstance(tag_name, Tag):
            note.tags.append(tag_name)
        elif isinstance(tag_name, str):  
            tag_obj = Tag.query.filter_by(name=tag_name).first()
            if tag_obj:
                note.tags.append(tag_obj)
            else:
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                note.tags.append(new_tag)

    db.session.add(note)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    notes = Note.query.filter(Note.tags.any(id=tag.id)).all()
    return render_template("tags-view.html", tag_name=tag_name, notes=notes)


@app.route("/note/<int:id>/edit", methods=["GET", "POST"])
def notes_edit(id):
    note = Note.query.get_or_404(id)
    form = NoteForm(obj=note)

    if form.validate_on_submit():
        form.populate_obj(note)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('notes-edit.html', form=form, note=note)


@app.route("/note/<int:id>/delete", methods=["POST"])
def notes_delete(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/tag/<int:id>/edit", methods=["GET", "POST"])
def tags_edit(id):
    tag = Tag.query.get_or_404(id)
    if request.method == 'POST':
        tag.name = request.form['name']
        db.session.commit()
        return redirect(url_for('tags_view', tag_name=tag.name))

    return render_template('tags-edit.html', tag=tag)


@app.route("/tag/<int:id>/delete", methods=["POST"])
def tags_delete(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
