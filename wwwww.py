import psycopg2
from prettytable import PrettyTable

help = '''
    Управление базой данных клиентов.
    ________________________________
    Команды:
    add_c - добавить нового клиента;
    add_p - добавить телефон существующему клиенту;
    сh_сl - изменить данные о клиенте;
    delet_p - удалить телефон из базы данных;
    delet_c - удалить клиента из базы данных;
    find_c - найти клиента по имени, фамилии, email или телефону;
    db_s - показать всю базу данных клиентов;
    help  - показать список команд;
    exit  - выход из программы.
    '''

# Создание базы данных
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS client(
            client_id SERIAL PRIMARY KEY,
            first_name VARCHAR(20) NOT NULL,
            last_name VARCHAR(20) NOT NULL,
            email VARCHAR(30) NOT NULL UNIQUE
            );''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS client_phone(
            id SERIAL PRIMARY KEY,
            client_id INT REFERENCES client(client_id),
            phone BIGINT UNIQUE
            );''')


# Добавление нового клиента
def add_client(conn):
    print('''Введите данные нового клиента.
             Имя, фамилия, email - обязательны.
             Если телефон отсутствует, пропустите запрос.
             --------------------------------------------''')

    first_name = input('Введите имя: ')
    last_name = input('Введите фамилию: ')
    email = input('Введите email: ')
    phone = input('Введите номер телефона: ')
    with conn.cursor() as cur:
        cur.execute(f'''
        INSERT INTO client(first_name, last_name, email)
        VALUES ('{first_name}', '{last_name}', '{email}')
        RETURNING client_id;''')

        client_id = cur.fetchone()[0]

    if phone != '':
        with conn.cursor() as cur:
            cur.execute(f'''
            INSERT INTO client_phone(client_id, phone)
            VALUES ({client_id}, {phone})
            ;''')


# Вывод всех клиентов
def db_show(conn):
    with conn.cursor() as cur:
        cur.execute('''
        SELECT c.client_id, last_name, first_name, email, phone
        FROM client c
        JOIN client_phone cp ON c.client_id = cp.client_id
        ORDER BY last_name
        ;''')
        return_db = cur.fetchall()
        table = PrettyTable(['client_id', 'last_name',
                             'first_name', 'email', 'phone'])
        for i in return_db:
            table.add_row(list(i))
        print(table)


# Выбор id клиента
def choice_id():
    print('Выберите id клиента из таблицы.')
    _ = input('Для вывода таблицы нажмите Enter.')
    db_show(conn)


# Добавить номер телефона клиенту
def add_phone(conn):
    choice_id()
    client_id = input('Введите id клиента: ')
    phone = input('Введите номер телефона: ')
    with conn.cursor() as cur:
        cur.execute(f'''
        INSERT INTO client_phone(client_id, phone)
        VALUES ({int(client_id)}, {int(phone)})
        ;''')

    print(f'Для клиента id-{client_id} добавлен номер {phone}.')


# Изменить данные о клиенте
def change_client(conn):
    choice_id()
    client_id = input('Введите id клиента, для изменения: ')
    first_name = input('Введите имя: ')
    last_name = input('Введите фамилию: ')
    email = input('Введите email: ')
    phone = input('Введите номер телефона: ')
    with conn.cursor() as cur:
        cur.execute('''
        UPDATE client
        SET first_name=%s, last_name=%s, email=%s
        WHERE client_id=%s
        ;''', (first_name, last_name, email, int(client_id)))

    if phone != '':
        with conn.cursor() as cur:
            cur.execute(f'''
            INSERT INTO client_phone(client_id, phone)
            VALUES ({int(client_id)}, {int(phone)})
            ;''')

    print(f'Данные клиента id-{client_id} обновлены.')


# Удалить телефон
def delete_phone(conn):
    choice_id()
    phone = input('Введите телефон, для удаления: ')
    with conn.cursor() as cur:
        cur.execute('''
        DELETE FROM client_phone
        WHERE phone=%s
        ;''', (phone,))

    print(f'Телефон {phone} удалён.')


# Удаление клиента из базы данных
def delete_client(conn):
    choice_id()
    client_id = input('Введите id клиента: ')
    with conn.cursor() as cur:
        cur.execute('''
        SELECT first_name, last_name
        FROM client
        WHERE client_id=%s
        ;''', (int(client_id),))

        info = cur.fetchone()

    with conn.cursor() as cur:
        cur.execute('''
        DELETE FROM client_phone
        WHERE client_id=%s
        ;''', (int(client_id),))

        cur.execute('''
        DELETE FROM client
        WHERE client_id=%s
        ;''', (int(client_id),))

    print(f'Клиент {info[0]} {info[1]} удалён.')


# Поиск клиента
def find_client(conn):
    data = input('Введите имя, фамилию, email или телефон: ')
    if data.isalpha():
        with conn.cursor() as cur:
            cur.execute('''
            SELECT c.client_id, last_name, first_name, email, phone
            FROM client c
            JOIN client_phone cp ON c.client_id = cp.client_id
            WHERE first_name=%s
            OR last_name=%s
            OR email=%s
            ;''', (data, data, data))
            return_db = cur.fetchall()
            table = PrettyTable(['client_id', 'last_name',
                                 'first_name', 'email', 'phone'])
            for i in return_db:
                table.add_row(list(i))
            print(table)
    else:
        with conn.cursor() as cur:
            cur.execute('''
            SELECT c.client_id, last_name, first_name, email, phone
            FROM client c
            JOIN client_phone cp ON c.client_id = cp.client_id
            WHERE phone=%s
            ;''', (data,))
            return_db = cur.fetchall()
            table = PrettyTable(['client_id', 'last_name',
                                 'first_name', 'email', 'phone'])
            for i in return_db:
                table.add_row(list(i))
            print(table)

# Словарь с функциями.
func = {
    'add_c': add_client,
    'add_p': add_phone,
    'ch_cl': change_client,
    'delet_p': delete_phone,
    'delet_c': delete_client,
    'find_c': find_client,
    'db_s': db_show
}

if __name__ == '__main__':
    print(help)
    command = input('Введите команду: ')
    with psycopg2.connect(database="test2", user="postgres", password="05hutopu") as conn:
        create_db(conn)
        conn.commit()
        while command != 'exit':
            if command == 'help':
                print(help)
                command = input('Введите новую команду: ')
            else:
                func[command](conn)
                conn.commit()
                command = input('Введите новую команду: ')

    conn.close()
