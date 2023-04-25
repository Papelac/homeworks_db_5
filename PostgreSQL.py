import psycopg2

def create_table(cur):
    cur.execute("""
                CREATE TABLE IF NOT EXISTS client(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) NOT null,
                    last_name VARCHAR(50) NOT null,
                    email VARCHAR(100) NOT null
                );
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS client_phone(
                    id SERIAL PRIMARY KEY,
                    phone VARCHAR(50) NOT null,
                    client_id INTEGER NOT NULL REFERENCES client(id)
                );
                """)
    
def add_client(cur, first_name, last_name, email, phone = None):
    cur.execute("""
                INSERT INTO client(first_name, last_name, email) VALUES(%s, %s, %s);
                """, (first_name, last_name, email))
    cur.execute("""
                SELECT id FROM client WHERE first_name=%s and last_name=%s and email=%s;
                """, (first_name, last_name, email))
    client_id = cur.fetchone()[0]
    if phone is not None:
        add_phone(cur, client_id, phone)

def add_phone(cur, client_id, phone):
    cur.execute("""
                INSERT INTO client_phone(phone, client_id) VALUES(%s, %s)
                """, (phone, client_id))

def change_client(cur, client_id, first_name = None, last_name = None, email = None, old_phone = None, new_phone = None):
    if first_name is not None:
        cur.execute("""
                UPDATE client SET first_name=%s WHERE id=%s;
                """, (first_name, client_id))
    if last_name is not None:
        cur.execute("""
                UPDATE client SET last_name=%s WHERE id=%s;
                """, (last_name, client_id))
    if email is not None:
        cur.execute("""
                UPDATE client SET email=%s WHERE id=%s;
                """, (email, client_id))
    if old_phone is not None and new_phone is not None:
        cur.execute("""
                UPDATE client_phone SET phone=%s WHERE id=%s and phone=%s;
                """, (new_phone, client_id, old_phone))
    elif new_phone is not None:
        add_phone(cur, client_id, new_phone)

def del_phone(cur, client_id, phone):
    cur.execute("""
                DELETE FROM client_phone WHERE phone=%s and client_id=%s;
                """, (phone, client_id))

def del_client(cur, client_id):
    cur.execute("""
                DELETE FROM client_phone WHERE client_id=%s;
                DELETE FROM client WHERE id=%s;
                """, (client_id, client_id))

def find_client(cur, first_name = None, last_name = None, email = None, phone = None):
    text_request = ''

    if phone is not None:
       text_request = "SELECT c.*, cp.phone FROM client as c LEFT JOIN client_phone cp ON cp.client_id = c.id WHERE cp.phone ='" + phone + "'"
 
    if first_name is not None:
        if text_request != '':
            text_request = text_request + " OR c.first_name='" + first_name + "'"
        else:
           text_request = "SELECT * FROM client WHERE first_name='" + first_name + "'"

    if last_name is not None:
        if text_request != '':
            text_request = text_request + " OR c.last_name='" + last_name + "'"
        else:
           text_request = "SELECT * FROM client WHERE last_name='" + last_name + "'"

    if email is not None:
        if text_request != '':
            text_request = text_request + " OR c.email='" + email + "'"
        else:
           text_request = "SELECT * FROM client WHERE email='" + email + "'"

    cur.execute(text_request)
    return cur.fetchall()

conn = psycopg2.connect(database='Test_DB', user='postgres', password='postgres')

with conn.cursor() as cur:
    create_table(cur)
    add_client(cur, 'Ivan', 'Ivanov', 'test1@mail.ru', '+7(910) 111 11 11')
    add_client(cur, 'Petr', 'Petrov', 'test2@mail.ru', '+7(910) 222 22 22')
    add_client(cur, 'Anton', 'Antonov', 'test3@mail.ru', '+7(910) 333 33 33')
    add_client(cur, 'Vasya', 'Vasilenko', 'test@mail.ru')
    add_phone(cur, 2, '+7(910) 222 22 23')
    change_client(cur, 2, first_name = 'Pavel', old_phone = '+7(910) 222 22 23', new_phone = '+7(910) 222 22 24')
    del_phone(cur, 2, '+7(910) 222 22 25')
    del_client(cur, 4)
    client_id = find_client(cur, first_name = 'Ivan', phone = '+7(910) 222 22 22')
    print('client', client_id)
    
    conn.commit()
    
    #cur.execute("Drop TABLE Client_phone")
    #cur.execute("Drop TABLE Client")
    #conn.commit()

conn.close()

