import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import sqlite3
import datetime

class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.init_main()
        self.db = db
        self.view_records()

    def init_main(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.fileMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Инфо", menu=self.fileMenu)
        self.fileMenu.add_command(label="Справка", command=self.open_reference)

        self.add_img = tk.PhotoImage(file='add.gif')
        btn_open_dialog = tk.Button(toolbar, text='Добавить устройство', command=self.open_dialog, bg='#d7d8e0', bd=0,
                                    compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        self.edit_img = tk.PhotoImage(file='update.gif')
        btn_edit_dialog = tk.Button(toolbar, text='Редактировать', bg='#d7d8e0', bd=0, image=self.edit_img,
                                    compound=tk.TOP, padx=10, command=self.open_update)
        btn_edit_dialog.pack(side=tk.LEFT)

        self.delete_img = tk.PhotoImage(file='delete.gif')
        btn_delete = tk.Button(toolbar, text='Удалить устройство', bg='#d7d8e0', bd=0, image=self.delete_img,
                               compound=tk.TOP, padx=10, command=self.open_delete_dialog)
        btn_delete.pack(side=tk.LEFT)

        self.logbook_img = tk.PhotoImage(file='logbook.gif')
        btn_logbook = tk.Button(toolbar, text='Журнал событий', bg='#d7d8e0', bd=0, image=self.logbook_img,
                               compound=tk.TOP, padx=10, command=self.open_logbook)
        btn_logbook.pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self, columns=('ID', 'Parent_ID', 'Type', 'Name', 'Model', 'IP', 'Mask', 'Gateway'),
                                  height=30, selectmode='extended')

        self.scrollbar = tk.Scrollbar(self)
        self.tree.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.column("#0", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("ID", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("Parent_ID", width=180, minwidth=180, stretch=tk.NO)
        self.tree.column("Type", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("Name", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("Model", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("IP", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("Mask", width=150, minwidth=150, stretch=tk.NO)
        self.tree.column("Gateway", width=150, minwidth=150, stretch=tk.NO)

        self.tree.heading("#0", text="Утройства", anchor=tk.W)
        self.tree.heading("ID", text="ID устройства", anchor=tk.W)
        self.tree.heading("Parent_ID", text="ID родительского устройства", anchor=tk.W)
        self.tree.heading("Type", text="Тип устройства", anchor=tk.W)
        self.tree.heading("Name", text="Название", anchor=tk.W)
        self.tree.heading("Model", text="Модель", anchor=tk.W)
        self.tree.heading("IP", text="IP адресс", anchor=tk.W)
        self.tree.heading("Mask", text="Маска подсети", anchor=tk.W)
        self.tree.heading("Gateway", text="Шлюз", anchor=tk.W)

        self.tree.pack(expand=True, fill=tk.BOTH)

    def records(self, id, parent_id, type, name, model, ip, mask, gateway, val_ip, val_m, val_g):
        if val_ip != True:
            mb.showerror('Ошибка', 'Неверный формат IP адреса')
        elif val_m != True:
            mb.showerror('Ошибка', 'Неверный формат маски подсети')
        elif val_g != True:
            mb.showerror('Ошибка', 'Неверный формат шлюза по умолчанию')
        else:
            self.db.insert_data(id, parent_id, type, name, model, ip, mask, gateway)
            self.view_records()

    def update_records(self, id, parent_id, type, name, model, ip, mask, gateway, v_ip, v_m, v_g):
        if v_ip != True:
            mb.showerror('Ошибка', 'Неверный формат IP адреса')
        elif v_m != True:
            mb.showerror('Ошибка', 'Неверный формат маски подсети')
        elif v_g != True:
            mb.showerror('Ошибка', 'Неверный формат шлюза по умолчанию')
        else:
            try:
                self.db.c.execute('''UPDATE Devices SET ID=?, Parent_ID=?, Type=?, Name=?, Model=?, IP=?, Mask=?, 
                Gateway=? WHERE ID=?''',
                                  (id, parent_id, type, name, model, ip, mask, gateway,
                                   self.tree.set(self.tree.selection()[0], '#1')))
                self.db.conn.commit()
                self.view_records()
            except:
                mb.showerror('Ошибка', 'Проверьте корректность вводимых данных')

    def view_records(self):
        dic = {'Маршрутизатор': 'id1', 'Коммутатор': 'id2', 'Сервер': 'id3', 'Компьютер': 'id4', 'МФУ': 'id5'}
        [self.tree.delete(i) for i in self.tree.get_children()]
        for device in dic:
            self.db.c.execute('''SELECT * FROM Devices WHERE Type = "{0}"'''.format(device))
            dic[device] = self.tree.insert("", "end", dic[device], text=device, open=True)
            [self.tree.insert(dic[device], 'end', values=row) for row in self.db.c.fetchall()]

    def delete_records(self):
        for selection_item in self.tree.selection():
            self.db.c.execute('''DELETE FROM Devices WHERE ID=?''', (self.tree.set(selection_item, '#1'),))
        self.db.conn.commit()
        self.view_records()

    def open_delete_dialog(self):
        if mb.askyesno('Подтверждение', 'Вы уверены, что хотите удалить запись?'):
            self.delete_records()

    def open_update(self):
        Update()

    def open_logbook(self):
        Logbook(t=True)

    def open_dialog(self):
        Device()

    def open_reference(self):
        Reference()

class Reference(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_reference()

    def init_reference(self):
        self.geometry("700x400+400+300")
        self.resizable(False, False)
        lbl = tk.Label(self,
                       text='Здравствуй, дорогой пользователь!'
                            '\n\nДля того чтобы добавить устройство, нажмите на кнпоку "Добавить устройство" в верхней '
                            'панели главного окна,'
                            '\nвведите необходимые данные в соответсвующие поля, предварительно выбрав тип устройства '
                            'из списка'
                            '\nзатем нажмите кнопку "Добавить".'
                            '\n\nДля того чтобы обновить информацию об устройстве, сначала нажмите на строку с '
                            'устройством, затем нажмите на'
                            '\nкнопку "Редактировать" в верхней панели главного окна, совершите все изменения и нажмите'
                            ' на кнопку'
                            '\n"Редактировать".'
                            '\n\nДля того чтобы удалить одно или несколько устройств, нажмите на строку с устройством, '
                            'затем нажмите на'
                            '\nкнопку "Удалить устройство". В окне с подтверждением нажмите "Да"'
                            '\n\nПримечание: Чтобы удалить сразу несколько устройств выберите их с зажатой на '
                            'клавиатуре клавишей "Ctrl".'
                            '\n\nВнимание!'
                            '\nПри заполнении текстовых полей в окнах "Добавить устройство" и "Редактировать '
                            'устройство" следует соблюдать'
                            '\nнекоторые правила ввода:'
                            '\n\t1) ID устройств не могут повторяться'
                            '\n\t2) Названия устройств не могут повторяться'
                            '\n\t3) IP адреса устройств не могут повторяться'
                            '\n\t4) IP адрес и шлюз устройства должны быть введены в следующем формате: х.х.х.х,'
                            '\n\tгде x - число от 0 до 255',
                       justify=tk.LEFT,
                       font=("Arial Bold", 10))
        lbl.pack()
        btn = ttk.Button(self, text='Ок', command=self.destroy)
        btn.pack()

class Device(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_device()
        self.view = app

    def init_device(self):
        self.title('Добавить устройство')
        self.geometry('400x300+400+300')
        self.resizable(False, False)

        label_id = tk.Label(self, text='Тип устройства:')
        label_id.place(x=50, y=20)
        label_id = tk.Label(self, text='Номер:')
        label_id.place(x=50, y=50)
        label_parent = tk.Label(self, text='Подключен к устройству:')
        label_parent.place(x=50, y=80)
        label_name = tk.Label(self, text='Имя:')
        label_name.place(x=50, y=110)
        label_model = tk.Label(self, text='Модель:')
        label_model.place(x=50, y=140)
        label_ip = tk.Label(self, text='IP:')
        label_ip.place(x=50, y=170)
        label_mask = tk.Label(self, text='Маска:')
        label_mask.place(x=50, y=200)
        label_gateway = tk.Label(self, text='Шлюз:')
        label_gateway.place(x=50, y=230)

        self.combobox = ttk.Combobox(self, values=[u'Маршрутизатор', u'Коммутатор', u'Сервер', u'Компьютер', u'МФУ'],
                                     state='readonly')
        self.combobox.current(0)
        self.combobox.place(x=200, y=20)
        self.entry_id = ttk.Entry(self)
        self.entry_id.place(x=200, y=50)
        self.entry_parent = ttk.Entry(self)
        self.entry_parent.place(x=200, y=80)
        self.entry_name = ttk.Entry(self)
        self.entry_name.place(x=200, y=110)
        self.entry_model = ttk.Entry(self)
        self.entry_model.place(x=200, y=140)
        self.entry_ip = ttk.Entry(self)
        self.entry_ip.place(x=200, y=170)
        self.entry_mask = ttk.Entry(self)
        self.entry_mask.place(x=200, y=200)
        self.entry_gateway = ttk.Entry(self)
        self.entry_gateway.place(x=200, y=230)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=300, y=260)

        self.btn_add = ttk.Button(self, text='Добавить')
        self.btn_add.place(x=220, y=260)

        self.btn_add.bind('<Button-1>', lambda event: self.view.records(self.entry_id.get(),
                                                                        self.entry_parent.get(),
                                                                        self.combobox.get(),
                                                                        self.entry_name.get(),
                                                                        self.entry_model.get(),
                                                                        self.entry_ip.get(),
                                                                        self.entry_mask.get(),
                                                                        self.entry_gateway.get(),
                                                                        self.validate_address(self.entry_ip.get()),
                                                                        self.validate_mask(self.entry_mask.get()),
                                                                        self.validate_address(self.entry_gateway.get())))


        self.grab_set()
        self.focus_set()

    def validate_address(self, s):
        a = s.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    def validate_mask(self, mask):
        a = mask.split('.')
        dic = {255, 254, 252, 248, 240, 224, 192, 128, 0}
        if len(a) != 4:
            return False
        if int(a[0]) == 255:
            last_i = 255
            b = True
            for x in range(1, 4):
                if a[x].isdigit() and (int(a[x]) in dic) and (int(a[x]) <= last_i):
                    i = int(a[x])
                    if b is True and last_i == 255 and i != 255:
                        b = False
                    elif last_i != 255 and i != 255 and i != 0:
                        return False
                    last_i = i
                else:
                    return False
            return True
        else:
            for i in range(1, 4):
                if int(a[i]) != 0:
                    return False
                else:
                    return True

class Logbook(tk.Toplevel):
    def __init__(self, t):
        if t:
            super().__init__()
            self.init_logbook()
            self.view = app
            self.db = DB()
            self.view_notes()
        else:
            self.db = DB()

    def init_logbook(self):
        self.title('Журнал событий')
        self.geometry('750x400+400+300')
        self.resizable(False, False)

        btn_delete = ttk.Button(self, text='Очистить журнал', command=self.open_delete_dialog)
        btn_delete.pack(fill=tk.X)

        self.tree1 = ttk.Treeview(self, columns=('ID', 'Old_Parent_ID', 'New_Parent_ID', 'DateTime'), height=25,
                                  show='headings', selectmode="extended")

        self.scrollbar = tk.Scrollbar(self)
        self.tree1.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tree1.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree1.column("ID", width=100, stretch=tk.NO)
        self.tree1.column("Old_Parent_ID", width=250, minwidth=250, stretch=tk.NO)
        self.tree1.column("New_Parent_ID", width=250, minwidth=250, stretch=tk.NO)
        self.tree1.column("DateTime", width=150, minwidth=150, stretch=tk.NO)

        self.tree1.heading("ID", text="ID устройства")
        self.tree1.heading("Old_Parent_ID", text="ID старого родительского устройства")
        self.tree1.heading("New_Parent_ID", text="ID нового родительского устройства")
        self.tree1.heading("DateTime", text="Время изменения")

        self.tree1.pack()

        self.grab_set()
        self.focus_set()

    def delete_notes(self):
        self.db.c.execute('''DELETE FROM Logbook''')
        self.db.c.execute('''UPDATE sqlite_sequence SET seq=0 WHERE Name="Logbook"''')
        self.db.conn.commit()
        self.view_notes()

    def open_delete_dialog(self):
        if mb.askyesno('Подтверждение', 'Вы уверены, что хотите очистить журнал?'):
            self.delete_notes()

    def notes(self, id, old_parent_id, new_parent_id, datetime, t1):
        self.db.insert_note(id, old_parent_id, new_parent_id, datetime)
        if t1:
            self.view_notes()

    def view_notes(self):
        self.db.c.execute('''SELECT Device_ID, Old_Parent_ID, New_Parent_ID, Datetime FROM Logbook''')
        [self.tree1.delete(i) for i in self.tree1.get_children()]
        [self.tree1.insert('', 'end', values=row) for row in self.db.c.fetchall()]

class Update(Device):
    def __init__(self):
        super().__init__()
        self.init_edit()
        self.view = app
        self.db = db
        self.log = log
        self.default_data()

    def init_edit(self):
        self.title('Редактировать устройство')
        btn_edit = ttk.Button(self, text='Редактировать')
        btn_edit.place(x=200, y=260)
        btn_edit.bind('<Button-1>', lambda event: self.check_difference())
        btn_edit.bind('<Button-1>', lambda event: self.view.update_records(self.entry_id.get(),
                                                                           self.entry_parent.get(),
                                                                           self.combobox.get(),
                                                                           self.entry_name.get(),
                                                                           self.entry_model.get(),
                                                                           self.entry_ip.get(),
                                                                           self.entry_mask.get(),
                                                                           self.entry_gateway.get(),
                                                                           self.validate_address(self.entry_ip.get()),
                                                                           self.validate_mask(self.entry_mask.get()),
                                                                           self.validate_address(self.entry_gateway.get())),
                                                                           add="+")

        self.btn_add.destroy()

    def default_data(self):
        self.db.c.execute('''SELECT * FROM Devices WHERE ID=?''',
                          (self.view.tree.set(self.view.tree.selection()[0], '#1'),))
        row = self.db.c.fetchone()
        dic = {0: 'Маршрутизатор', 1: 'Коммутатор', 2: 'Сервер', 3: 'Компьютер', 4: 'МФУ'}
        for i in range(5):
            if row[2] == dic.get(i):
                self.combobox.current(i)
                break
        self.entry_id.insert(0, row[0])
        self.entry_parent.insert(0, row[1])
        self.old_parent_id = self.entry_parent.get()
        self.entry_name.insert(0, row[3])
        self.entry_model.insert(0, row[4])
        self.entry_ip.insert(0, row[5])
        self.entry_mask.insert(0, row[6])
        self.entry_gateway.insert(0, row[7])

    def get_time(self):
        datetime_now = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
        return datetime_now

    def check_difference(self):
        if self.entry_parent.get() != self.old_parent_id:
            self.log.notes(Logbook(t=False), self.entry_id.get(), self.old_parent_id, self.entry_parent.get(),
                           self.get_time(), t1=False)


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('network_directory.db')
        self.c = self.conn.cursor()
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS Devices (ID INTEGER PRIMARY KEY, Parent_ID INTEGER, Type TEXT, 
            Name TEXT UNIQUE, Model TEXT, IP TEXT UNIQUE, Mask TEXT, Gateway TEXT)''')
        self.conn.commit()
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS Logbook (ID INTEGER PRIMARY KEY AUTOINCREMENT, Device_ID INTEGER, 
            Old_Parent_ID INTEGER, New_Parent_ID INTEGER, Datetime TEXT)''')
        self.conn.commit()


    def insert_data(self, id, parent_id, type, name, model, ip, mask, gateway):
        try:
            self.c.execute('''INSERT INTO Devices(ID, Parent_ID, Type, Name, Model, IP, Mask, Gateway) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (id, parent_id, type, name, model, ip, mask, gateway))
            self.conn.commit()
        except sqlite3.IntegrityError:
            mb.showerror('Ошибка', 'Проверьте корректность вводимых данных')

    def insert_note(self, id, old_parent_id, new_parent_id, datetime):
        try:
            self.c.execute('''INSERT INTO Logbook(Device_ID, Old_Parent_ID, New_Parent_ID, Datetime) 
            VALUES (?, ?, ?, ?)''',
                           (id, old_parent_id, new_parent_id, datetime))
            self.conn.commit()
        except sqlite3.IntegrityError:
            mb.showerror('Ошибка', 'Проверьте корректность вводимых данных')

if __name__ == "__main__":
    root = tk.Tk()
    db = DB()
    app = Main(root)
    log = Logbook
    app.pack()
    root.title("Network directory")
    root.geometry("1400x650+80+100")
    root.mainloop()