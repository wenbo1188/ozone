import sqlite3
import time
from hashlib import md5
import os

from jinja2 import TemplateNotFound

from flask import Blueprint, abort
from flask import current_app as app
from flask import flash, g, redirect, render_template, request, session, url_for

from . import album_page
from ..config import logger
from ..utils.db_util import get_db
from ..utils.form_util import AlbumForm, UploadForm

@album_page.route('/upload', methods=['GET', 'POST'])
def upload():
    from .. import photos
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))
        
    form = UploadForm()

    if form.validate_on_submit():
        photo_infos = []
        for filename in request.files.getlist('file'):
            photo_name = photos.save(filename)
            logger.debug("file name: {}".format(photo_name))
            photo_url = photos.url(photo_name)
            logger.debug("file url: {}".format(photo_url))
            md5_value = md5()
            md5_value.update(bytes(photo_name, 'utf-8'))
            photo_id = md5_value.hexdigest()
            logger.debug("md5: {}".format(photo_id))
            timestamp = int(time.time())
            photo_infos.append(dict(id=photo_id, name=photo_name, timestamp=timestamp))

        with app.app_context():
            db = get_db()

            for photo_info in photo_infos:
                try:
                    db.cursor().execute("insert into photo (id, name, album, timestamp) values (?, ?, null, ?)", [photo_info["id"], photo_info["name"], photo_info["timestamp"]])
                except sqlite3.DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
            db.commit()
            logger.info("Success add {} photo".format(len(photo_infos)))
            flash("You have successfully uploaded photo", "success")

    return render_template("photo_upload.html", form=form)

@album_page.route('/delete/<string:photo_id>', methods=['GET'])
def delete(photo_id):
    from .. import photos
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    with app.app_context():
        db = get_db()
        cur = db.cursor().execute("select name from photo where id = ?", [photo_id])
        file_name = cur.fetchone()[0]
        file_path = photos.path(file_name)
        logger.debug("delete file path: {}".format(file_path))
        try:
            db.cursor().execute("delete from photo where id = ?", [photo_id])
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)

        try:
            os.remove(file_path)
            db.commit()
            logger.info("Success delete photo")
        except:
            logger.error("Something goes wrong while deleting the file")
            abort(404)

        flash("You have successfully deleted a photo", "success")
        return redirect((url_for('main.manage', function="album")))
    
@album_page.route('/', methods=['GET'])
def show_photo():
    from .. import photos
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))
    
    with app.app_context():
        db = get_db()
        try:
            cur = db.cursor().execute("select distinct name from photo")
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
        photo_infos = [dict(name=row[0], url=photos.url(row[0])) for row in cur.fetchall()]
        logger.info("photo_infos:\n{}".format(photo_infos))
        
    return render_template("show_photo.html", photo_infos=photo_infos)