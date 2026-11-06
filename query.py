#This file contains functions interacting with the database
import cs304dbi as dbi

#TO:DOs:
#Donate Listings (Team Member 2): Allow students to create Donate posts with an item name, description, one or more categories, and required photo. Store posts with an initial status of Available and display them on Home and individual post-detail pages.
#Request Posts (Team Member 2): Allow students to create Request posts with an item name, description, one or more categories, and optional photo. Store posts with an initial status of Open and display them in a separate section of Home.

print(dbi.conf('fahama_db'))

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

<<<<<<< HEAD
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
    
=======
def add_donate_post(conn, sid, pid, title, description, category, photo_filename, status):
    '''adding donate post when user wants to donate an item'''
    #The initial status for a donate post should be Available
    status = 'Available'
    curs = dbi.cursor(conn)
    curs.execute('''
    insert into posts (pid, uid, post_type, title, description, category, photo_filename, status, is_deleted, posted_at)
    values (%s, %s, 'Donate', %s, %s, %s, %s, %s, 0, NOW())
    ''', [pid, sid, title, description, category, photo_filename, status])
    conn.commit()
    return


def add_request_post(conn, sid, pid, title, description, category, photo_filename, status):
    '''adding request post when user wants to request an item'''
    #The initial status for a request post should be Open
    status = 'Open'
    curs = dbi.cursor(conn)
    curs.execute('''
    insert into posts (pid, uid, post_type, title, description, category, photo_filename, status, is_deleted, posted_at)
    values (%s, %s, 'Request', %s, %s, %s, %s, %s, 0, NOW())
    ''', [pid, sid, title, description, category, photo_filename, status])
    conn.commit()
    return


>>>>>>> 6afbae639e83f37cfff7c82738c948dd4a6ada2b
