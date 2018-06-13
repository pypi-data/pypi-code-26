from __future__ import absolute_import

from todo.services import Service


class GroupService(Service):
    def initialise_table(self):
        self.cursor.execute(
            '''CREATE TABLE "group"(
                name TEXT PRIMARY KEY NOT NULL,
                in_use BOOLEAN NOT NULL DEFAULT 0
            );'''
        )
        self.cursor.execute('''INSERT INTO "group" (name, in_use) VALUES ('global', 0);''')

    # POST
    def add(self, name):
        self.cursor.execute('INSERT INTO "group" (name) VALUES (?);',
                (name,))
        self.connection.commit()
        return name

    # DELETE
    def delete(self, name):
        self.cursor.execute('DELETE FROM "group" WHERE name = ?;', (name, ))
        self.connection.commit()

    # PUT
    def edit_name(self, name):
        self.cursor.execute('UPDATE "group" SET name = ? WHERE name = ?;', (name, name))
        self.connection.commit()

    def use(self, name):
        self.cursor.execute('UPDATE "group" SET in_use = 0')
        self.cursor.execute('UPDATE "group" SET in_use = 1 WHERE name = ?;', (name,))
        self.connection.commit()

    # GET
    def get(self, name):
        self.cursor.execute('SELECT name FROM "group" WHERE name = ?;', (name, ))
        return self.cursor.fetchone()

    def get_all(self):
        self.cursor.execute(
            """
            SELECT name, todos.items, todos.uncompleted, todos.completed
            FROM "group" LEFT OUTER JOIN (
                SELECT group_name,
                       COUNT(*) as items,
                       SUM(completed = 0) as uncompleted,
                       SUM(completed = 1) as completed
                FROM todo
                GROUP BY group_name
            ) todos ON todos.group_name = name;
            """
        )
        return self.cursor.fetchall()
