import flet as ft
import database as db
from views import TodoApp

def main(page: ft.Page):
    # Ініціалізація бази даних
    db.init_db()

    page.title = "Todo"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    # Початкова тема
    page.theme_mode = ft.ThemeMode.DARK

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_button.icon = ft.Icons.DARK_MODE
        else:
            page.theme_mode = ft.ThemeMode.DARK
            theme_button.icon = ft.Icons.LIGHT_MODE
        page.update()

    theme_button = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE, 
        on_click=toggle_theme,
        tooltip="Змінити тему сайту"
    )

    page.appbar = ft.AppBar(
        title=ft.Text("Мої завдання"),
        center_title=True,
        actions=[theme_button],
        bgcolor=ft.Colors.SURFACE,
    )

    page.add(TodoApp())

if __name__ == "__main__":
    ft.app(target=main,view=ft.AppView.WEB_BROWSER)