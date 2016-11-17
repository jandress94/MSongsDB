from db_utils import *

db_filename = 'D:/artist_full.db'

conn = open_db_conn(db_filename)

artist_list = get_artists(conn)
zero_term_count = 0
for i in range(len(artist_list)):
    if i % 100 == 0: print i, 'out of', len(artist_list)
    if not get_artist_terms(artist_list[i][0], conn):
        zero_term_count += 1
print zero_term_count, len(artist_list)

# artist_list = get_artists(conn, artist_name = 'Red Hot Chili Peppers')
# print [artist[1] for artist in artist_list]
# artist_id = artist_list[0][0]

# print artist_id
# print get_artist_name(artist_id, conn)

# print get_artist_tags(artist_id, conn)
# print get_sim_artists(artist_id, conn)
# print get_artist_tracks(artist_id, conn, limit = 20)

# artists_in_year = get_artist_ids_active_during_year(2000, 0, conn)
# print len(artists_in_year)
# for artist_id in artists_in_year:
    # print artist_id, len(get_artist_terms(artist_id, conn))


# for artist in artists_in_1975:
#     year_range = get_artist_track_year_range(artist, conn)
#     print get_artist_name(artist, conn), year_range
#     if not (year_range[0] <= 1975 and 1975 <= year_range[1]):
#         print 'ERROR, the above year range does not contain 1975'

# print [get_artist_name(aid, conn) for aid in get_artist_ids_active_during_year(1975, 0, conn)]

# print get_artist_track_year_range(artist_id, conn)

# for year in range(1930, 2010):
#     print year, len(get_artist_ids_active_during_year(year, 0, conn))



close_db_conn(conn)