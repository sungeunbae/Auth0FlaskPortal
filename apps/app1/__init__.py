PERMISSION= "read:devonly"

from authflask import AuthFlask

app = AuthFlask(__name__,permission=PERMISSION)


@app.route('/') 
def hello_world():
        return 'Hello World from {} : {} permission needed.'.format(app.import_name, app.permission)

if __name__ == '__main__':
    app.run()





	