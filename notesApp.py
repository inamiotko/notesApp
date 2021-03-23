from flask import Flask, render_template, request, session
import sqlite3 as sql

app = Flask(__name__)

occurrences = []


@app.route('/')
def home():
    try:
        conn = sql.connect('database.db')
        print("Opened database successfully")

        conn.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL, '
                     'added TEXT NOT NULL)')
        conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, note_id INTEGER NOT '
                     'NULL,title TEXT NOT NULL, added TEXT NOT NULL , modified TEXT NOT NULL, content TEXT NOT NULL, '
                     'deleted INT NOT NULL, edited INT NOT NULL, FOREIGN KEY (note_id) REFERENCES notes(id),'
                     'UNIQUE(note_id,title,edited,deleted) ON CONFLICT IGNORE)')
        print("Tables opened successfully")
    except sql.Error as error:
        print("Failed to create table ", error)

    conn.close()
    return render_template('index.html')


@app.route('/addtodb', methods=['POST', 'GET'])
def addtodb():
    if request.method == 'POST':
        try:
            conn = sql.connect('database.db')
            title = request.form['title']
            content = request.form['content']
            created = request.form['added']
            conn.execute("INSERT INTO notes (title, added) VALUES(?, ?)", (title, created))

            conn.execute(
                "INSERT INTO items (deleted, edited, title,content, added, modified, note_id) SELECT ?,?,?,?,?,?, "
                "id FROM notes WHERE id=id AND NOT EXISTS (SELECT 1 FROM items WHERE (items.title = notes.title AND "
                "items.note_id=notes.id))", (0, 0, title, content, created, created))
            conn.commit()
            print("Note added")

        except sql.Error as error:
            print("Failed to add record ", error)

        return render_template("added.html")
        conn.close()


@app.route('/results')
def results():
    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        conn.row_factory = sql.Row
        cur.execute("SELECT * FROM notes")
        data = cur.fetchall()
    except sql.Error as error:
        print("Failed to make query ", error)
    return render_template('results.html', data=data)


@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        try:
            conn = sql.connect('database.db')
            cur = conn.cursor()
            id_up = request.form['id']
            title_up = request.form['title']
            cur.execute("SELECT content FROM items WHERE (note_id=? AND title=?)", (id_up, title_up))
            content_up = cur.fetchall()
            content = content_up.pop()
            content = content[0]

        except sql.Error as error:
            print("Failed to update table ", error)
    return render_template('update.html', id=id_up, title=title_up, content=content)


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    if request.method == 'POST':
        try:
            conn = sql.connect('database.db')
            title = request.form['titleN']
            id_up = request.form['idN']
            content = request.form['contentN']
            modified = request.form['modifiedN']
            print(title, content, id_up, modified)
            cur = conn.cursor()
            occurrences.append(id_up)
            ver = occurrences.count(id_up)
            conn.execute("INSERT INTO items (note_id, edited, deleted,title,content, added, modified) SELECT note_id, "
                         "? ,deleted,?,?, added, ? FROM items WHERE note_id=?", (ver, title, content, modified, id_up))
            conn.execute("UPDATE notes SET title=? WHERE id=? ", (title, id_up))
            conn.commit()
            print("note changed")
            cur.close()
        except sql.Error as error:
            print("Failed to edit table ", error)
    return render_template('added.html')


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        id_del = request.form['delete']
        cur.execute("DELETE FROM notes WHERE id=?", (id_del,))
        cur.execute("UPDATE items SET deleted =? WHERE note_id=? ", (1, id_del))
        conn.commit()
        data_aft = cur.fetchall()
    except sql.Error as error:
        print("Failed to delete record ", error)
    return render_template('delete.html', data=data_aft)


@app.route('/details', methods=['POST', 'GET'])
def details():
    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        id_show = request.form['details']
        cur.execute("SELECT * FROM items WHERE note_id=? ORDER BY edited ASC", id_show)
        conn.commit()
        data_aft = cur.fetchall()
    except sql.Error as error:
        print("Failed to query details ", error)
    return render_template('details.html', data=data_aft)


if __name__ == '__main__':
    app.run()
    app.run(debug=True, port=5000)
