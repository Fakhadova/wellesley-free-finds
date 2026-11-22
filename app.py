from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, abort)
app = Flask(__name__)

import os
import cs304dbi as dbi
import pymysql
import secrets

from pwd_context import hash_password, verify_password
from werkzeug.utils import secure_filename
#helper functions
from query import *


# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

#photo uploads for posts (photos are stored in the picfile table, not on disk)
app.config['MAX_CONTENT_LENGTH']=5 * 1024 * 1024


@app.route('/')
def index():
    #making sure log-ined users are sent to home
    if session.get('uid'):
        return redirect(url_for('home'))
    return render_template('main.html', page_title='Main Page')


@app.route('/register/', methods=["POST"])
def register():
    """Register a new user."""
    username = request.form.get('username', '').strip()
    passwd1 = request.form.get('password1', '')
    passwd2 = request.form.get('password2', '')
    if not username or len(username) > 20:
        flash('Username is required (max 20 characters).)')
        return redirect(url_for('index'))
    if not passwd1:
        flash('Password is required.')
        return redirect(url_for('index'))
    if not passwd2:
        flash('Please confirm your password.')
        return redirect(url_for('index'))
    if passwd1 != passwd2:
        flash('Passwords do not match.')
        return redirect(url_for('index'))
    hashed = hash_password(passwd1)

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
            session.clear()
            session['username'] = username
            session['uid'] = uid
            session['logged_in'] = True
            session['visits'] = 1
            flash("Account created successfully.")
            return redirect(url_for('home'))

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
                # all done; go to the user's home page
                return redirect(url_for('home'))
            else:
                flash('login incorrect. Try again or register')
                return redirect( url_for('index'))

@app.route('/home/', endpoint='home')
def home():
    #search and filter functionality for the home page
    filters= {
        'keyword': request.args.get('keyword', '').strip(), #our search term
        'post_type': request.args.get('post_type', ''),
        'categories': request.args.getlist('category'),
        'statuses': request.args.getlist('status'),
        'sort': request.args.get('sort', 'newest'),
    }
    with dbi.connect() as conn:
        posts= get_all_active_posts(conn, **filters)
    #making this true if the user used search or filter so the "clear" button shows up
    filtering= bool(filters['keyword'] or filters['post_type']
                     or filters['categories'] or filters['statuses'])
    return render_template('home.html', page_title='Home Page', posts=posts,
                           filters=filters, filtering=filtering,
                           categories=CATEGORIES, active_statuses=ACTIVE_STATUSES)

@app.route('/user/<username>')
def user(username=None):
    # don't trust the URL; it's only there for decoration
    # it could just as easily be omitted
    if 'username' in session:
        username = session['username']
        uid = session['uid']
        session['visits'] = 1+int(session.get('visits',0))
        # return render_template('greet.html',
        #                        page_title=f'My App: Welcome {username}',
        #                        name=username,
        #                        uid=uid,
        #                        visits=session['visits'])

        return render_template('home.html', page_title='Home Page')
    else:
        flash('you are not logged in. Please login or join')
        return redirect( url_for('index') )

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

@app.route('/post/<int:pid>/make_request/', methods=['POST'])
def make_request(pid):
    sid = session.get('uid')
    if not sid:
        flash('Please login first')
        return redirect(url_for('index'))

    with dbi.connect() as conn:
        post = get_post_details(conn, pid) #whatever you use to find a post based on pid
        if post is None:
            flash("Post doesn't exist")
            return redirect(url_for('index'))
        if post['uid'] == sid:
            flash("You can't request to your own post")
        elif post['status'] not in ('Available', 'Open'):
            flash('This post is not available')
        else:
            add_request(conn, sid, pid, 'Pending')
            flash('request sent')
        return redirect(url_for('post_detail', pid=pid))

@app.route('/post/<int:pid>/cancel/', methods=['POST'])
def cancel_request(pid):
    uid = session.get('uid')
    if not uid:
        flash('please login first')
        return redirect(url_for('login'))
    with dbi.connect() as conn:
        post = get_post_details(conn, pid)
        if post is None:
            flash("Post doesn't exist")
            return redirect(url_for('index'))
        #user trying to cancell request on their own post
        if post['uid'] == uid:
            flash("You can't cancel request to your own post")
            return redirect(url_for('index'))
        interest = get_interest_bypid(conn, pid, uid)

        #if request hasn't been made or request was not in pending or accepted
        if interest is None or interest['status'] not in ('Pending', 'Accepted'):
            flash("You have not made a request")
            return redirect(url_for('post_detail', pid=pid))
        #someone else is trying to cancel a request
        if interest['uid']!=uid:
            flash("You cannot cancel someone else's request")
            return redirect(url_for('post_detail', pid=pid))
        #withdraw interest
        withdraw_interest(conn, interest['iid'])
        if interest['status'] == 'Accepted' and post['status'] == 'Claimed':
            change_post_status(conn, pid, 'Available')
        flash("Your request was withdrawn")
        return redirect(url_for('post_detail', pid=pid))

@app.route('/profile/interest_list/<int:iid>/accept', methods=['POST'])#what is the endpoint of this?
def accept_interest(iid):
    username = session.get('username')
    uid = session.get('uid')
    if not username:
        flash('Please log in')
        return redirect(url_for('index'))
    with dbi.connect() as conn:
        interest = get_interest_byiid(conn, iid)
        if not interest:
            flash("This request doesn't exist")
        if interest['status']!='Pending':
            flash('you cannot accept this interest')
            return redirect(url_for('profile', username=username))
        post = get_post_details(conn, interest['pid'])
        #someone else is trying to accept a request
        if post is None or post['uid']!=uid:
            flash("You cannot accept interest on someone else's post")
            return redirect(url_for('post_detail', pid=interest['pid']))
        elif post['status'] not in ('Available', 'Open'):
            flash('This item is already filled')
            return redirect(url_for('profile', username=username))
        else:
            accept_request(conn, iid)
            change_post_status(conn, interest['pid'], 'Claimed')
            flash('Accepted the interest')
        return redirect(url_for('profile', username=username))

@app.route('/profile/interest_list/<int:iid>/decline', methods=['POST'])#what is the endpoint of this?
def decline_interest(iid):
    username = session.get('username')
    uid = session.get('uid')
    if not username:
        flash('please log in first')
        redirect(url_for('index'))
    with dbi.connect() as conn:
        interest = get_interest_byiid(conn, iid)
        if not interest:
            flash("This request doesn't exist")
        post = get_post_details(conn, interest['pid'])
        #someone else is trying to accept a request
        if post['uid']!=uid:
            flash("You cannot accept interest on someone else's post")
            return redirect(url_for('post', pid=interest['pid']))
        else:
            decline_request(conn, iid)
        return redirect(url_for('profile', username=username))

@app.route('/profile/<username>')
# Profile (Team Member 1): Display the current user's Donate and Request posts in Profile.
def profile(username):
    if 'username' not in session or session['username'] != username:
        flash('You are not authorized to view this profile.')
        return redirect(url_for('index'))
    uid = session['uid']

    # Fetch the user's donate and request posts from the database
    with dbi.connect() as conn:
        with dbi.dict_cursor(conn) as curs:
            curs.execute('''SELECT * FROM posts WHERE uid = %s''', [uid])
            posts = curs.fetchall()
            curs.execute('''SELECT * from posts where uid = %s and is_deleted = 0 and status not in ('Completed', 'Fulfilled')
            order by posted_at desc''', [uid])
            active_posts = curs.fetchall()
            curs.execute('''SELECT * from posts where uid = %s and is_deleted = 0 and status in ('Completed', 'Fulfilled')
            order by posted_at desc''', [uid])
            archived_posts = curs.fetchall()
            curs.execute('''SELECT posts.* from posts join saved_posts on posts.pid = saved_posts.pid where saved_posts.uid = %s and posts.is_deleted = 0 order by saved_posts.sid desc''', [uid])
            saved_posts = curs.fetchall()
            interests = get_interest_on_my_post(conn, uid)
            my_interests = get_my_interests(conn, uid)
    return render_template('profile.html', page_title = f"{username}'s Profile", active_posts = active_posts, archived_posts = archived_posts, saved_posts = saved_posts, interests = interests, my_interests = my_interests)


# Donate Listings & Request Posts Code
ALLOWED_PHOTO_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

@app.template_filter('category_labels')
def category_labels(category_set):
    """turning our db volumns to display labels"""
    return [CATEGORIES.get(c,c) for c in category_set.split(',') if c]


@app.errorhandler(413) #we need to check if this works
def photo_too_large(err):
    flash('That photo is too large (max 5 MB).')
    return redirect(url_for('post'))


def photo_extension(file):
    """returns the photo's lowercase extension, or None if no file was chosen.
    raises ValueError if it isn't an allowed image type"""
    if file is None or file.filename=='':
        return None
    ext=file.filename.rsplit('.', 1)[-1].lower()
    if '.' not in file.filename or ext not in ALLOWED_PHOTO_EXTENSIONS:
        raise ValueError('Photo must be a JPG, PNG, GIF, or WEBP image.')
    return ext


PHOTO_MIMETYPES = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                   'gif': 'image/gif', 'webp': 'image/webp'}


def save_photo(conn, pid, file, ext):
    """stores the photo's bytes in picfile under the name <pid>.<ext>"""
    filename=secure_filename(f'{pid}.{ext}')
    add_photo(conn, pid, filename, PHOTO_MIMETYPES[ext], file.read())


@app.route('/post/', methods=['GET', 'POST'])
def post():
    """page to create a donate or request post"""
    uid=session.get('uid')
    if not uid:
        flash('Please log in to create a post.')
        return redirect(url_for('index'))
    if request.method=='GET':
        return render_template('create_post.html', page_title='Create a Post',
                               categories=CATEGORIES, form={})
    form=request.form
    post_type=form.get('post_type') #getting whether its a donate or request
    title=form.get('title', '').strip()
    description=form.get('description', '').strip()
    categories=[c for c in form.getlist('category') if c in CATEGORIES]
    photo=request.files.get('photo')
    errors = [] #copilot randomly added these so we have to check but they seem to be used for form validation
    if post_type not in INITIAL_STATUS:
        errors.append('Choose Donate or Request.')
    if not title or len(title) > 100:
        errors.append('Item name is required (max 100 characters).')
    if not description or len(description) > 500:
        errors.append('Description is required (max 500 characters).')
    if not categories:
        errors.append('Choose at least one category.')
    if post_type == 'Donate' and (photo is None or photo.filename == ''):
        errors.append('Donate posts require a photo.')
    ext=None
    if not errors:
        try:
            ext=photo_extension(photo) #check the photo type BEFORE creating the post
        except ValueError as err:
            errors.append(str(err))
    if errors:
        for e in errors:
            flash(e)
        #we rerender the create post page so they can try again
        return render_template('create_post.html', page_title='Create a Post',
                               categories=CATEGORIES, form=form,
                               chosen=categories)
    with dbi.connect() as conn:
        pid=add_post(conn, uid, post_type, title, description, #now we add the post and it will return the pid
                       categories)
        if ext:
            save_photo(conn, pid, photo, ext) #photo is named after the pid, so it's saved after the post
    flash(f'Your {post_type.lower()} post was created!')
    return redirect(url_for('post_detail', pid=pid)) #i'm thinking like in the movies, we redirect to their new post page


@app.route('/post/<int:pid>/')
def post_detail(pid):
    """shows a single post"""
    uid = session.get('uid')
    with dbi.connect() as conn:
        p = get_post_details(conn, pid)
        if p is None:
            flash("That post doesn't exist.")
            return redirect(url_for('index'))
        interest = get_interest_bypid(conn, pid, uid) if uid else None
    return render_template('post_detail.html', page_title=p['title'],
                           post=p, uid=uid, interest=interest)


# Request Post Management: Allow owners to edit, delete, or mark Request posts as Fulfilled. Move Fulfilled posts to the owner's archive and close outstanding offers. Maybe take them to edit_post_detail.html? with sessions though?
#@app.route('/post/<int:pid>/edit/', methods = ['GET', 'POST'])
#def edit_post(pid):
@app.route('/post/<int:pid>/edit/', methods = ['GET', 'POST'])
#Edit post from profile page - Allow owners to edit, delete, mark request posts as fufilled from their own posts from the active posts listed in their profile. Move fulfilled posts to the owner's archive and close outstanding offers.
def edit_post(pid):
    uid = session.get('uid')
    if not uid:
        flash('Please log in to edit your post.')
        return redirect(url_for('index'))
    with dbi.connect() as conn:
        post = get_post_details(conn, pid)
        
        if post is None:
            flash("That post doesn't exist.")
            return redirect(url_for('index'))

        if post['uid'] != uid:
            flash("You are not authorized to edit this post.")
            return redirect(url_for('index'))

        if post['post_type'] != 'Request':
            flash("Donate post editing is not available yet.")
            return redirect(url_for('post_detail', pid=pid))
        
        if post['status'] == 'Fulfilled':
            flash('This post has already been fulfilled.')
            return redirect(url_for('post_detail', pid=pid))

        if request.method == 'GET':
            return render_termplate(
                'edit_post.html', 
                post = post,
                categories = CATEGORIES,
                form = {},
                chosen = post['category'].split(','))
        
        #Get the submitted form values
        form = request.form
        title = form.get('title', '').strip()
        description = form.get('description', '').strip()
        categories = [c for c in form.getlist('category') if c in CATEGORIES]
        errors = []
        
        if not title or len(title) > 100:
            errors.append('Item name is required (max 100 characters).')
        
        if not description or len(description) > 500:
            errors.append('Description is required (max 500 characters).')
        
        if not categories:
            errors.append('Choose at least one category.')
        
        #A new photo is optional
        ext = None
        try: 
            ext = photo_extention(photo)
        except ValueError as err:
            errors.append(str(err))

        if errors:
            for error in errors:
                flash(error)
            return render_template('edit_post.html', page_title = 'Edit Post', 
            post = post, categories = CATEGORIES, form = form, chosen = categories)

        #Update the post's text info 

        update_post(conn, pid, title, description, categories)

        #replace the photo only if new one is uploaded
        if ext: 
            save_photo(conn, pid, photo, ext)
    flash('Your post has been updated.')
    return redirect(url_for('post_detail', pid = pid))







@app.route('/uploads/<filename>')
def uploaded_photo(filename):
    """sends a post's photo straight from the picfile table"""
    with dbi.connect() as conn:
        row=get_photo(conn, filename)
    if row is None:
        abort(404)
    return Response(row['photo'], mimetype=row['mimetype'])

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
