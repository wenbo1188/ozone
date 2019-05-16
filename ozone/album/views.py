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


@album_page.route('/upload_photo/<string:title>', methods=['GET', 'POST'])
def upload_photo(title="null"):
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    from .. import photos
        
    form = UploadForm()

    if form.validate_on_submit():
        photo_infos = []
        for filename in request.files.getlist('file'):
            timestamp = int(time.time())
            photo_name = photos.save(filename)
            logger.debug("file name: {}".format(photo_name))
            photo_url = photos.url(photo_name)
            logger.debug("file url: {}".format(photo_url))
            md5_value = md5()
            md5_value.update(bytes(photo_name, 'utf-8'))
            md5_value.update(bytes(str(timestamp), 'utf-8'))
            photo_id = md5_value.hexdigest()
            logger.debug("md5: {}".format(photo_id))
            photo_infos.append(dict(id=photo_id, name=photo_name, timestamp=timestamp))

        with app.app_context():
            db = get_db()

            # Check if the album exists
            try:
                cur = db.cursor().execute("select * from album where title = ?", [title,])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)

            if title == "null" or cur.fetchone() is None:
                for photo_info in photo_infos:
                    try:
                        db.cursor().execute("insert into photo (id, name, album, timestamp) values (?, ?, null, ?)", [photo_info["id"], photo_info["name"], photo_info["timestamp"]])
                    except sqlite3.DatabaseError as err:
                        logger.error("Invalid database operation:{}".format(err))
                        abort(404)
                db.commit()
            else:
                for photo_info in photo_infos:
                    try:
                        db.cursor().execute("insert into photo (id, name, album, timestamp) values (?, ?, ?, ?)", [photo_info["id"], photo_info["name"], title, photo_info["timestamp"]])
                    except sqlite3.DatabaseError as err:
                        logger.error("Invalid database operation:{}".format(err))
                        abort(404)
                db.commit()

            logger.info("Success add {} photo to {} album".format(len(photo_infos), title))
            flash("You have successfully uploaded photo", "success")

    return render_template("photo_upload.html", form=form, title=title)


@album_page.route('/delete_photo/<string:photo_id>', methods=['GET'])
def delete_photo(photo_id):
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    from .. import photos

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
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    from .. import photos
    
    with app.app_context():
        db = get_db()

        # For displaymode all
        try:
            cur = db.cursor().execute("select distinct id, name from photo")
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
        photo_infos_all = [dict(id = row["id"], name=row["name"], url=photos.url(row["name"])) for row in cur.fetchall()]
        
        # For displaymode album
        try:
            cur = db.cursor().execute("select distinct title from album")
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
        album_titles = [row["title"] for row in cur.fetchall()]
        logger.debug("titles: {}".format(album_titles))
        photo_infos_album = []
        for title in album_titles:
            try:
                cur = db.cursor().execute("select distinct name from photo where album = ?", [title,])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            album_photos = [dict(name=row["name"], url=photos.url(row["name"])) for row in cur.fetchall()]
            photo_infos_album.append(dict(title=title, photo_infos=album_photos))

        logger.info("photo_infos:\n{}".format(photo_infos_album))
        
    return render_template("show_photo.html", photo_infos_all=photo_infos_all, photo_infos_album=photo_infos_album)


@album_page.route('/add_album', methods=['GET', 'POST'])
def add_album():
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    form = AlbumForm()

    if form.validate_on_submit():
        timestamp = int(time.time())
        title = form.title.data
        md5_value = md5()
        md5_value.update(bytes(title, 'utf-8'))
        md5_value.update(bytes(str(timestamp), 'utf-8'))
        album_id = md5_value.hexdigest()
        about = form.about.data
        if about is None:
            about = "NULL"
        with app.app_context():
            db = get_db()
            try:
                db.cursor().execute("insert into album (id, title, about, timestamp) values (?, ?, ?, ?)", [album_id, title, about, timestamp])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            db.commit()

        logger.info("Success add an album: {} {} {} {}".format(album_id, title, about, timestamp))
        flash("You have successfully add an album", "success")
        return redirect(url_for("main.manage", function="album"))
    else:
        return render_template("add_album.html", form=form)


@album_page.route('/delete_album/<string:album_id>')
def delete_album(album_id):
    # check if login
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    # unlink photos with album and then delete album
    with app.app_context():
        db = get_db()
        try:
            db.cursor().execute("update photo set album = ? where album = ?", ["NULL", album_id])
            db.cursor().execute("delete from album where id = ?", [album_id,])
            db.commit()
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)

        logger.info("Success delete an album: {}".format(album_id))
        
    flash("You have successfully deleted an album", "success")
    return redirect((url_for('main.manage', function="album")))


@album_page.route('/update_album')
def update_album():
    pass


@album_page.route('/add_photo_to_album/<string:photo_id>', methods=['POST'])
def add_photo_to_album(photo_id):
    # Check if login
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    album_title = request.form["album_title"]

    with app.app_context():
        # Check if photo_id and album_id exist
        db = get_db()
        try:
            res1 = db.cursor().execute("select * from album where title = ?", [album_title,])
            res2 = db.cursor().execute("select * from photo where id = ?", [photo_id,])
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
            
        if res1.fetchone() is not None and res2.fetchone() is not None:
            try:
                db.cursor().execute("update photo set album = ? where id = ?", [album_title, photo_id])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            db.commit()
            
            logger.info("You have success add photo {} to {}".format(photo_id, album_title))
            flash("You have success add photo to album", "success")
            return redirect(url_for("main.manage", function="album"))
        else:
            logger.warning("No photo or album found specified by request")
            flash("No such photo or album found", "danger")
            return redirect(url_for("album.show_photo"))


@album_page.route('/add_photo_to_exhibition/<string:photo_id>')
def add_photo_to_exhibition(photo_id):
    # Check if login
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    with app.app_context():
        db = get_db()
        # Check if photo already in exhibition
        if db.cursor().execute("select exhibition from photo where id = ?", [photo_id,]).fetchone()[0] == 1:
            flash("This photo is already in exhibition!", "warning")
            return redirect(url_for("album.show_photo"))
        else:
            exhibition_num = 4
            timestamp = int(time.time())
            try:
                old_exhibition_num = db.cursor().execute("select count(*) from photo where exhibition = 1").fetchone()[0]
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            logger.debug("old_exhibition_num: {}".format(old_exhibition_num))
            if old_exhibition_num < exhibition_num:
                # Update exhibition by photo_id
                try:
                    db.cursor().execute("update photo set exhibition = 1, last_chosen_time = ? where id = ?", [timestamp, photo_id])
                except sqlite3.DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
            else:
                # replace the eldest exhibition and set a new one
                try:
                    db.cursor().execute("update photo set exhibition = 0, last_chosen_time = 0 where exhibition = 1 and last_chosen_time = (select min(last_chosen_time) from photo where last_chosen_time > 0)")
                    db.cursor().execute("update photo set exhibition = 1, last_chosen_time = ? where id = ?", [timestamp, photo_id])
                except sqlite3.DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
            db.commit()

            flash("Successfully add photo to exhibition!", "success")
            return redirect(url_for("album.show_photo"))
