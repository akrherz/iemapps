""".. title:: NLDN Placefile Generator

This application generates a placefile of NLDN lightning strikes for a given
time period.

Example Usage:
--------------

Get all strikes between 00:00 and 01:00 UTC on June 1, 2019:

https://iemapps.agron.iastate.edu/isu/nldn_placefile.py?sts=2019-06-01T00:00Z&ets=2019-06-01T01:00Z

Get all strikes between 00:00 and 01:00 UTC on June 1, 2019, with the lightning
strike icons colored red:

https://iemapps.agron.iastate.edu/isu/nldn_placefile.py?sts=2019-06-01T00:00Z&ets=2019-06-01T01:00Z&r=255&g=0&b=0

Parameters
----------

* `sts`: The start of the time period of interest in `YYYY-MM-DDTHH:MMZ`
    format.
* `ets`: The end of the time period of interest in `YYYY-MM-DDTHH:MMZ` format.
* `r`: The red component of the color to use for the lightning strike icons.
* `g`: The green component of the color to use for the lightning strike icons.
* `b`: The blue component of the color to use for the lightning strike icons.

"""

from pyiem.webutil import iemapp


def gen_strikes(cursor, sts, ets):
    """Do the work."""
    cursor.execute(
        """
        SELECT st_x(geom) as x, st_y(geom) as y, valid at time zone 'UTC' as v
        from nldn_all WHERE valid BETWEEN %s and %s
    """,
        (sts, ets),
    )
    for row in cursor:
        yield (
            f"Icon: {row['y']:.4f}, {row['x']:.4f}, 0, 1, 1, "
            f'"{row["v"]:%H:%M:%S} UTC"\n'
        )


@iemapp(iemdb="nldn", iemdb_cursorname="nldn", help=__doc__)
def application(environ, start_response):
    """WSGI application."""
    sts = environ["sts"]
    ets = environ["ets"]
    r = int(environ.get("r", 255))
    g = int(environ.get("g", 255))
    b = int(environ.get("b", 255))
    content = f"""
Title: NLDN {sts} to {ets}
Color: {r} {g} {b}
IconFile: 1, 32, 32, 16, 16, "http://www.meteor.iastate.edu/~jpatton/lightning_icon.png"
Font: 1, 9, 0, "Courier New"

{"".join(gen_strikes(environ["iemdb.nldn.cursor"], sts, ets))}
    """
    start_response("200 OK", [("Content-type", "text/plain")])
    return [content.encode("ascii")]
