# Добавление нового клиента
def add_client(cur):
    print('''Введите данные нового клиента.
             Имя, фамилия и email - обязательные данные.
             Если телефона нет, пропустите данный запрос.
             --------------------------------------------''')

    first_name = input('Введите имя: ')
    last_name = input('Введите фамилию: ')
    email = input('Введите email: ')
    phone = input('Введите номер телефона: ')
    cur.execute(f'''
        INSERT INTO client(first_name, last_name, email)
        VALUES ('{first_name}', '{last_name}', '{email}')
        RETURNING client_id;''')

    client_id = cur.fetchone()[0]

    if phone != '':
            cur.execute(f'''
            INSERT INTO client_phone(client_id, phone)
            VALUES ({client_id}, {phone})
            ;''')


# Вывод всех клиентов
def db_show(cur):
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
    _ = input('Для вывода таблицы нажмите клавишу Enter.')
    db_show(conn)


# Добавить номер телефона клиенту
def add_phone(cur):
    choice_id()
    client_id = input('Введите id клиента: ')
    phone = input('Введите номер телефона: ')
    cur.execute(f'''
        INSERT INTO client_phone(client_id, phone)
        VALUES ({int(client_id)}, {int(phone)})
        ;''')

    print(f'Для клиента id-{client_id} добавлен номер {phone}.')


# Изменить данные о клиенте
def change_client(cur):
    choice_id()
    client_id = input('Введите id клиента, данные которого хотите изменить: ')
    first_name = input('Введите имя: ')
    last_name = input('Введите фамилию: ')
    email = input('Введите email: ')
    phone = input('Введите номер телефона: ')
    cur.execute('''
        UPDATE client
        SET first_name=%s, last_name=%s, email=%s
        WHERE client_id=%s
        ;''', (first_name, last_name, email, int(client_id)))

    if phone != '':
        cur.execute(f'''
            INSERT INTO client_phone(client_id, phone)
            VALUES ({int(client_id)}, {int(phone)})
            ;''')

    print(f'Данные для клиента id-{client_id} обновлены.')


# Удалить телефон
def delete_phone(cur):
    choice_id()
    phone = input('Введите телефон, который хотите удалить: ')
    cur.execute('''
        DELETE FROM client_phone
        WHERE phone=%s
        ;''', (phone,))

    print('Телефон {phone} удалён из базы данных.')


# Удаление клиента из базы данных
def delete_client(cur):
    choice_id()
    client_id = input('Введите id клиента: ')
    cur.execute('''
        SELECT first_name, last_name
        FROM client
        WHERE client_id=%s
        ;''', (int(client_id),))

    info = cur.fetchone()

    cur.execute('''
        DELETE FROM client_phone
        WHERE client_id=%s
        ;''', (int(client_id),))

    cur.execute('''
        DELETE FROM client
        WHERE client_id=%s
        ;''', (int(client_id),))

    print(f'Клиент {info[0]} {info[1]} удалён из базы данных.')


# Поиск клиента
def find_client(cur):
    data = input('Введите имя, фамилию, email или телефон: ')
    if data.isalpha():
        cur.execute('''
            SELECT c.client_id, last_name, first_name, email, phone
            FROM client c
            JOIN client_phone cp ON c.client_id = cp.client_id
            WHERE first_name=%s
            AND last_name=%s
            AND email=%s
            ;''', (data, data, data))
        return_db = cur.fetchall()
        table = PrettyTable(['client_id', 'last_name',
                                 'first_name', 'email', 'phone'])
        for i in return_db:
            table.add_row(list(i))
        print(table)
    else:
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
        while command != 'exit':
            if command == 'help':
                print(help)
                command = input('Введите новую команду: ')
            else:
                func[command](conn)
                command = input('Введите новую команду: ')
with conn.cursor() as cur:
    conn.close()
