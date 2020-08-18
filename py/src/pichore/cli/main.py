
from .. import core

import argparse
import base64
import datetime
import face_recognition
import hashlib
import logging
import numpy
import os
import peewee
import PIL
import shutil
import time

log = logging.getLogger(__name__)

_IMAGE_FILE_EXTS = set([".jpg"])

def import_pictures(src_dir_path, dst_dir_path):
    db_file_path = os.path.join(dst_dir_path, "pichore.db")

    os.makedirs(os.path.join(dst_dir_path, "images"), exist_ok=True)

    db = peewee.SqliteDatabase(db_file_path)

    model = core.model.create(db)

    Person = model.Person
    Picture = model.Picture
    Appearance = model.Appearance

    known_faces = [(appearance.person.id, numpy.frombuffer(appearance.face_encoding, dtype=numpy.float64))
                      for appearance in Appearance.select().where(Appearance.weight > 0)]

    def process_face(pixels, encoding, location, picture):
        results = face_recognition.compare_faces([encoding for _, encoding in known_faces], encoding, tolerance=0.4)

        matches = [id for match, (id, encoding) in zip(results, known_faces) if match]

        if len(matches) == 1:
            person_id = matches[0]
            appearance_weight = 0
            log.info("  face found with {}".format(person_id))
        else:
            # Create a new person
            person = Person.create(first_name="Awesome",
                                   middle_names="'Photo Bomber'",
                                   surname="McAwesome")
            person_id = person.id
            appearance_weight = 100

            known_faces.append((person_id, encoding))

            log.info("  no match")

        appearance = Appearance.create(person=person_id,
                                       picture=picture.id,
                                       top=location[0],
                                       left=location[3],
                                       bottom=location[2],
                                       right=location[1],
                                       face_encoding=encoding.tobytes(),
                                       weight=appearance_weight)

    def process_picture(src_file_path, ext):
        image = PIL.Image.open(src_file_path)
        pixels = numpy.array(image)

        hash = hashlib.sha256(pixels)
        digest = hash.digest()

        dst_file_stem = base64.urlsafe_b64encode(digest).decode("ascii")

        try:
            picture = Picture.get(Picture.digest == digest)

            log.info("'{}' already in database with hash {}".format(src_file_path, dst_file_stem))

        except Picture.DoesNotExist:
            log.info("'{}' not yet in database".format(src_file_path))

            dst_file_path = os.path.join("images", "{}{}".format(dst_file_stem, ext))

            shutil.copyfile(src_file_path, os.path.join(dst_dir_path, dst_file_path))

            date = None
            camera_make = None
            camera_model = None
            lat = None
            lon = None

            exif = image._getexif()
            if exif is not None:
                date = exif.get(0x9003, None)
                if date is None:
                    date = exif.get(0x0132, None)

                camera_make = exif.get(0x010F, None)
                camera_model = exif.get(0x0110, None)

                def get_decimal_from_dms(dms, ref):
                    degrees = dms[0][0] / dms[0][1]
                    minutes = dms[1][0] / dms[1][1] / 60.0
                    seconds = dms[2][0] / dms[2][1] / 3600.0

                    if ref in ['S', 'W']:
                        degrees = -degrees
                        minutes = -minutes
                        seconds = -seconds

                    return round(degrees + minutes + seconds, 5)

                gps = exif.get(0x8825, None)
                if gps is not None:
                    lat = get_decimal_from_dms(gps['GPSLatitude'],
                                               gps['GPSLatitudeRef'])
                    lon = get_decimal_from_dms(gps['GPSLongitude'],
                                               gps['GPSLongitudeRef'])

            if date is None:
                date = os.path.getmtime(src_file_path)
            else:
                date = datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S").timestamp()

            picture = Picture.create(digest=digest,
                                     file_path=dst_file_path,
                                     camera_make=camera_make,
                                     camera_model=camera_model,
                                     latitude=lat,
                                     longitude=lon,
                                     date=date,
                                     day=date // (60 * 60 * 24))

            face_locations = face_recognition.face_locations(pixels)
            if face_locations:
                log.info("'{}' contains {} face(s)".format(src_file_path, len(face_locations)))

                face_encodings = face_recognition.face_encodings(pixels, face_locations)
                for encoding, location in zip(face_encodings, face_locations):
                    process_face(pixels, encoding, location, picture)

    def process_dir(src_dir_path):
        for ent_basename in os.listdir(src_dir_path):
            ent_path = os.path.join(src_dir_path, ent_basename)
            if os.path.isdir(ent_path):
                process_dir(ent_path)
            elif os.path.isfile(ent_path):
                _, ext = os.path.splitext(ent_basename)
                if ext in _IMAGE_FILE_EXTS:
                    process_picture(ent_path, ext)

    process_dir(src_dir_path)

def main():
    cwd = os.getcwd()

    parser = argparse.ArgumentParser("Words")
    parser.add_argument("src_dir_path",
                        metavar="src-dir-path",
                        help="Path to the directory to walk looking for images")
    parser.add_argument("-d", "--dst-dir-path",
                        default=cwd,
                        help="Path to the directory to put the images")
    parser.add_argument("-v", "--verbose",
                        dest="verbose_count",
                        action="count",
                        default=0,
                        help="Increases log verbosity for each occurence.")

    args = parser.parse_args()

    logging.basicConfig(level=max(3 - args.verbose_count, 0) * 10)

    import_pictures(args.src_dir_path, args.dst_dir_path)
