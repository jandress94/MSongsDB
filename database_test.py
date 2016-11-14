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


def die_with_usage():
    """ HELP MENU """
    print 'list_all_artists.py'
    print '   by T. Bertin-Mahieux (2010) Columbia University'
    print ''
    print 'usage:'
    print '  python list_all_artists.py databaseFile'
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
    if len(sys.argv) < 2:
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
    dbfile = sys.argv[1]

    # sanity checks

    conn = sqlite3.connect(dbfile)

    q = 'SELECT COUNT(*) FROM artists'
    c = conn.cursor()
    res = c.execute(q)
    result = res.fetchone()
    print result

    conn.close()