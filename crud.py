import cs304dbi as dbi
myStaffId = 8620

def update_movie(conn, formData, tt_old):
    """
    Change the data associated with a movie whose tt is movDict.get('tt')
    Assumes the all data inputs are valid
    """
    cursOld = dbi.dict_cursor(conn)
    cursNew = dbi.dict_cursor(conn)
    tt_new = formData.get('movie-tt')
    cursOld.execute(# Find the movie's previous data
        """
        select tt, title, `release`, director, addedby
        from movie
        where tt = %s;
        """, [tt_old]
    )
    oldMovie = cursOld.fetchone()
    # check whether the proposed tt is associated with another movie
    ttTest = check_tt_exists(tt_new)
    if ttTest != None: # tt is associated with another movie
        ttIsUnique = False
    else: # tt is available
        ttIsUnique = True
    # if tt has not changed or tt is unique, proceed
    # if tt is not unique (is associated with another show), tell app.py to flash an error
    if (tt_old == tt_new) or (ttIsUnique):
    # make those changes
    else:

def delete_movie(conn, tt):
    """
    Remove movie with given tt from the database
    Assumes the tt is valid
    """
    curs = dbi.dict_cursor(conn)
    curs.execute(
        """
        delete from movie
        where tt = %s;
        """, [tt]
    )
    conn.commit() # Makes the deletion permanent

def movie_details(conn, tt):
    """
    Returns a dict with information about a given movie based on the tt
    """
    cursMovie = dbi.dict_cursor(conn)
    cursDirector = dbi.dict_cursor(conn)
    cursMovie.execute( # find the given movie
        '''
        select tt, title, `release`, director as 'directorid', addedby
        from movie
        where tt = %s;
        ''', [tt]
    )
    cursDirector.execute( # find the given movie
        '''
        select name
        from person inner join movie on (director = nm)
        where tt = %s;
        ''', [tt]
    )
    movDict = cursMovie.fetchone()
    director = cursDirector.fetchone()
    movDict['directorName'] = director.get('name') if (director != None) else ('none specified')
    return movDict

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
    dbi.conf('je100_db')
    conn = dbi.connect()
    #print(movie_details(conn, 555))
    print(delete_movie(conn, 555))
    # fakeMovie = {'tt':556, 'title':'The Worst Movie You Ever Wasted 3 Hours On', 'addedby':myStaffId}
    # success = insert_movie(conn, fakeMovie)
    # print(success)
    