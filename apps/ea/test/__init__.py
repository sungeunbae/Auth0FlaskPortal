from authflask import AuthFlask

app = AuthFlask(__name__)


@app.route("/")
def hello_world():
    return "Hello World from {} : You have {} permission to view this page.".format(
        app.import_name, app.permission
    )


if __name__ == "__main__":
    app.run()
