from home.piccolo_app import APP_CONFIG
from home.tables import Task
from piccolo.apps.user.tables import BaseUser
from piccolo.engine import engine_finder
from piccolo_admin.endpoints import create_admin
from piccolo_api.crud.endpoints import PiccoloCRUD
from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Mount
from starlette.templating import Jinja2Templates
from utils import pagination

from wtforms_piccolo.orm import table_form

templates = Jinja2Templates(directory="home/templates")


app = Starlette(
    routes=[
        Mount(
            "/admin/",
            create_admin(
                tables=APP_CONFIG.table_classes,
                # Required when running under HTTPS:
                # allowed_hosts=['my_site.com']
            ),
        ),
        Mount("/tasks/", PiccoloCRUD(table=Task)),
    ],
)


@app.route("/", methods=["GET"])
async def home(request):
    page_query = pagination.get_page_number(url=request.url)
    count = await Task.count().run()
    paginator = pagination.Pagination(page_query, count)
    tasks = (
        await Task.select(Task.all_columns(), Task.get_readable())
        .limit(paginator.page_size)
        .offset(paginator.offset())
        .order_by(Task.id, ascending=False)
        .run()
    )

    field_name_list = [i._meta.name for i in Task._meta.columns]
    fk_fields = [i._meta.name for i in Task._meta.foreign_key_columns]

    # pagination links in templates
    page_controls = pagination.get_page_controls(
        url=request.url,
        current_page=paginator.current_page(),
        total_pages=paginator.total_pages(),
    )
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "tasks": tasks,
            "table_name": Task._meta.tablename,
            "field_name_list": field_name_list,
            "fk_fields": fk_fields,
            "page_controls": page_controls,
        },
    )


@app.route("/create/", methods=["GET", "POST"])
async def create(request):
    TaskForm = table_form(Task, exclude=["id"])
    users = await BaseUser.select().run()
    data = await request.form()
    form = TaskForm(formdata=data)
    instance = Task()
    # FK select field
    form.task_user.choices = [(i["id"], i["username"]) for i in users]
    if request.method == "POST" and form.validate():
        form.populate_obj(instance)
        await instance.save()
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "create.html",
        {
            "request": request,
            "form": form,
            "table_name": Task._meta.tablename,
        },
    )


@app.route("/{id:int}/edit/", methods=["GET", "POST"])
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


@app.route("/{id:int}/delete/", methods=["GET"])
async def delete(request):
    path_id = request.path_params["id"]
    await Task.delete().where(Task.id == path_id)
    response = RedirectResponse(url="/", status_code=302)
    return response


@app.on_event("startup")
async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


@app.on_event("shutdown")
async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")
