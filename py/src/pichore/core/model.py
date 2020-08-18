
import collections
import peewee

Model = collections.namedtuple("Model", ["Person", "Picture", "Appearance"])

def create(db):
    class Table(peewee.Model):
        class Meta:
            database = db

    class Person(Table):
        first_name = peewee.TextField()
        middle_names = peewee.TextField()
        surname = peewee.TextField()
        display_name = peewee.TextField(null=True)

    class Picture(Table):
        digest = peewee.BlobField(unique=True)
        camera_make = peewee.TextField(null=True)
        camera_model = peewee.TextField(null=True)
        latitude = peewee.DoubleField(null=True)
        longitude = peewee.DoubleField(null=True)
        date = peewee.FloatField()
        day = peewee.IntegerField()
        file_path = peewee.TextField()

    class Appearance(Table):
        person = peewee.ForeignKeyField(Person)
        picture = peewee.ForeignKeyField(Picture)
        top = peewee.IntegerField()
        left = peewee.IntegerField()
        bottom = peewee.IntegerField()
        right = peewee.IntegerField()
        face_encoding = peewee.BlobField(unique=True)
        weight = peewee.IntegerField()

        def to_dict(self):
            return {
                "person": self.person.id,
                "picture": self.picture.id,
                "top": self.top,
                "left": self.left,
                "bottom": self.bottom,
                "right": self.right
            }

    with db:
        db.create_tables([Person, Picture, Appearance])

    return Model(Person=Person,
                 Picture=Picture,
                 Appearance=Appearance)
