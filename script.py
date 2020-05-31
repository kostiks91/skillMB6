from bottle import route, run, template, HTTPError
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from bottle import request
from datetime import datetime

DB_PATH = "sqlite:///albums.sqlite3"
Base = declarative_base()


class Album(Base):
    __tablename__ = "album"
    id = sa.Column(sa.INTEGER, primary_key=True)
    year = sa.Column(sa.INTEGER)
    artist = sa.Column(sa.TEXT)
    genre = sa.Column(sa.TEXT)
    album = sa.Column(sa.TEXT)


def connect_db():
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()


def find(artist):
    session = connect_db()
    albums = session.query(Album).filter(Album.artist == artist).all()
    return albums


@route("/albums/<artist>")
def albums(artist):
    albums_list = find(artist)
    if not albums_list:
        message = "Альбомов {} не найдено".format(artist)
        result = HTTPError(404, message)
    else:
        album_names = [album.album for album in albums_list]
        result = "Список альбомов {}, Количетсво альбомов {} \n".format(artist, len(album_names))
        result += "\n".join(album_names)
    return result


def save(user_data):
    session = connect_db()
    savealbum = Album(year=user_data.get("year"), artist=user_data.get("artist"), genre=user_data.get("genre"),
                      album=user_data.get("album"))
    session.add(savealbum)
    session.commit()
    return True


@route('/albums')
def albums():
    return '''
        <form action="/albums" method="post">
            year: <input name="year" type="text" />
            Artist <input name="artist" type="text" />
            genre <input name="genre" type="text" />
            album <input name="album" type="text" />
            <input value="Go" type="submit" />
        </form>
    '''


@route("/albums", method="POST")
def user():
    user_data = {
        "artist": request.forms.get("artist"),
        "genre": request.forms.get("genre"),
        "album": request.forms.get("album")
    }
    try:
        if int(request.forms.get("year")) >1900 and int(request.forms.get("year")) <= datetime.now().year:
            user_data.update({"year": request.forms.get("year")})
        else:
            return 'неправильная дата {}'.format(request.forms.get('year'))
    except ValueError:
        return 'Неправильный тип даты, укажи число'
    albums_list = find(request.forms.get("artist"))
    album_names = [album.album for album in albums_list]
    print(album_names)
    if not albums_list:
        pass
    else:
        if request.forms.get("album") in album_names:
            return HTTPError(409, "Такой альбом уже существует!")
    save(user_data)
    return "Данные успешно сохранены"


if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)
