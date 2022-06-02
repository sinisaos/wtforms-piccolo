from decimal import Decimal
from unittest import TestCase

from piccolo.columns import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    Serial,
    Text,
    Timestamp,
    Varchar,
)
from piccolo.columns.defaults.date import DateNow
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.table import Table
from wtforms import fields as f

from wtforms_piccolo.orm import table_form


class Author(Table):
    id = Serial(primary_key=True)
    name = Varchar(required=True)


class Book(Table):
    id = Serial(primary_key=True)
    title = Varchar(required=True)
    content = Text(required=True)
    created = Timestamp()
    released = Boolean(default=False)
    released_date = Date()
    price = Numeric(digits=(5, 2))
    rating = Integer(default=0)
    book_author = ForeignKey(references=Author)


class WTFPiccoloTestCase(TestCase):
    def test_input(self):
        BookForm = table_form(Book, only=["title"])

        form = BookForm(title="Book title")
        self.assertEqual(form.data, {"title": "Book title"})

    def test_book_form(self):
        BookForm = table_form(Book)
        form = BookForm()
        self.assertEqual(
            list(form._fields.keys()),
            [
                "id",
                "title",
                "content",
                "created",
                "released",
                "released_date",
                "price",
                "rating",
                "book_author",
            ],
        )
        self.assertEqual(
            form.data,
            {
                "id": None,
                "title": "",
                "content": "",
                "created": TimestampNow(),
                "released": False,
                "released_date": DateNow(),
                "price": Decimal("0"),
                "rating": 0,
                "book_author": None,
            },
        )

    def test_exclude(self):
        BookForm = table_form(Book, exclude=["id", "content", "rating"])

        form = BookForm()
        self.assertEqual(
            list(form._fields.keys()),
            [
                "title",
                "created",
                "released",
                "released_date",
                "price",
                "book_author",
            ],
        )
        self.assertNotEqual(
            list(form._fields.keys()),
            [
                "id",
                "title",
                "content",
                "created",
                "released",
                "released_date",
                "price",
                "book_author",
            ],
        )
        self.assertEqual(
            form.data,
            {
                "title": "",
                "created": TimestampNow(),
                "released": False,
                "released_date": DateNow(),
                "price": Decimal("0"),
                "book_author": None,
            },
        )

    def test_only(self):
        BookForm = table_form(Book, only=["title", "content", "rating"])

        form = BookForm(title="Book1", content="Book1", rating=95)
        self.assertEqual(
            list(form._fields.keys()),
            [
                "title",
                "content",
                "rating",
            ],
        )
        self.assertNotEqual(
            list(form._fields.keys()),
            [
                "id",
                "title",
                "content",
                "created",
                "released",
                "price",
            ],
        )
        self.assertEqual(
            form.data,
            {
                "title": "Book1",
                "content": "Book1",
                "rating": 95,
            },
        )

    def test_new_label_field_args(self):
        BookForm = table_form(
            Book,
            only=["title"],
            field_args={"title": {"label": "Your new label"}},
        )

        form = BookForm()
        for field in form:
            self.assertEqual(field.label.text, "Your new label")
            self.assertNotEqual(field.label.text, "Title")

    def test_field_types(self):
        BookForm = table_form(Book)

        form = BookForm()
        self.assertTrue(isinstance(form.id, f.IntegerField))
        self.assertTrue(isinstance(form.title, f.StringField))
        self.assertTrue(isinstance(form.content, f.TextAreaField))
        self.assertTrue(isinstance(form.created, f.DateTimeField))
        self.assertTrue(isinstance(form.price, f.FloatField))

    def test_validators(self):
        BookForm = table_form(Book)

        form = BookForm(
            id=1,
            title="Book1",
            content="Book1",
            created=TimestampNow(),
            released=False,
            released_date=DateNow(),
            price=10.5,
            rating=95,
            book_author=1,
        )
        form.book_author.choices = [i for i in range(1, 3)]
        self.assertEqual(
            form.data,
            {
                "id": 1,
                "title": "Book1",
                "content": "Book1",
                "created": TimestampNow(),
                "released": False,
                "released_date": DateNow(),
                "price": 10.5,
                "rating": 95,
                "book_author": form.book_author.choices[0],
            },
        )
        self.assertTrue(form.validate())
