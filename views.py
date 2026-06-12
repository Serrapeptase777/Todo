from dataclasses import dataclass
from typing import Callable
import flet as ft
import database as db

# 1. Створюємо чисту модель даних для завдання
@dataclass
class TaskData:
    task_id: int
    task_name: str
    date_text: str
    time_text: str
    is_completed: bool


# 2. Компонент інтерфейсу приймає екземпляр нашого dataclass
class Task(ft.Column):
    def __init__(self, data: TaskData, task_status_change: Callable, task_delete: Callable):
        super().__init__()
        # Зберігаємо dataclass всередині компонента
        self.data = data
        self.task_status_change = task_status_change
        self.task_delete = task_delete

        self.display_task = ft.Checkbox(
            value=self.data.is_completed, 
            label=self.data.task_name, 
            on_change=self.status_changed
        )
        
        self.time_label = ft.Text(size=11, color=ft.colors.GREY_500)
        self.update_time_label_text() 

        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=0,
                    controls=[
                        self.display_task,
                        ft.Container(content=self.time_label, padding=ft.padding.only(left=35))
                    ]
                ),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Редагувати",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE,
                            tooltip="Видалити",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Оновити",
                    on_click=self.save_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def update_time_label_text(self):
        """Оновлює текст мітки часу на основі даних з dataclass."""
        prefix = "Виконано" if self.data.is_completed else "Створено"
        self.time_label.value = f"{prefix}: {self.data.date_text} о {self.data.time_text}"
        self.time_label.style = ft.TextStyle(italic=self.data.is_completed)

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        if self.edit_name.value.strip() == "":
            return
        
        # Оновлюємо в базі та в нашому dataclass
        db.update_task_text(self.data.task_id, self.edit_name.value.strip())
        self.data.task_name = self.edit_name.value.strip()
        
        self.display_task.label = self.data.task_name
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        # Оновлюємо значення в dataclass відповідно до чекбокса
        self.data.is_completed = self.display_task.value
        
        # Оновлюємо базу даних і отримуємо свіжий час зміни статусу
        new_date, new_time = db.update_task_status(self.data.task_id, self.data.is_completed)
        
        # Записуємо нові дати в наш dataclass
        self.data.date_text = new_date
        self.data.time_text = new_time
        
        self.update_time_label_text()
        self.task_status_change(self)

    def delete_clicked(self, e):
        db.delete_task(self.data.task_id)
        self.task_delete(self)


class TodoApp(ft.Column):
    def __init__(self):
        super().__init__()
        self.new_task = ft.TextField(
            hint_text="Що потрібно зробити?",
            on_submit=self.add_clicked, 
            expand=True,
            filled=True,                                  
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,  
            focused_bgcolor=ft.Colors.SURFACE, 
            border_color=ft.Colors.OUTLINE,              
            focused_border_color=ft.Colors.SURFACE,      
            border_radius=ft.border_radius.all(12),       
            content_padding=15
        )
        self.tasks = ft.Column()

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="Всі"), ft.Tab(text="В процесі"), ft.Tab(text="Виконані")],
        )

        self.items_left = ft.Text("0 активних завдань залишилось")
        self.width = 600
        
        self.controls = [
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.icons.ADD, on_click=self.add_clicked
                    ),
                ],
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filter,
                    self.tasks,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.items_left,
                            ft.OutlinedButton(
                                text="Сховати виконані", on_click=self.clear_clicked
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def did_mount(self):
        self.load_tasks_from_db()

    def load_tasks_from_db(self):
        saved_tasks = db.get_all_tasks()
        for row in saved_tasks:
            task_id, text, date_str, time_str, is_completed = row
            
            # Пакуємо сирі дані з БД у красивий dataclass об'єкт
            task_data = TaskData(
                task_id=task_id,
                task_name=text,
                date_text=date_str,
                time_text=time_str,
                is_completed=bool(is_completed)
            )
            
            # Передаємо цей об'єкт у компонент відображення
            task = Task(
                data=task_data,
                task_status_change=self.task_status_change,
                task_delete=self.task_delete
            )
            self.tasks.controls.append(task)
        self.update()

    def add_clicked(self, e):
        if self.new_task.value.strip():
            task_id, date_str, time_str = db.add_task(self.new_task.value.strip())
            
            # Пакуємо дані нового завдання у dataclass
            task_data = TaskData(
                task_id=task_id,
                task_name=self.new_task.value.strip(),
                date_text=date_str,
                time_text=time_str,
                is_completed=False
            )
            
            task = Task(
                data=task_data,
                task_status_change=self.task_status_change,
                task_delete=self.task_delete
            )
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        self.filter.selected_index = 1
        self.update()

    def before_update(self):
        status_index = self.filter.selected_index
        status = "all" if status_index == 0 else "active" if status_index == 1 else "completed"
        
        count = 0
        for task in self.tasks.controls:
            # Звертаємося до внутрішнього dataclass для фільтрації
            task.visible = (
                status == "all"
                or (status == "active" and not task.data.is_completed)
                or (status == "completed" and task.data.is_completed)
            )
            if not task.data.is_completed:
                count += 1
        self.items_left.value = f"{count} активних завдань залишилось"