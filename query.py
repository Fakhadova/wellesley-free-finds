#This file contains functions interacting with the database
import cs304dbi as dbi

dbi.conf('fahama_db')

def add_request(conn, sid, pid, status):
    curs = dbi.cursor(conn)
    curs.execute('''
    insert into interests (pid, uid, status)
    values (%s, %s, %s)
    on duplicate key update status='Pending'
    ''', [pid, sid, status])
    conn.commit()
    return

def get_post(conn, pid):
    '''getting post based on pid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from posts
        where pid=%s
    ''',[pid])
    return curs.fetchone()

def get_interest(conn, pid, uid):
    '''getting post request based on iid'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select * from interests
        where pid=%s and uid=%s
    ''', [pid, uid])
    return curs.fetchone()

def withdraw_interest(conn, iid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        update interests
        set status='Withdrawn'
        where iid=%s
    ''',[iid])
    curs.commit()
    return

def change_post_status(conn, pid, status):
<<<<<<< HEAD

=======
    pass



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
def add_post(conn, uid, post_type, title, description, categories, photo_filename=None):
    '''inserts a new post (donate or request) and returns the pid'''
    curs=dbi.cursor(conn)
    curs.execute('''
        insert into posts (uid, post_type, title, description, category,
                           photo_filename, status, is_deleted, posted_at)
        values (%s, %s, %s, %s, %s, %s, %s, 0, now())
    ''', [uid, post_type, title, description, ','.join(categories),
          photo_filename, INITIAL_STATUS[post_type]])
    conn.commit()
    return curs.lastrowid

def get_active_posts(conn):
    '''this is for the posts shown in home, newest first and excludes deleted and archived posts'''
    curs=dbi.dict_cursor(conn)
    curs.execute('''
        select p.pid, p.uid, u.username, p.post_type, p.title,
               p.description, p.category, p.photo_filename, p.status,
               p.posted_at
        from posts p join users u using (uid)
        where p.is_deleted = 0 and p.status not in (%s, %s)
        order by p.posted_at desc
    ''', list(ARCHIVED_STATUSES))
    donate=[]
    request=[]
    for post in curs.fetchall():
        (donate if post['post_type']=='Donate' else request).append(post)
    return donate, request

def get_post_details(conn, pid):
    '''returns a non-deleted post with its author's username, im assuming we need this later'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select p.*, u.username
        from posts p join users u using (uid)
        where p.pid = %s and p.is_deleted = 0
    ''', [pid])
    return curs.fetchone()
>>>>>>> 158c77129704b518497c2c051fde03e35cdbd11c
