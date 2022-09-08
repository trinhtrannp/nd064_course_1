import sys
import logging
import sqlite3

from flask import Flask, jsonify, render_template, request, url_for, redirect, flash

total_connection = 0

logging.basicConfig()
logger = logging.getLogger('app')
for h in logger.handlers[:]:
    logger.removeHandler(h)
    h.close()
logFormatter = logging.Formatter(fmt='%(levelname)s:%(name)s:%(asctime)s, %(message)s', datefmt='%m/%d/%Y, %H:%M:%S')
handler = logging.StreamHandler()
handler.setLevel('DEBUG')
handler.setFormatter(logFormatter)
logger.addHandler(handler)
logger.setLevel('DEBUG')

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global total_connection
    total_connection += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to count the number of post in the database
def count_post():
    connection = get_db_connection()
    count = connection.execute('SELECT count(*) FROM posts').fetchone()
    connection.close()
    return count[0]

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logger.error(f"Article with id \"{post_id}\" does not exist!")
      return render_template('404.html'), 404
    else:
      logger.info(f"Article \"{post['title']}\" retrieved!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info(f"The \"About Us\" page is retrieved.")
    return render_template('about.html')

@app.route('/healthz')
def healthz():
    return jsonify({'result': 'OK - healthy'}), 200

@app.route('/metrics')
def metrics():
    global total_connection
    return jsonify({'db_connection_count': total_connection, 'post_count': count_post()}), 200    

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            logger.info(f"A new article is created with title '{title}'.")
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
