from flask import Flask, render_template, request, g
import sqlite3 as sql

app = Flask(__name__)
DATABASE = 'database.db'
occurrences = []


# database initialisation
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# function that connects to db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sql.connect(DATABASE)
    return db


# closing connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# welcome page with add note form
@app.route('/')
def home():
    init_db()
    return render_template('index.html')


# adding records to db
@app.route('/addtodb', methods=['POST'])
def addtodb():
    if request.method == 'POST':
        try:
            db = get_db()
            title = request.form['title']
            content = request.form['content']
            created = request.form['added']
            db.execute("INSERT INTO notes (title, added) VALUES(?, ?)", (title, created))

            db.execute(
                "INSERT INTO items (deleted, edited, title,content, added, modified, note_id) SELECT ?,?,?,?,?,?, "
                "id FROM notes WHERE id=id AND NOT EXISTS (SELECT 1 FROM items WHERE (items.title = notes.title AND "
                "items.note_id=notes.id))", (0, 0, title, content, created, created))
            db.commit()
            print("Note added")

        except sql.Error as error:
            print("Failed to add record ", error)

        return render_template("added.html")
        conn.close()


# displaying all results from notes table
@app.route('/results')
def results():
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM notes")
        data = cur.fetchall()
    except sql.Error as error:
        print("Failed to make query ", error)
    return render_template('results.html', data=data)


# getting data from table to update it
@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        try:
            db = get_db()
            cur = db.cursor()
            id_up = request.form['id']
            title_up = request.form['title']
            cur.execute("SELECT content FROM items WHERE (note_id=? AND title=?)", (id_up, title_up))
            content_up = cur.fetchall()
            content = content_up.pop()
            content = content[0]
        except sql.Error as error:
            print("Failed to fetch table ", error)
    return render_template('update.html', id=id_up, title=title_up, content=content)


# updating table with data inserted in form
@app.route('/edit', methods=['POST'])
def edit():
    if request.method == 'POST':
        try:
            db = get_db()
            title = request.form['titleN']
            id_up = request.form['idN']
            content = request.form['contentN']
            modified = request.form['modifiedN']
            print(title, content, id_up, modified)
            cur = db.cursor()
            occurrences.append(id_up)
            ver = occurrences.count(id_up)
            db.execute("INSERT INTO items (note_id, edited, deleted,title,content, added, modified) SELECT note_id, "
                       "? ,deleted,?,?, added, ? FROM items WHERE note_id=?", (ver, title, content, modified, id_up))
            db.execute("UPDATE notes SET title=? WHERE id=? ", (title, id_up))
            db.commit()
            print("note changed")
            cur.close()
        except sql.Error as error:
            print("Failed to edit table ", error)
    return render_template('added.html')


# deleting chosen records
@app.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        try:
            db = get_db()
            cur = db.cursor()
            id_del = request.form['delete']
            cur.execute("DELETE FROM notes WHERE id=?", (id_del,))
            cur.execute("UPDATE items SET deleted =? WHERE note_id=? ", (1, id_del))
            db.commit()
            data_aft = cur.fetchall()
        except sql.Error as error:
            print("Failed to delete record ", error)
    return render_template('delete.html', data=data_aft)


# displaying details about each note
@app.route('/details', methods=['POST'])
def details():
    if request.method == 'POST':
        try:
            db = get_db()
            cur = db.cursor()
            id_show = request.form['details']
            print(id_show)
            cur.execute("SELECT * FROM items WHERE note_id=? ORDER BY edited ASC", (id_show,))
            db.commit()
            data_aft = cur.fetchall()
        except sql.Error as error:
            print("Failed to query details ", error)
    return render_template('details.html', data=data_aft)


# displaying content and title of each note when title pressed
@app.route('/readonly', methods=['POST'])
def readonly():
    if request.method == 'POST':
        try:
            db = get_db()
            cur = db.cursor()
            title_read = request.form['titleRead']
            id_read = request.form['idRead']
            cur.execute("SELECT content FROM items WHERE (note_id=? AND title=?)", (id_read, title_read))
            db.commit()
            content_read = cur.fetchall()
            content = content_read.pop()
            content = content[0]
        except sql.Error as error:
            print("Failed to query details ", error)
    return render_template('readonly.html', content=content, title=title_read)


if __name__ == '__main__':
    app.run()
    app.run(debug=True, port=5000)
