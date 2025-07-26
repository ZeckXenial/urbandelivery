import json
from django.db import connection
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder


class JSONFieldExtended(JSONField):
    """
    Extensión de JSONField con métodos adicionales para manejar campos JSON.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('encoder', DjangoJSONEncoder)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """
        Convierte el valor de Python a un formato adecuado para la base de datos.
        """
        if value is None:
            return None
        return json.dumps(value, cls=self.encoder)

    def from_db_value(self, value, expression, connection):
        """
        Convierte el valor de la base de datos a un objeto Python.
        """
        if value is None:
            return value
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return value

    def get_db_prep_save(self, value, connection):
        """
        Prepara el valor para ser guardado en la base de datos.
        """
        if value is None:
            return value
        return self.get_prep_value(value)


def dictfetchall(cursor):
    ""
    Devuelve todas las filas de un cursor como un diccionario.
    ""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def execute_sql_view(query, params=None):
    ""
    Ejecuta una consulta SQL y devuelve los resultados como una lista de diccionarios.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return dictfetchall(cursor)


class SQLViewMixin:
    ""
    Mixin para modelos que representan vistas SQL.
    """
    @classmethod
    def get_view_name(cls):
        ""
        Devuelve el nombre de la vista SQL.
        Debe ser implementado por las clases hijas.
        """
        raise NotImplementedError(
            'Las clases que usen SQLViewMixin deben implementar get_view_name()'
        )

    @classmethod
    def get_all(cls):
        ""
        Obtiene todos los registros de la vista SQL.
        """
        query = f"SELECT * FROM {cls.get_view_name()}"
        return execute_sql_view(query)

    @classmethod
    def filter(cls, **filters):
        ""
        Filtra los registros de la vista SQL según los criterios especificados.
        """
        if not filters:
            return cls.get_all()
            
        where_clauses = []
        params = []
        
        for field, value in filters.items():
            where_clauses.append(f"{field} = %s")
            params.append(value)
            
        where = " AND ".join(where_clauses)
        query = f"SELECT * FROM {cls.get_view_name()} WHERE {where}"
        
        return execute_sql_view(query, params)

    @classmethod
    def get(cls, **filters):
        ""
        Obtiene un único registro de la vista SQL que coincida con los filtros.
        """
        results = cls.filter(**filters)
        return results[0] if results else None


class JSONFieldMixin:
    ""
    Mixin para modelos con campos JSON que proporciona métodos de utilidad.
    """
    def get_json_value(self, field_name, key, default=None):
        ""
        Obtiene un valor de un campo JSON por su clave.
        """
        json_data = getattr(self, field_name, {}) or {}
        return json_data.get(key, default)

    def set_json_value(self, field_name, key, value):
        ""
        Establece un valor en un campo JSON.
        """
        json_data = getattr(self, field_name, {}) or {}
        json_data[key] = value
        setattr(self, field_name, json_data)
        return self

    def update_json_field(self, field_name, updates):
        ""
        Actualiza múltiples valores en un campo JSON.
        """
        if not updates:
            return self
            
        json_data = getattr(self, field_name, {}) or {}
        json_data.update(updates)
        setattr(self, field_name, json_data)
        return self

    def remove_json_key(self, field_name, key):
        ""
        Elimina una clave de un campo JSON.
        """
        json_data = getattr(self, field_name, {}) or {}
        if key in json_data:
            del json_data[key]
            setattr(self, field_name, json_data)
        return self
