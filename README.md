Server-side form generation utilities for Piccolo ORM Table class.
Based on the code found in [wtforms.ext](https://wtforms.readthedocs.io/en/2.3.x/ext/) and provides a bridge between Piccolo ORM tables and WTForms. 

# Installation 

```bash
pip install wtforms-piccolo
```
# Usage

Example usage:

```python
# table.py
from piccolo.apps.user.tables import BaseUser
from piccolo.columns import Boolean, ForeignKey, Integer, Text, Varchar
from piccolo.table import Table


class Task(Table):
    """
    An example table.
    """

    name = Varchar(required=True, null=False)
    description = Text(required=True, null=False)
    views = Integer(required=True, null=False, default=0)
    completed = Boolean(default=False)
    task_user = ForeignKey(references=BaseUser)
```

Generate a form based on the table.

```shell
TaskForm = table_form(Task)
```

Generate a form based on the table, excluding 'id' and 'views'.

```shell
TaskForm = table_form(Task, exclude=['id', 'views'])
```
Generate a form based on the table, only including 'name' and 'description'.

```shell
TaskForm = table_form(Task, only=['name', 'description'])
```
The form can be generated setting field arguments:

```python
TaskForm = table_form(Task, only=['name', 'description'], field_args={
    'name': {
        'label': 'Your new label',
    },
    'description': {
        'label': 'Your new label',
    }
})
```
Example implementation for an edit view using Starlette web app:

```python
# app.py
# other imports
from wtforms_piccolo.orm import table_form

@app.route("/{id:int}/", methods=["GET", "POST"])
async def edit(request):
    path_id = request.path_params["id"]
    item = await Task.objects().get(Task.id == path_id).run()
    users = await BaseUser.select().run()
    data = await request.form()
    TaskForm = table_form(Task, exclude=["id"])
    form = TaskForm(obj=item, formdata=data)
    # FK select field
    form.task_user.choices = [(i["id"], i["username"]) for i in users]
    if request.method == "POST" and form.validate():
        form.populate_obj(item)
        await item.save().run()
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "form": form,
            "table_name": Task._meta.tablename,
        },
    )
```

Example template for above view using Jinja and Bootstrap:

```html
{% extends "base.html" %}
{% block content %}
<main role="main">
    <br><br>
    <div class="container">
        <h2>Edit Task</h2>
        <br>
        <form method="POST">
            {% for field in form %}
            <div class="form-group">
                {{ field.label }}:
                {{ field(class="form-control") }}
                {% for error in field.errors %}
                <span style="color: red;">*{{ error }}</span>
                {% endfor %}
            </div>
            {% endfor %}
            <p><input class="btn btn-primary" type="submit" value="Submit"></p>
        </form>
    </div> <!-- /container -->
    <hr>
</main>
{% endblock %}
```

The full example of the Starlette web application is in example folder.