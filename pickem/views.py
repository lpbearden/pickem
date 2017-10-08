from pickem import app, reddit_login


@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with reddit</a>'
    return text % reddit_login.make_authorization_url()
