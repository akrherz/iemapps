"""
IEM /admin/ front page driving my mod_wsgi and takes the Okta SSO Oauth
provided username.
"""

def application(envion, start_response):
    """Do something"""
    start_response("200 OK", [("Content-type", "text/html")])
    res = f"Hello World! {envion['REMOTE_USER']}"
    return [res.encode("ascii")]
