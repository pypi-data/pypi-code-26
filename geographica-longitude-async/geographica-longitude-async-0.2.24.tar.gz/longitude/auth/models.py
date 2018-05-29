from longitude.models.sql import SQLCRUDModel


class UserModel(SQLCRUDModel):
    table_name = 'longitude_auth_users'

    select_columns = (
        'id',
        'name',
        'username',
        'email',
    )

    def where_sql(self, params, username=None, password=None, **filters):
        where_clause, params = super().where_sql(params, **filters)

        if username is not None:
            name = self.add_param_name('username', username, params)
            where_clause += ' AND {schema}{table}.username=${name}'.format(
                table=self.table_name,
                schema=self.schema,
                name=name
            )

        if password is not None:
            name = self.add_param_name('password', password, params)
            where_clause += ' AND {schema}{table}.password=${name}'.format(name)

        return where_clause, params


class UserTokenModel(SQLCRUDModel):
    table_name = 'longitude_auth_users_refresh_tokens'

    def where_sql(self, params, auth_user_id=None, **filters):
        where_clause, params = super().where_sql(params, **filters)

        if auth_user_id is not None:
            name = self.add_param_name('auth_user_id', auth_user_id, params)
            where_clause += ' AND {schema}{table}.auth_user_id=${name}'.format(
                table=self.table_name,
                schema=self.schema,
                name=name
            )

        return where_clause, params

    async def upsert(self, values, pk=('auth_user_id',), returning_columns=None):
        return await super().upsert(values, pk=pk, returning_columns=returning_columns)
