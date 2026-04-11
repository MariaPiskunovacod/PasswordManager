import tkinter as tk
import sys
import os

#переходим в папку с программой
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from gui import PasswordManagerGUI

def main():
    try:
        #cоздаем главное окно
        root = tk.Tk()
        
        #eстанавливаем иконку (если есть)
        try:
            root.iconbitmap(default='icon.ico')
        except:
            pass
        
        #запускаем приложение
        app = PasswordManagerGUI(root)
        
        #обработчик закрытия окна
        def on_closing():
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        #запускаем главный цикл
        root.mainloop()
        
    except Exception as e:
        #отслеживаем все ошибки
        tk.messagebox.showerror(
            "Критическая ошибка",
            f"Произошла непредвиденная ошибка:\n{e}\n\n"
            "Приложение будет закрыто."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
