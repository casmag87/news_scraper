import psycopg2


def get_connection():
    return psycopg2.connect("""
    host = 'localhost'
    port = '5432'
    user = ''
    dbname= ''
    password = ''
    """)



def insert_articles(title, opening, img_url,published,author,main_section,created_on,modified_on):
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("""
            INSERT INTO articles (title,opening,img_url,published,author,main_section,created_on,modified_on)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, [title,opening,img_url,published,author,main_section,created_on,modified_on])

def insert_logs(message, created_on):
    connection = get_connection()
    try:
        with connection.cursor() as cur:
            cur.execute("""
            INSERT INTO logs (message, created_on)
            VALUES (%s, %s);
            """, (message, created_on))
        connection.commit()
    finally:
        connection.close()

