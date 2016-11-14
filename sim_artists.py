import os
import sys
import glob
import time
import datetime
import sqlite3

verbose = False

def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than posgtresql, no N to specify unicode)
    EXAMPLE:
    That's my boy! -> 'That''s my boy!'
    """
    return "'" + s.replace("'", "''") + "'"

def create_database(filename):
    # creates file
    conn = sqlite3.connect(filename)
    # create artist table
    c = conn.cursor()
    q = 'CREATE TABLE artists (artist_id text primary key, artist_name text)'
    if verbose: print q
    c.execute(q)

    q = 'CREATE TABLE sim_artists (start_artist_id text, end_artist_id text, primary key(start_artist_id, end_artist_id))'
    if verbose: print q
    c.execute(q)

    q = 'CREATE TABLE tracks (track_id text primary key, artist_id text, track_year integer, track_name text)'
    if verbose: print q
    c.execute(q)

    q = 'CREATE TABLE terms (artist_id text, term text, term_freq real, term_weight real, primary key(artist_id, term))'
    if verbose: print q
    c.execute(q)
    # commit and close
    conn.commit()
    c.close()
    conn.close()

def update_terms(artist_id, term_list, freq_list, weight_list, conn):
    c = conn.cursor()
    q = 'SELECT term FROM terms WHERE artist_id = ' + encode_string(artist_id)
    if verbose: print q
    res = c.execute(q)
    existing_terms = res.fetchall()
    existing_terms = set([existing_term[0] for existing_term in existing_terms])

    terms_to_add = set()
    for i in xrange(len(term_list)):
        if term_list[i] not in existing_terms:
            terms_to_add.add(i)

    if not terms_to_add:
        return

    q = 'INSERT INTO terms VALUES (?, ?, ?, ?)'
    for idx in terms_to_add:
        if verbose: print q, artist_id, term_list[idx], freq_list[idx], weight_list[idx]
        c.execute(q, (artist_id, term_list[idx], freq_list[idx], weight_list[idx]))
    c.close()

def save_artist(artist_id, artist_name, conn):
    c = conn.cursor()
    q = 'INSERT INTO artists VALUES (' + encode_string(artist_id) + ", " + encode_string(artist_name) + ")"
    if verbose: print q
    c.execute(q)
    c.close()

def update_sim_artists(artist_id, sim_artist_list, conn):
    c = conn.cursor()
    q = 'SELECT end_artist_id FROM sim_artists WHERE start_artist_id = ' + encode_string(artist_id)
    if verbose: print q
    res = c.execute(q)
    existing_sim_artists = res.fetchall()
    existing_sim_artists = set([artist[0] for artist in existing_sim_artists])

    artists_to_add = set()
    for sim_artist in sim_artist_list:
        if sim_artist not in existing_sim_artists:
            artists_to_add.add(sim_artist)

    if not artists_to_add:
        return

    q = 'INSERT INTO sim_artists VALUES (?, ?)'
    for artist in artists_to_add:
        if verbose: print q, artist_id, artist
        c.execute(q, (artist_id, artist))
    c.close()

def save_track(track_id, artist_id, track_year, track_name, conn):
    c = conn.cursor()
    q = 'INSERT INTO tracks VALUES (' + encode_string(track_id) + ', ' + encode_string(artist_id) + ', ' + str(track_year) + ', ' + encode_string(track_name) + ')'
    if verbose: print q
    c.execute(q)
    c.close()

def process_file(trackfile, conn, artists):
    h5 = hdf5_utils.open_h5_file_read(trackfile)

    if GETTERS.get_num_songs(h5) != 1:
        print 'there was a file that had more than one song:', trackfile
        return
    # assert GETTERS.get_num_songs(h5) == 1,'code must be modified if more than one song per .h5 file'

    artist_id = GETTERS.get_artist_id(h5)
    artist_name = GETTERS.get_artist_name(h5)
    if artist_id not in artists:
        save_artist(artist_id, artist_name, conn)
        artists.add(artist_id)

    sim_artist_list = GETTERS.get_similar_artists(h5)
    update_sim_artists(artist_id, sim_artist_list, conn)

    track_id = GETTERS.get_track_id(h5)
    track_year = GETTERS.get_year(h5)
    track_name = GETTERS.get_title(h5)
    save_track(track_id, artist_id, track_year, track_name, conn)

    term_list = GETTERS.get_artist_terms(h5)
    freq_list = GETTERS.get_artist_terms_freq(h5)
    weight_list = GETTERS.get_artist_terms_weight(h5)
    update_terms(artist_id, term_list, freq_list, weight_list, conn)

    h5.close()

def process_all(maindir, conn):
    artists = set()
    numfiles = 0
    # iterate over all files in all subdirectories
    for root, dirs, files in os.walk(maindir):
        # keep the .h5 files
        files = glob.glob(os.path.join(root,'*.h5'))
        for f in files :
            if numfiles % 500 == 0:
                print numfiles, f
                conn.commit()
            numfiles += 1
            process_file(f, conn, artists)

    conn.commit()
    print 'num files:', numfiles
    print 'num artists:', len(artists)


def die_with_usage():
    """ HELP MENU """
    print 'list_all_artists.py'
    print '   by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'usage:'
    print '  python list_all_artists.py <DATASET DIR> output.txt'
    print ''
    print 'This code lets you list all the similar artists for a each artist contained in all'
    print 'subdirectories of a given directory.'
    print 'This script puts the result in a text file, but its main'
    print 'function can be used by other codes.'
    # print 'The txt file format is: (we use <SEP> as separator symbol):'
    # print 'artist Echo Nest ID<SEP>artist Musicbrainz ID<SEP>one track Echo Nest ID<SEP>artist name'
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # Million Song Dataset imports, works under Linux
    # otherwise, put the PythonSrc directory in the PYTHONPATH!
    pythonsrc = os.path.join(sys.argv[0],'../MSDatabaseCode/PythonSrc')
    # pythonsrc = os.path.join(sys.argv[0],'../../../PythonSrc')
    pythonsrc = os.path.abspath( pythonsrc )
    print pythonsrc
    sys.path.append( pythonsrc )
    import hdf5_utils
    import hdf5_getters as GETTERS

    # params
    maindir = sys.argv[1]
    dbfile = sys.argv[2]

    # sanity checks
    if not os.path.isdir(maindir):
        print maindir,'is not a directory'
        sys.exit(0)
    if os.path.isfile(dbfile):
        print 'output file:',dbfile,'exists, please delete or choose new one'
        sys.exit(0)

    # go!
    t1 = time.time()
    create_database(dbfile)

    conn = sqlite3.connect(dbfile)

    process_all(maindir, conn)
    conn.close()

    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print 'time:',stimelength