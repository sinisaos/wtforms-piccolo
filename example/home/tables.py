from piccolo.apps.user.tables import BaseUser
from piccolo.columns import Boolean, ForeignKey, Integer, Text, Varchar
from piccolo.columns.readable import Readable
from piccolo.table import Table


class Task(Table):
    """
    An example table.
    """

    name = Varchar(required=True, null=False)
    description = Text(required=True, null=False)
    views = Integer(default=0, null=False)
    completed = Boolean(default=True)
    task_user = ForeignKey(references=BaseUser)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s", columns=[cls.task_user.username])
