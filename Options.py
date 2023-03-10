import configparser
import tkinter
import tkinter.messagebox


def create_or_get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def check_config():
    config = create_or_get_config()
    value_1 = config['OPTIONS']['audiovideo']
    value_2 = config['OPTIONS']['video']
    if value_1 == 'True' and value_2 == 'True':
        tkinter.messagebox.showinfo(
            'Выбраны оба параметра',
            'Выберите только один'
        )
        raise SystemExit


def save_options(
        checkboxes: dict,
        master: tkinter.Tk,
        config: configparser.ConfigParser
        ):
    save_button = tkinter.Button(
        master,
        text='Сохранить',
        command=master.destroy
    )
    save_button.grid(
        row=len(checkboxes),
        column=0
    )
    master.mainloop()
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def create_widgets(
        OPTIONS: list,
        master: tkinter.Tk,
        config: configparser.ConfigParser
        ):
    checkboxes = {}
    if 'OPTIONS' not in config:
        config['OPTIONS'] = {}
    for i, option in enumerate(OPTIONS):
        var = tkinter.BooleanVar()
        if option in config['OPTIONS']:
            var.set(config['OPTIONS'].getboolean(option))
        else:
            var.set(False)
        checkbox = tkinter.Checkbutton(
            master,
            text=option,
            variable=var
        )
        checkbox.grid(
            row=i,
            column=0,
            sticky=tkinter.W
        )
        checkboxes[option] = var
    return checkboxes


def checkbox_window():
    master = tkinter.Tk()
    master.geometry('330x100')
    master.title('Выберите нужные опции')
    OPTIONS = [
        'audiovideo',
        'video',
    ]
    config = create_or_get_config()
    checkboxes = create_widgets(OPTIONS, master, config)
    save_options(checkboxes, master, config)
