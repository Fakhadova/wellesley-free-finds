from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory)
app = Flask(__name__)

import os
import cs304dbi as dbi
import pymysql
import secrets
app.secret_key = secrets.token_hex()

from pwd_context import hash_password, verify_password

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True


@app.route('/')
def index():
    return render_template('main.html', page_title='Main Page')

@app.route('/register/', methods=["POST"])
def register():
    username = request.form.get('username', '').strip()
    passwd1 = request.form.get('password1')
    passwd2 = request.form.get('password2')
    if username == '':
        flash('username is required')
        return redirect(url_for('index'))
    if passwd1 == '':
        flash('password is required')
        return redirect(url_for('index'))
    # this is also a good place to enforce, say, minimum password
    # length
    if passwd1 != passwd2:
        flash('passwords do not match')
        return redirect( url_for('index'))
    hashed = hash_password(passwd1)
    print('REGISTER', username)
    # should probably be a helper function
    with dbi.connect() as conn:
        with dbi.cursor(conn) as curs:
            try:
                curs.execute('''INSERT INTO users(uid,username,password_hash)
                                VALUES(null,%s,%s)''',
                                [username, hashed])
                conn.commit()
            except pymysql.IntegrityError as err:
                flash(f'Username taken: {err}')
                return redirect(url_for('index'))
            uid = curs.lastrowid
            flash(f'FYI, you were issued UID {uid}')
            session['username'] = username
            session['uid'] = uid
            session['logged_in'] = True
            session['visits'] = 1
            return redirect(url_for('index'))

@app.route('/login/', methods=["POST"])
def login():
    username = request.form.get('username', '').strip()
    passwd = request.form.get('password', '')
    # should use a helper function
    with dbi.connect() as conn:
        with dbi.dict_cursor(conn) as curs:
            curs.execute('''SELECT uid,password_hash
                            FROM users
                            WHERE username = %s''',
                            [username])
            row = curs.fetchone()
            if row is None:
                # Same response as wrong password,
                # so no information about what went wrong
                flash('login incorrect. Try again or register')
                return redirect( url_for('index'))
            stored = row['password_hash']
            print('ATTEMPT LOGIN', username)
            okay, new_hash = verify_password(passwd, stored)
            if okay:
                print('they match!')
                flash('successfully logged in as '+username)
                session['username'] = username
                session['uid'] = row['uid']
                session['logged_in'] = True
                session['visits'] = 1
                if new_hash is not None:
                    curs.execute('''update users set password_hash = %s where uid = %s''',
                                 [new_hash, row['uid']])
                    conn.commit()
                # all done; go to user's page
                return redirect(url_for('index'))
            else:
                flash('login incorrect. Try again or register')
                return redirect( url_for('index'))

#@app.route('/user/<username>')
#def user(username):
    # don't trust the URL; it's only there for decoration
    # it could just as easily be omitted
 #   if 'username' in session:
  #      username = session['username']
   #     uid = session['uid']
    #    session['visits'] = 1+int(session.get('visits',0))
     #   return render_template('greet.html',
      #                         page_title=f'My App: Welcome {username}',
       #                        name=username,
        #                       uid=uid,
         #                      visits=session['visits'])
    #else:
     #   flash('you are not logged in. Please login or join')
      #  return redirect( url_for('index') )

@app.route('/logout/', methods=['POST'])
def logout():
    if 'username' in session:
        username = session['username']
        session.clear()         # this pops all values
        flash('You are logged out')
        return redirect(url_for('index'))
    else:
        flash('you are not logged in. Please login or join')
        return redirect( url_for('index') )


@app.route('/post/<int:pid>/request/', methods=['POST'])
def cancell_request(pid):
    sid = session.get('uid')
    if not sid:
        flash('please login first')
        return render_template(url_for('login'))

    conn = dbi.connect()
    post = get_pos(conn, pid)

    if post is None:
        flash("Post doesn't exist")
        return render_template(url_for('index'))
    if post['uid'] == sid:
        flash("You can't cancel request to your own post")

    
def make_request(pid):
    sid = session.get('uid')
    if not sid:
        flash('Please login first')
        return render_template(url_for('login'))

    conn = dbi.connect()
    post = get_post(conn, pid) #whatever you use to find a post based on pid
    if post is None:
        flash("Post doesn't exist")
        return render_template(url_for('index'))
    if post['uid'] == sid:
        flash("You can't request to your own post")
    elif post['status'] not in ('Available', 'Open'):
        flash('This post is not available')
    else:
        add_request(conn, sid, pid, 'Pending')
        flash('request sent')
    return render_template(url_for('post', pid=pid))

@app.route()

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
