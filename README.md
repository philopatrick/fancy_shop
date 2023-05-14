#### How to start the app

1. Create a virtual environment:

`virtualenv fancy_shop`

if there is no virtualenv, install with:

`pip install -U virtualenv`

2. Install the requirements

in the terminal, open into the virtualenv folder, then copy the webapp into that folder:

```bash
cd fancy_shop
cp -r where/webapp .
cp requirements.txt .
```

and then, install the requirement with:
`pip install -r requirements.txt`

3. Config the database

run the code to initiate database
```bash
cd webapp
python3 app.py
```

find the generated `test.sqlite` file, and replace the file with the root folder file

copy test.sqlite database into that folder:

`cp webapp/test.sqlite var/app-instance`

4. Run the app

open into webapp, and run with `python3 app.py`

```bash
cd webapp
python3 app.py
```

### how the folder organize


`models.py` hold the database model define
`app.py` hold most backend api route
`static/` hold the static file, css, js, image, and user upload files
`templates/` hold the jinjia2 template html files
`views.py` hold most view route

We seperate the flask route with flask blueprint into views and apis.

