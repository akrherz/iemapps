"""
IEM /admin/ front page driving my mod_wsgi and takes the Okta SSO Oauth
provided username.
"""

PAGE = """
<html><head><title>IEM Admin</title></head>
<body>

<p>Hello, %(user)s!</p>

<ul>
    <li><a href="add_news.phtml">Add a news item</a></li>
    <li><a href="add_site.phtml">Add a mesosite station...</a></li>
    <li><a href="feature.php">IEM Feature Editor</a></li>
    <li><a href="props.phtml">IEM Properties Editor</a></li>
    <li><a href="iembot.php">IEMBot Room/Channel Config</a></li>
</ul>
</body>
</html>
"""


def application(envion, start_response):
    """Do something"""
    start_response("200 OK", [("Content-type", "text/html")])
    res = PAGE % {"user": envion["REMOTE_USER"]}
    return [res.encode("ascii")]
