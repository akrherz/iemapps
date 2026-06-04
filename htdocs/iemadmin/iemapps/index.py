"""
IEM management of iemapps database relation.

CREATE TABLE iemapps (
    appid serial UNIQUE,
    name text UNIQUE NOT NULL,
    description text,
    url text NOT NULL,
    category text NOT NULL DEFAULT '',
    subcategory text NOT NULL DEFAULT '',
    tags text [] NOT NULL DEFAULT '{}',
    importance int NOT NULL DEFAULT 0
);

"""

from paste.request import parse_formvars
from pyiem.database import sql_helper, with_sqlalchemy_conn
from sqlalchemy.engine import Connection

PAGE = """
<html><head><title>IEMAdmin | IEMApps Database Editor</title></head>
<body>

<p>Hello, %(user)s!</p>

<form name="sel" method="GET">
<strong>Select App:</strong>
<select name="appid">
%(appopts)s
</select>
<input type="submit" value="Select">
</form>

<form name="edit" method="POST">
<input type="hidden" name="appid" value="%(appid)s">
<input type="hidden" name="doedit" value="1">
<strong>App Name:</strong>
<input type="text" name="name" value="%(name)s">
<br>
<strong>App URL:</strong>
<input type="text" name="url" value="%(url)s">
<br>
<strong>App Description:</strong>
<textarea name="description" rows="5" cols="40">%(description)s</textarea>
<br>
<strong>App Category:</strong>
<input type="text" name="category" value="%(category)s">
<br>
<strong>App Subcategory:</strong>
<input type="text" name="subcategory" value="%(subcategory)s">
<br>
<strong>App Tags (comma separated):</strong>
<input type="text" name="tags" value="%(tags)s">
<br>
<strong>App Importance (higher is more important):</strong>
<input type="text" name="importance" value="%(importance)s">
<br>
<input type="submit" value="Submit">
</form>

"""


@with_sqlalchemy_conn("mesosite")
def generate_apps(conn: Connection | None = None) -> str:
    """Generate the options"""
    res = conn.execute(
        sql_helper("""
    select appid, name from iemapps ORDER by name ASC
                   """)
    )
    options = []
    for row in res.mappings():
        options.append(
            f'<option value="{row["appid"]}">'
            f"{row['appid']}. {row['name']}</option>"
        )
    return "\n".join(options)


@with_sqlalchemy_conn("mesosite")
def get_appopts(appid: str, conn: Connection | None = None) -> dict:
    """Get what the database offers."""
    appopts = {}
    res = conn.execute(
        sql_helper(
            """
    select * from iemapps where appid = :appid
    """
        ),
        {"appid": appid},
    )
    row = res.mappings().first()
    if row is not None:
        appopts = {
            "name": row["name"],
            "url": row["url"],
            "description": row["description"],
            "category": row["category"],
            "subcategory": row["subcategory"],
            "tags": ",".join(row["tags"]),
            "importance": row["importance"],
        }
    return appopts


@with_sqlalchemy_conn("mesosite")
def make_edit(form: dict, conn: Connection | None = None):
    """Edit the database entry."""
    appid = form.get("appid")
    if appid is None or appid == "":
        appid = -1
    appid = int(appid)
    name = form.get("name")
    url = form.get("url")
    description = form.get("description")
    category = form.get("category")
    subcategory = form.get("subcategory")
    tags = form.get("tags", "").split(",")
    importance = int(form.get("importance", "0"))
    if appid >= 0:
        conn.execute(
            sql_helper(
                """
        UPDATE iemapps
        SET name = :name, url = :url, description = :description,
        category = :category, subcategory = :subcategory, tags = :tags,
        importance = :importance WHERE appid = :appid
        """
            ),
            {
                "appid": appid,
                "name": name,
                "url": url,
                "description": description,
                "category": category,
                "subcategory": subcategory,
                "tags": tags,
                "importance": importance,
            },
        )
    else:
        conn.execute(
            sql_helper(
                """
        INSERT into iemapps (name, url, description, category, subcategory,
        tags, importance) VALUES (:name, :url, :description, :category,
        :subcategory, :tags, :importance)
        """
            ),
            {
                "name": name,
                "url": url,
                "description": description,
                "category": category,
                "subcategory": subcategory,
                "tags": tags,
                "importance": importance,
            },
        )
    conn.commit()


def application(environ: dict, start_response: callable):
    """Do something"""
    form = parse_formvars(environ)
    if form.get("doedit") is not None:
        make_edit(form)
    appopts = {}
    appid = form.get("appid", -1)
    if appid is None or appid == "":
        appid = -1
    appid = int(appid)
    if appid >= 0:
        appopts = get_appopts(appid)

    start_response("200 OK", [("Content-type", "text/html")])
    res = PAGE % {
        "user": environ["REMOTE_USER"],
        "appid": form.get("appid", ""),
        "appopts": generate_apps(),
        "name": appopts.get("name", ""),
        "url": appopts.get("url", ""),
        "description": appopts.get("description", ""),
        "category": appopts.get("category", ""),
        "subcategory": appopts.get("subcategory", ""),
        "tags": appopts.get("tags", ""),
        "importance": appopts.get("importance", ""),
    }
    return [res.encode("ascii")]
