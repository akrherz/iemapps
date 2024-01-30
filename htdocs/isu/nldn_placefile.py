"""Generate a NLDN Gibson Ridge Placefile for ISU research usage."""
from datetime import datetime, timezone

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
            f'Icon: {row["y"]:.4f}, {row["x"]:.4f}, 0, 1, 1, '
            f'"{row["v"]:%H:%M:%S} UTC"\n'
        )


@iemapp(iemdb="nldn", parse_times=False, iemdb_cursorname="nldn")
def application(environ, start_response):
    """WSGI application."""
    fmt = (
        "%Y-%m-%dT%H:%M:%SZ"
        if len(environ["sts"]) == 20
        else "%Y-%m-%dT%H:%MZ"
    )
    sts = datetime.strptime(environ["sts"], fmt)
    sts = sts.replace(tzinfo=timezone.utc)
    ets = datetime.strptime(environ["ets"], fmt)
    ets = ets.replace(tzinfo=timezone.utc)
    content = f"""
Title: NLDN {sts} to {ets}
Color: 255 255 255
IconFile: 1, 32, 32, 16, 16, "http://www.meteor.iastate.edu/~jpatton/lightning_icon.png"
Font: 1, 9, 0, "Courier New"

{''.join(gen_strikes(environ['iemdb.nldn.cursor'], sts, ets))}
    """
    start_response("200 OK", [("Content-type", "text/plain")])
    return [content.encode("ascii")]
