import builtins, sqlite3

def prepare():
    cursor.execute("CREATE TABLE IF NOT EXISTS 'boards' ('name' TEXT NOT NULL, 'info' TEXT NOT NULL, 'board_id' INTEGER NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS 'posts' ('content' TEXT NOT NULL, 'msg_id' INTEGER NOT NULL, 'author_board_id' INTEGER NOT NULL)")
    print("[DATABASE-DEBUG] Created TABLES")

def connect():
    try:
        builtins.sql = sqlite3.connect("rat.db", check_same_thread=False)
        builtins.cursor = sql.cursor()
        prepare()
        print("[DATABASE-DEBUG] Connected!")
    except Exception as e:
        print("[DATABASE-DEBUG] Failed to connect, traceback bellow:")
        print(e)