#This file contains functions interacting with the database
import cs304dbi as dbi

dbi.conf('fahama_db')

def add_request(conn, sid, pid, status):
    '''adding interest to interest table (pid, uid, status)'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
        insert into interests (pid, uid, status)
        values (%s, %s, %s)
        on duplicate key update status='Pending'
        ''', [pid, sid, status])
        conn.commit()
        return

def accept_request(conn, iid):
    '''change the status of interest at iid to Accepted'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
        update interests
        set status='Accepted'
        where iid=%s
        ''',[iid])
    conn.commit()

def decline_request(conn, iid):
    '''change the status of interest at iid to Declined'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
        update interests
        set status='Declined'
        where iid=%s
        ''',[iid])
    conn.commit()

def get_interest_bypid(conn, pid, uid):
    '''getting post request based on iid'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            select * from interests
            where pid=%s and uid=%s
        ''', [pid, uid])
        return curs.fetchone()

def get_interest_byiid(conn, iid):
    '''getting post request based on iid'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            select * from interests
            where iid=%s
        ''', [iid])
        return curs.fetchone()

def withdraw_interest(conn, iid):
    '''change the status of iid to Withdrawn'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            update interests
            set status='Withdrawn'
            where iid=%s
        ''',[iid])
        conn.commit()
    return

def change_post_status(conn, pid, status):
    '''change the status of iid to given status'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            update posts
            set status=%s
            where pid=%s
        ''', [status, pid])
        conn.commit()
    return
def get_my_interests(conn, uid):
    '''all requests/offers the user has made, with the poster's username'''
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            SELECT i.iid,
                   i.status   AS interest_status,
                   p.pid, p.title, p.post_type, p.category,p.posted_at,
                   p.status   AS post_status,
                   u.username AS poster,
                   f.filename AS photo_filename
            FROM interests i
                JOIN posts p USING (pid)
                JOIN users u ON p.uid = u.uid
                LEFT JOIN picfile f ON f.pid = p.pid
            WHERE i.uid = %s
              AND p.is_deleted = 0
            ORDER BY i.status, p.posted_at DESC
        ''', [uid])
        return curs.fetchall()
def get_interest_on_my_post(conn, uid):
    with dbi.dict_cursor(conn) as curs:
        curs.execute('''
            SELECT i.iid,
                   i.status   AS interest_status,
                   u.username AS requester,
                   p.pid, p.title, p.post_type,
                   p.status   AS post_status
            FROM interests i
                JOIN posts p ON i.pid = p.pid
                JOIN users u ON i.uid = u.uid
            WHERE p.uid = %s
              AND p.is_deleted = 0
              AND i.status IN ('Pending', 'Accepted')
            ORDER BY p.posted_at DESC, i.iid
        ''', [uid])
        return curs.fetchall()

#Code for donate listings & request posts
#making global variables to make life easier and to match it with the db
CATEGORIES={
    'Clothing_Shoes': 'Clothing/Shoes',
    'School_Supplies': 'School Supplies',
    'Kitchenware': 'Kitchenware',
    'Books': 'Books',
    'Technology': 'Technology',
    'Decorations_Furniture': 'Decorations/Furniture',
    'Tools_Sporting_Goods': 'Tools/Sporting Goods',
    'Miscellaneous': 'Miscellaneous',
}

#the starting statuses
INITIAL_STATUS = {'Donate':'Available','Request':'Open'}
#the statuses that are archived and hidden from Home
ARCHIVED_STATUSES = ('Completed','Fulfilled')
def add_post(conn, uid, post_type, title, description, categories):
    '''inserts a new post (donate or request) and returns the pid.
    the photo is stored separately in picfile (see add_photo)'''
    curs=dbi.cursor(conn)
    curs.execute('''
        insert into posts (uid, post_type, title, description, category,
                           status, is_deleted, posted_at)
        values (%s, %s, %s, %s, %s, %s, 0, now())
    ''', [uid, post_type, title, description, ','.join(categories),
          INITIAL_STATUS[post_type]])
    conn.commit()
    return curs.lastrowid

def add_photo(conn, pid, filename, mimetype, data):
    '''stores a post's photo (the image bytes themselves) in picfile.
    one photo per post; storing it in the shared DB means everyone sees it'''
    curs=dbi.cursor(conn)
    curs.execute('''
        insert into picfile (pid, filename, mimetype, photo)
        values (%s, %s, %s, %s)
        on duplicate key update filename=values(filename),
            mimetype=values(mimetype), photo=values(photo)
    ''', [pid, filename, mimetype, data])
    conn.commit()

def get_photo(conn, filename):
    '''returns {mimetype, photo} for a photo filename, or None'''
    curs=dbi.dict_cursor(conn)
    curs.execute('''
        select mimetype, photo from picfile where filename = %s
    ''', [filename])
    return curs.fetchone()

def get_all_active_posts(conn):
    '''all posts shown in home with newest first.
    excludes deleted and archived posts'''
    curs=dbi.dict_cursor(conn)
    curs.execute('''
        select p.pid, p.uid, u.username, p.post_type, p.title,
               p.description, p.category, f.filename as photo_filename,
               p.status, p.posted_at
        from posts p join users u using (uid)
                     left join picfile f using (pid)
        where p.is_deleted = 0 and p.status not in (%s, %s)
        order by p.posted_at desc
    ''', list(ARCHIVED_STATUSES))
    return curs.fetchall()

def get_active_posts(conn):
    '''same posts as get_all_active_posts but split into donate or request'''
    donate=[]
    request=[]
    for post in get_all_active_posts(conn):
        (donate if post['post_type']=='Donate' else request).append(post)
    return donate, request

def get_post_details(conn, pid):
    '''returns a non-deleted post with its author's username, im assuming we need this later'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select p.pid, p.uid, u.username, p.post_type, p.title,
               p.description, p.category, f.filename as photo_filename,
               p.status, p.is_deleted, p.posted_at
        from posts p join users u using (uid)
                     left join picfile f using (pid)
        where p.pid = %s and p.is_deleted = 0
    ''', [pid])
    return curs.fetchone()

def search_posts(conn, keyword):
    '''searches for posts with the keyword in title'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select p.pid, p.uid, u.username, p.post_type, p.title,
               p.description, p.category, f.filename as photo_filename,
               p.status, p.posted_at
        from posts p join users u using (uid)
                     left join picfile f using (pid)
        where p.title like %s
          and p.is_deleted = 0 and p.status not in (%s, %s)
        order by p.posted_at desc
    ''', ['%' + keyword + '%'] + list(ARCHIVED_STATUSES))
    return curs.fetchall()
