import cs304dbi as dbi
myStaffId = 8570

def check_tt_exists(conn, tt):
    """
    If a movie with the given tt is in the database, return a dictionary containing the title of the movie
    If a movie with the given tt does NOT exist in the database, return None
    """
    curs = dbi.dict_cursor(conn)
    curs.execute( # search for the given movie
        '''
        select title from movie
        where tt = %s;
        ''', [tt]
    )
    return curs.fetchone()

def insert_movie(conn, formData):
    """
    Insert a movie row into movie table
    using tt, title, and release year
    """
    curs = dbi.dict_cursor(conn)
    curs.execute( # insert given movie into movie table
        '''
        insert into movie(tt, title, `release`, addedby)
        values (%s, %s, %s, %s);
        ''', [formData.get('movie-tt'), formData.get('movie-title'), formData.get('movie-release'), myStaffId]
    )
    conn.commit() # Makes the change permanent
    return 'You just added {title} at tt = {tt}'.format(title=formData.get('movie-title'), tt=formData.get('movie-tt'))


if __name__ == '__main__':
    dbi.conf('kb102_db')
    conn = dbi.connect()
    check_tt_exists(conn, 5555)
    # fakeMovie = {'tt':556, 'title':'The Worst Movie You Ever Wasted 3 Hours On', 'addedby':myStaffId}
    # success = insert_movie(conn, fakeMovie)
    # print(success)
    