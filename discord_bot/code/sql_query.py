PLAYLIST_QUERY = '''SELECT name FROM songs 
        WHERE playlist_id = (SELECT id FROM playlist WHERE (name=? AND 
        user_id=(SELECT id FROM users WHERE user_id = ?)))'''
