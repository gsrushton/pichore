
from .. import core

import flask
import io
import os
import PIL.Image
import peewee

api = flask.Blueprint("api", __name__)

def select_people():
    model = flask.g.model

    default_appearances = (model.Appearance.select(model.Appearance.id,
                                                   model.Appearance.person_id,
                                                   peewee.fn.MAX(model.Appearance.weight))
                                           .group_by(model.Appearance.person)
                                           .alias("appearance"))

    return (model.Person.select(model.Person.id,
                                model.Person.first_name.alias("firstName"),
                                model.Person.middle_names.alias("middleNames"),
                                model.Person.surname,
                                model.Person.display_name.alias("displayName"),
                                default_appearances.c.id.alias("defaultAppearanceId"))
                        .join(default_appearances,
                              on=(model.Person.id == default_appearances.c.person_id)))

@api.route("/people")
def people():
    model = flask.g.model
    return flask.jsonify([person for person in select_people().dicts()])

@api.route("/people/<int:id>", methods=["GET", "POST"])
def person(id):
    model = flask.g.model

    if flask.request.method == 'POST':
        person = flask.request.json

        (model.Person.update(first_name=person["firstName"],
                            middle_names=person["middleNames"],
                            surname=person["surname"],
                            display_name=person["displayName"])
                     .where(model.Person.id == id)
                     .execute())

        return ("", 200)
    else:
        return flask.jsonify(select_people().where(model.Person.id == id)
                                            .dicts()
                                            .first())

@api.route("/people/<int:id>/appearances")
def persons_appearances(id):
    model = flask.g.model
    return flask.jsonify([appearance.id
                            for appearance in model.Appearance
                                                   .select()
                                                   .where(model.Appearance.person == id)])

@api.route("/appearances/<int:id>")
def appearance(id):
    model = flask.g.model
    appearance = model.Appearance.get(model.Appearance.id == id)
    return flask.jsonify(appearance.to_dict())

@api.route("/appearances/<int:id>/image")
def appearance_image(id):
    model = flask.g.model
    appearance = model.Appearance.get(model.Appearance.id == id)

    img_file_path = os.path.join(flask.g.src_dir_path,
                                 appearance.picture.file_path)

    image = PIL.Image.open(img_file_path)

    half_width = (appearance.right - appearance.left) // 2
    height = appearance.bottom - appearance.top

    left = max(appearance.left - half_width, 0)
    top = max(appearance.top - ((height * 3) // 4), 0)
    right = min(appearance.right + half_width, image.width - 1)
    bottom = min(appearance.bottom + (height // 4), image.height - 1)

    width = right - left
    height = bottom - top

    if width < height:
        diff = height - width
        half_diff = diff // 2
        top += half_diff
        bottom = bottom - diff + half_diff
    elif height < width:
        diff = width - height
        half_diff = diff // 2
        left += half_diff
        right = right - diff + half_diff

    image = image.crop((left, top, right, bottom))
    image = image.resize((96, 96), resample=PIL.Image.LANCZOS)

    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        data = output.getvalue()

    return flask.send_file(io.BytesIO(data), mimetype="image/jpeg")

@api.route("/pictures/count-per-day")
def picture_count_per_day():
    model = flask.g.model

    rows = (model.Picture.select(model.Picture.day,
                                 peewee.fn.COUNT(model.Picture.id).alias("count"))
                         .group_by(model.Picture.day))

    return flask.jsonify({row.day: row.count for row in rows})

@api.route("/pictures/for-day/<int:day>")
def picture_for_day(day):
    model = flask.g.model
    return flask.jsonify(list(model.Picture.select(model.Picture.id)
                                           .where(model.Picture.day == day)
                                           .dicts()))

@api.route("/pictures/<int:id>")
def picture(id):
    model = flask.g.model
    picture = model.Picture.get(model.Picture.id == id)
    return flask.send_file(os.path.join(flask.g.src_dir_path, picture.file_path))
