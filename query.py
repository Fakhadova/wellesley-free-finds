#This file contains functions interacting with the database

# configure DBI
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
    
