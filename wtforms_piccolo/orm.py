"""
Form generation utilities for Piccolo ORM Table class.
"""
from __future__ import annotations

import typing as t

from piccolo.columns import Column
from piccolo.table import Table
from wtforms import Form
from wtforms import fields as f
from wtforms import validators
from wtforms.validators import DataRequired


def convert_IntField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.IntegerField:
    """Returns a form field for a Integer column."""
    return f.IntegerField()


def convert_SmallIntField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.IntegerField:
    """Returns a form field for a SmallInt column."""
    return f.IntegerField()


def convert_BigIntField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.IntegerField:
    """Returns a form field for a BigInt column."""
    return f.IntegerField()


def convert_CharField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.StringField:
    """Returns a form field for a Varchar column."""
    d: dict = t.cast(dict, kwargs)
    d["validators"].append(validators.length(max=255))
    return f.StringField(**kwargs)


def convert_TextField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.TextAreaField:
    """Returns a form field for a Text column."""
    return f.TextAreaField(**kwargs)


def convert_UUIDField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.StringField:
    """Returns a form field for a UUID column."""
    d: dict = t.cast(dict, kwargs)
    d["validators"].append(validators.length(max=255))
    return f.StringField(**kwargs)


def convert_BooleanField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.BooleanField:
    """Returns a form field for a Boolean column."""
    return f.BooleanField(**kwargs)


def convert_FloatField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.FloatField:
    """Returns a form field for a Numeric column."""
    return f.FloatField(**kwargs)


def convert_DecimalField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.FloatField:
    """Returns a form field for a Decimal column."""
    return f.FloatField(**kwargs)


def convert_DateTimeField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.DateTimeField:
    """Returns a form field for a Timestamp column."""
    return f.DateTimeField(**kwargs)


def convert_DateField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.DateField:
    """Returns a form field for a Date column."""
    return f.DateField(**kwargs)


def convert_SelectField(
    table: t.Type[Table],
    prop: t.Type[Column],
    kwargs: t.Optional[dict] = None,
) -> f.SelectField:
    """Returns a form field for a FK column."""
    return f.SelectField(**kwargs, coerce=int)


class TableConverter:
    """
    Converts properties from a table class to form fields.
    Default conversions between properties and fields:
    """

    default_converters = {
        "Varchar": convert_CharField,
        "Text": convert_TextField,
        "UUID": convert_UUIDField,
        "Boolean": convert_BooleanField,
        "Serial": convert_IntField,
        "Integer": convert_IntField,
        "SmallInt": convert_IntField,
        "BigInt": convert_IntField,
        "Numeric": convert_FloatField,
        "Decimal": convert_FloatField,
        "Timestamp": convert_DateTimeField,
        "Date": convert_DateField,
        "ForeignKey": convert_SelectField,
    }

    def __init__(self, converters: t.Optional[dict] = None):
        """
        Constructs the converter, setting the converter callables.

        :param converters:
            A dictionary of converter callables for each property type. The
            callable must accept the arguments (table, prop, kwargs).
        """
        self.converters = converters or self.default_converters

    def convert(
        self,
        table: t.Type[Table],
        prop: t.Type[Column],
        field_args: t.Optional[dict] = None,
    ):
        """
        Returns a form field for a single table property.

        :param table:
            The table class that contains the property.
        :param prop:
            The table property: a ``db.column`` instance.
        :param field_args:
            Optional keyword arguments to construct the field.
        """
        prop_type_name = type(prop).__name__
        kwargs: t.Any = {
            "label": prop._meta.name.title(),
            "default": prop._meta.params.get("default"),
            "validators": [],
        }
        if field_args:
            kwargs.update(field_args)

        if prop._meta.required:
            kwargs["validators"].append(DataRequired())

        converter = self.converters.get(prop_type_name, None)
        if converter is not None:
            return converter(table, prop, kwargs)


def table_fields(
    table: t.Type[Table],
    only: t.Optional[t.Iterable[str]] = None,
    exclude: t.Optional[t.Iterable[str]] = None,
    field_args: t.Optional[dict] = None,
    converter: t.Optional[t.Union[dict, TableConverter]] = None,
) -> dict:
    """
    Extracts and returns a dictionary of form fields for a given
    table class.

    :param table:
        The table class to extract fields from.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to a keyword arguments
        used to construct each field object.
    :param converter:
        A converter to generate the fields based on the table properties. If
        not set, TableConverter is used.
    """
    converter = converter or TableConverter()
    field_args = field_args or {}

    # Get the field names we want to include or exclude, starting with the
    # full list of table properties.
    props = {i._meta.name: i for i in table._meta.columns}
    field_names = [prop for prop in props.keys()]

    if only:
        field_names = [f for f in only if f in field_names]

    elif exclude:
        field_names = [f for f in field_names if f not in exclude]

    # Create all fields.
    field_dict = {}
    for name in field_names:
        field = converter.convert(  # type: ignore
            table,
            props[name],  # type: ignore
            field_args.get(name),
        )
        if field is not None:
            field_dict[name] = field
    return field_dict


def table_form(
    table: t.Type[Table],
    base_class=Form,
    only: t.Optional[t.Iterable[str]] = None,
    exclude: t.Optional[t.Iterable[str]] = None,
    field_args: t.Optional[dict] = None,
    converter: t.Optional[t.Union[dict, TableConverter]] = None,
) -> type:
    """
    Creates and returns a dynamic ``wtforms.Form`` class for a given
    table class. The form class can be used as it is or serve as a base
    for extended form classes, which can then mix non-table related fields,
    subforms with other table forms, among other possibilities.

    :param table:
        The table class to generate a form for.
    :param base_class:
        Base form class to extend from. Must be a ``wtforms.Form`` subclass.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to keyword arguments
        used to construct each field object.
    :param converter:
        A converter to generate the fields based on the table properties. If
        not set, TableConverter is used.
    """
    # Extract the fields from the table.
    field_dict = table_fields(table, only, exclude, field_args, converter)

    # Return a dynamically created form class, extending from base_class and
    # including the created fields as properties.
    return type(
        f"{table._meta.tablename.title()}Form", (base_class,), field_dict
    )
