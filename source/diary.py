import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime



#Первый запуск
def create_table():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('PRAGMA table_info(notes)')
    if c.fetchall() == []:
        c.execute('''CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                time TEXT,
                timestamp INTEGER,
                text TEXT,
                importance INTEGER
                    )''')




        start_time = round(datetime.datetime.timestamp(datetime.datetime.now()))
        start_text = '''Добрый день! Вот как пользоваться нашей программой-ежедневником:
Создание новой задачи: Чтобы добавить новую задачу, просто нажмите на кнопку в левом нижнем углу. После этого станет активной правая панель ввода, где вы можете написать текст своей задачи, а также указать время выполнения.
Просмотр и выбор задач: В левой панели находится список всех ваших текущих записей. Просто дважды щелкните по нужной задаче, чтобы открыть её и прочитать подробности. Можно также использовать функцию поиска сверху для быстрого нахождения задач по времени или тексту.
Редактирование и удаление задач: После открытия задачи в правой панели, вы можете прочитать её содержание и выполнить необходимые действия. Если задача выполнена, просто нажмите кнопку удаления для её удаления из списка.
Мы сделали наш ежедневник максимально удобным для вас, чтобы вы могли легко управлять своими задачами и планировать свое время. Если у вас возникнут вопросы или предложения, не стесняйтесь обращаться к нам!'''


        c.execute('INSERT INTO notes (timestamp, text, time) VALUES (?, ?, ?)',
                       (start_time, start_text, str(datetime.datetime.fromtimestamp(start_time))))
        


        conn.commit()
    conn.close()
    





# Получение заметок из базы данных
def get_notes():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, text FROM notes")
    notes = cursor.fetchall()
    short_notes = {}
    for note in notes:
        short_notes[note[0]] = "[" + str(datetime.datetime.fromtimestamp(note[1])) + "] " + note[2][:50]
    conn.close()
    return notes, short_notes



# Нажатие на кнопку создания заметки
def create_new_note():
    text_field.config(state=tk.NORMAL)
    text_field.delete('1.0', tk.END)
    text_field.config(state=tk.NORMAL)
    save_button.config(state=tk.NORMAL)
    delete_button.config(state=tk.DISABLED)
    new_note_button.config(state=tk.DISABLED)
    date_entry.config(state=tk.NORMAL)
    date_entry.delete('0', tk.END)
    date_entry.insert(0, str(datetime.datetime.now()).split(':')[0] + ':' + str(datetime.datetime.now()).split(':')[1]) 
    text_field.focus_set()


# Сохранение новой заметки
def save_note():
    if text_field.get('1.0', tk.END).strip():
        if date_entry.get():
            try:
                input_datetime = datetime.datetime.strptime(date_entry.get(), '%Y-%m-%d %H:%M')
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты и времени. Используйте формат 'гггг-мм-дд ЧЧ:ММ'.")
                return
            

        #Проверка на существование задачи на такое время
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute("SELECT time FROM notes WHERE time=?", (date_entry.get()+':00',))
            time_check = cursor.fetchone()
            conn.close()
            if time_check:
                messagebox.showerror("Ошибка", "Задача на данное время уже существует")
                return
            
        else:
            input_datetime = datetime.datetime.now()
        

        
        current_time = round(datetime.datetime.timestamp(input_datetime))
        
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (timestamp, text, time) VALUES (?, ?, ?)",
                       (current_time, text_field.get('1.0', tk.END), str(datetime.datetime.fromtimestamp(current_time))))
        conn.commit()
        conn.close()
        update_listbox()
        save_button.config(state=tk.DISABLED)
        new_note_button.config(state=tk.NORMAL)
    else:
        messagebox.showwarning("Пустая заметка", "Нельзя сохранить пустую задачу.")


# Функция для удаления заметки
def delete_note():
    selected_index = listbox.curselection()
    if selected_index:
        result = messagebox.askokcancel("Подтверждение удаления", "Вы уверены, что хотите удалить эту задачу?")
        if result:
            selected_id = notes[selected_index[0]][0]
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id=?", (selected_id,))
            conn.commit()
            conn.close()
            text_field.config(state=tk.NORMAL)
            text_field.delete('1.0', tk.END)
            text_field.config(state=tk.DISABLED)
            listbox.delete(selected_index)
            new_note_button.config(state=tk.NORMAL)
            delete_button.config(state=tk.DISABLED)
            date_entry.config(state=tk.DISABLED)
            update_listbox()



# Чтение полной заметки
def read_full_note():
    selected_index = listbox.curselection()
    search_date = (listbox.get(selected_index).split('[')[1].split(']')[0])
    search_note = listbox.get(selected_index).split('[')[1].split(']')[1]

    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text, time FROM notes WHERE time=?", (search_date,))
    full_note = cursor.fetchall()[0]


    if full_note:
        text_field.config(state=tk.NORMAL)
        text_field.delete('1.0', tk.END)
        text_field.insert(tk.END, full_note[0])
        text_field.config(state=tk.DISABLED)
        delete_button.config(state=tk.NORMAL)
        save_button.config(state=tk.DISABLED)
        new_note_button.config(state=tk.NORMAL)

        date_entry.config(state=tk.NORMAL)
        date_entry.delete('0', tk.END)
        date_entry.insert(0, full_note[1].split(':')[0] + ':' + str(full_note[1]).split(':')[1])
        date_entry.config(state=tk.DISABLED)

    conn.close()


def update_listbox():
    listbox.delete(0, tk.END)
    global notes
    if search_date_entry.get() or search_text_entry.get():
        search_notes()
    else:
        notes, short_notes = get_notes()
        for note in short_notes.values():
            listbox.insert(tk.END, note)
    text_field.config(state=tk.DISABLED)


def search_notes():
    search_date = search_date_entry.get()
    search_text = search_text_entry.get()
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    if search_date and search_text:
        cursor.execute("SELECT id, timestamp, text FROM notes WHERE time LIKE ? AND text LIKE ?", (f"%{search_date}%", f"%{search_text}%"))
    elif search_date:
        cursor.execute("SELECT id, timestamp, text FROM notes WHERE time LIKE ?", (f"%{search_date}%",))
    elif search_text:
        cursor.execute("SELECT id, timestamp, text FROM notes WHERE text LIKE ?", (f"%{search_text}%",))
    else:
        update_listbox()
        conn.close()
        return
    
    searched_notes = cursor.fetchall()
    short_searched_notes = {}
    for note in searched_notes:
        short_searched_notes[note[0]] = "[" + str(datetime.datetime.fromtimestamp(note[1])) + "] " + note[2][:50]
    
    conn.close()
    
    listbox.delete(0, tk.END)
    for note in short_searched_notes.values():
        listbox.insert(tk.END, note)

def menu():
    global notes
    global listbox
    global text_field
    global delete_button
    global save_button
    global new_note_button
    global search_date_entry
    global search_text_entry
    global date_entry

    notes, short_notes = get_notes()

    root = tk.Tk()
    root.title("Ежедневник")
    root.geometry("1024x640")

    search_frame = tk.Frame(root)
    search_frame.pack(side=tk.TOP, padx=10, pady=0, fill=tk.X)

    text_field_label = tk.Label(search_frame, text="Фильтры поиска")
    text_field_label.pack(side=tk.TOP, padx=5, pady=5)

    search_date_label = tk.Label(search_frame, text="Искомое время:")
    search_date_label.pack(side=tk.LEFT)

    search_date_entry = tk.Entry(search_frame)
    search_date_entry.pack(side=tk.LEFT, padx=5)

    search_label = tk.Label(search_frame, text="Текст для поиска:")
    search_label.pack(side=tk.LEFT, padx=(20, 5))

    search_text_entry = tk.Entry(search_frame)
    search_text_entry.pack(side=tk.LEFT, padx=5)

    search_button = tk.Button(search_frame, text="Поиск", command=search_notes)
    search_button.pack(side=tk.LEFT, padx=5)



    listbox_frame = tk.Frame(root)
    listbox_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)

    tasks_label = tk.Label(listbox_frame, text="Текущие задачи:")
    tasks_label.pack(side=tk.TOP, padx=5, pady=0)

    listbox = tk.Listbox(listbox_frame, width=50, height=45)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

    for note in short_notes.values():
        listbox.insert(tk.END, note)

    scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    listbox.bind("<Double-Button-1>", lambda event: read_full_note())




    text_field_frame = tk.Frame(root)
    text_field_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

    text_field_label = tk.Label(text_field_frame, text="Поле ввода:")
    text_field_label.pack(side=tk.TOP, padx=5, pady=0)

    text_field = tk.Text(text_field_frame, width=150, height=45, state=tk.DISABLED)
    text_field.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    date_label = tk.Label(text_field_frame, text="Дата и время задачи (гггг-мм-дд ЧЧ:ММ):")
    date_label.pack(side=tk.TOP, padx=5, pady=5)

    date_entry = tk.Entry(text_field_frame)
    date_entry.pack(side=tk.TOP, padx=5, pady=5)

    scrollbar_text = tk.Scrollbar(text_field, orient=tk.VERTICAL)
    scrollbar_text.config(command=text_field.yview)
    scrollbar_text.pack(side=tk.RIGHT, fill=tk.Y)
    text_field.config(yscrollcommand=scrollbar_text.set)

    new_note_button = tk.Button(text_field_frame, text="Создать новую задачу", command=create_new_note)
    new_note_button.pack(side=tk.LEFT, padx=5, pady=5)

    save_button = tk.Button(text_field_frame, text="Сохранить", command=save_note, state=tk.DISABLED)
    save_button.pack(side=tk.RIGHT, padx=5, pady=5)

    delete_button = tk.Button(text_field_frame, text="Удалить", command=delete_note, state=tk.DISABLED)
    delete_button.pack(side=tk.RIGHT, padx=5, pady=5)
    

    root.mainloop()


create_table()
menu()
