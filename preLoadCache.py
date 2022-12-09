import sqlite3
import requests
import topPages
import zlib

connect_db = sqlite3.connect("web_cache.db")
db = connect_db.cursor()
db.execute("CREATE TABLE IF NOT EXISTS CACHE (Path TEXT, Data BLOB);")


def preload_cache(origin):

    for path in topPages.mostVisited[:200]:
        # # check if path starts with forward slash
        # if len(path) > 0 and path[0] != "/":
        #     path = "/" + path

        db.execute("SELECT Data FROM Cache WHERE Path = :Path", {"Path": path})
        path_or_none = db.fetchone()

        if path_or_none == None:
            print(f"inserting {path}")
            url = "http://" + origin + ":8080/" + path
            url_data = requests.get(url)
            zipped_data = zlib.compress(url_data.content)
            db.execute("INSERT INTO Cache(Path,Data) VALUES(?,?)", (path, zipped_data))
        else:
            print(f"skipping {path} because it already exists")

    # 19920000 20 MB
    # 14940000 15 MB


preload_cache("cs5700cdnorigin.ccs.neu.edu")

db.execute("SELECT Data FROM Cache WHERE Path = :Path", {"Path": "Main_Page"})
nextPath = db.fetchone()
print(zlib.decompress(nextPath[0]))

db.connection.commit()

db.close()
