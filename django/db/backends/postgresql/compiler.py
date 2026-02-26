from django.db.models.sql import compiler


class SQLCompiler(compiler.SQLCompiler):
    def quote_name_unless_alias(self, name):
        if '$' in name:
            raise ValueError(
                'Dollar signs are not permitted in column aliases on PostgreSQL.'
            )
        return super().quote_name_unless_alias(name)


class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):
    pass


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    pass


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass
