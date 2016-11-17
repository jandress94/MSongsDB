import sqlite3

def open_db_conn(filename):
    conn = sqlite3.connect(filename)
    create_indices(conn)
    return conn

def create_indices(conn):
    print 'creating indices'
    c = conn.cursor()
    q = 'CREATE INDEX IF NOT EXISTS my_sim_index ON sim_artists (start_artist_id)'
    c.execute(q)
    q = 'CREATE INDEX IF NOT EXISTS your_sim_index ON sim_artists (end_artist_id)'
    c.execute(q)
    q = 'DROP INDEX IF EXISTS my_track_index'
    c.execute(q)
    c.close()
    conn.commit()
    print 'done creating indices'

def close_db_conn(conn):
    conn.close()

def encode_string(s):
    return "'" + s.replace("'", "''") + "'"

def get_query_results_and_close(q, c):
    results = c.execute(q).fetchall()
    c.close()
    return results

# returns list of tuples (artist_id, artist_name)
def get_artists(conn, limit = None, artist_name = None):
    c = conn.cursor()
    q = 'SELECT * FROM artists'
    if artist_name is not None:
        q += ' WHERE artist_name LIKE ' + encode_string('%' + artist_name + '%')
    if limit is not None:
        q += ' LIMIT ' + str(limit)
    return get_query_results_and_close(q, c)

# returns the string of the artist's name for the artists with the given id
def get_artist_name(artist_id, conn):
    c = conn.cursor()
    q = 'SELECT artist_name FROM artists WHERE artist_id = ' + encode_string(artist_id)
    artist_name = get_query_results_and_close(q, c)
    return artist_name[0][0]

# returns list of tuples (term, term_freq, term_weight)
def get_artist_terms(artist_id, conn, limit = None):
    c = conn.cursor()
    q = 'SELECT term, term_freq, term_weight FROM terms WHERE artist_id = ' + encode_string(artist_id)
    if limit is not None:
        q += ' LIMIT ' + str(limit)
    return get_query_results_and_close(q, c)

# returns a list of artists similar to the provided artist_id
def get_sim_artists(artist_id, conn):
    c = conn.cursor()
    q = 'SELECT end_artist_id FROM sim_artists WHERE start_artist_id = ' + encode_string(artist_id)
    my_sim_artists = get_query_results_and_close(q, c)

    c = conn.cursor()
    q = 'SELECT start_artist_id FROM sim_artists WHERE end_artist_id = ' + encode_string(artist_id)
    artists_who_think_im_similar = get_query_results_and_close(q, c)

    return [artist[0] for artist in my_sim_artists + artists_who_think_im_similar]

# returns a list of tuples (track_id, track_year, track_name)
def get_artist_tracks(artist_id, conn, exclude_no_year = True, limit = None):
    c = conn.cursor()
    q = 'SELECT track_id, track_year, track_name FROM tracks WHERE artist_id = ' + encode_string(artist_id)
    if exclude_no_year:
        q += ' AND track_year > 0'
    if limit is not None:
        q += ' LIMIT ' + str(limit)
    return get_query_results_and_close(q, c)

# returns a list of artist_ids whose first song appeared before or at the year
# and last song appeared at most years_active_after_last_song years before the given year
def get_artist_ids_active_during_year(year, years_active_after_last_song, conn):
    c = conn.cursor()
    q = 'SELECT artist_id from tracks WHERE track_year > 0 GROUP BY artist_id' + \
        ' HAVING MIN(track_year) <= ' + str(year) + \
        ' AND ' + str(year) + ' <= MAX(track_year) + ' + str(years_active_after_last_song)
    artist_list = get_query_results_and_close(q, c)
    return [artist[0] for artist in artist_list]

# returns a tuple (min_year, max_year)
def get_artist_track_year_range(artist_id, conn):
    c = conn.cursor()
    q = 'SELECT MIN(track_year), MAX(track_year) from tracks WHERE track_year > 0 AND artist_id = ' + encode_string(artist_id)
    return get_query_results_and_close(q, c)[0]
