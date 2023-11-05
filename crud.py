from flask import flash

import cs304dbi as dbi
myStaffId = 8620

def find_incomplete_movies(conn):
    """
    Returns the titles and tts of movies without release dates or without directors
    """
    curs = dbi.dict_cursor(conn)
    curs.execute(
        """
        select tt, title from movie 
        where (director is null) or (`release` is null);
        """
    )
    return curs.fetchall()


def update_movie(conn, formData, tt_old):
    """
    Change the data associated with a movie whose tt is movDict.get('tt')
    Assumes the all data inputs are valid
    """
    
    cursOld = dbi.dict_cursor(conn)
    cursNew = dbi.dict_cursor(conn)
    tt_new = int(formData.get('movie-tt'))
    cursOld.execute(# Find the movie's previous data
        """
        select tt, title, `release`, director, addedby
        from movie
        where tt = %s;
        """, [tt_old]
    )
    oldMovie = cursOld.fetchone()

    # convert string 'None' to actual Nones
    movieData = {}
    for elt in formData:
        if formData.get(elt) == 'None':
            movieData[elt] = None
        else:
            movieData[elt] = formData.get(elt)

    #check that staff exists, if they do exist, proceed and otherwise flash error
    newStaff = movieData.get('movie-addedby')
    if not (check_addedby_exists(conn, newStaff)):
        newStaff = oldMovie.get('addedby')
        flash(f"That staff member doesn't exist!")

    # check whether the proposed tt is associated with another movie
    ttTest = check_tt_exists(conn, tt_new)
    if ttTest != None: # tt is associated with another movie
        ttIsUnique = False
    else: # tt is available
        ttIsUnique = True
    print(f"tt_old is: {type(tt_old)}, tt_new is {type(tt_new)}, is tt_new unique: {ttIsUnique}, checking == condition: {tt_old == tt_new}")
    # if tt has not changed or tt is unique, proceed
    if (tt_old == tt_new) or (ttIsUnique):
        # make those changes
        # TODO: check for director accuracy and addedby accuracy, also check that tt is a valid number


        cursNew.execute(# Update movie with new data
        """
            update movie
            set tt = %s, title = %s, `release` = %s, director = %s, addedby = %s
            where tt = %s;
        """, [tt_new, movieData.get('movie-title'), movieData.get('movie-release'), movieData.get('movie-director'), newStaff, tt_old]
        )
        conn.commit()
        flash(f"TO DO: Movie ({movieData.get('movie-title')}) was updated successfully")   
    else: # if tt is not unique (is associated with another show), tell app.py to flash an error
        flash(f"Movie already exists.")

        

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

def check_addedby_exists(conn, addedby):
    """
    If the given addedby is in the database, return true
    If the given addedby is not in the database, return false
    """
    curs = dbi.dict_cursor(conn)
    curs.execute( # search for the given addedby
        '''
        select uid from staff
        where uid = %s;
        ''', [addedby]
    )
    result = curs.fetchone()
    print(result)
    if result == None:
        return False
    else:
        return True
    
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
    #print(delete_movie(conn, 555))
    # fakeMovie = {'tt':556, 'title':'The Worst Movie You Ever Wasted 3 Hours On', 'addedby':myStaffId}
    # success = insert_movie(conn, fakeMovie)
    shows = find_incomplete_movies(conn)
    for i in range(10):
        print(f"{shows.get('title')} has tt {shows.get('tt')}")
    # print(success)
    