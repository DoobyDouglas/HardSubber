from PIL import Image, ImageTk
from tkinter import filedialog
from typing import Tuple
import subprocess
import tkinter
import os
import pysubs2
import configparser
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
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    with open('config.ini', 'w') as config_file:
        config.write(config_file)
    master.destroy()


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
            variable=var,
            background='#ffc0cb',
            bd=3,
            pady=3,
            activebackground='#ffc0cb'
        )
        checkbox.grid(
            row=i,
            column=0,
            sticky=tkinter.W
        )
        checkboxes[option] = var
    save_button = tkinter.Button(
        master,
        text='Сохранить',
        background='#9b93b3',
        activebackground='#9b93b3',
        bd=3,
        pady=3,
        command=lambda: save_options(checkboxes, master, config)
    )
    save_button.place(relx=0.5, rely=1.0, anchor="center", y=-60)
    master.mainloop()


def checkbox_window():
    master = tkinter.Tk()
    master.geometry('330x100')
    master.resizable(width=False, height=False)
    master.title('Выберите нужные опции')
    img = Image.open("background.png")
    tk_img = ImageTk.PhotoImage(img)
    background_label = tkinter.Label(master, image=tk_img)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    OPTIONS = [
        'audiovideo',
        'video',
        'subs_extract',
    ]
    config = create_or_get_config()
    create_widgets(OPTIONS, master, config)


def comparator(actor: str) -> bool:
    if (
        'text' not in actor
        and 'sign' not in actor
        and 'надпись' not in actor
        and 'caption' not in actor
    ):
        return True
    return False


def subs_extract(video_path, folder) -> str:
    subs_path = f'{folder}subs.ass'
    copy = ''
    while os.path.exists(subs_path):
        copy += 'copy'
        subs_path = f'{folder}subs_{copy}.ass'
    command = f'ffmpeg -i "{video_path}" -map 0:s:m:language:rus "{subs_path}"'
    subprocess.call(command, shell=True)
    return subs_path


def subs_edit(path: str) -> None:
    subs = pysubs2.load(path)
    if subs.events[0].name:
        to_delete = []
        for i, sub in enumerate(subs.events):
            if comparator(sub.name.lower()):
                to_delete.append(i)
    else:
        search_char = '{'
        to_delete = [
            i for i, line in enumerate(subs) if search_char not in line.text
        ]
    for i in reversed(to_delete):
        del subs[i]
    subs.save(path)


def name_generator(file: str, ext: str) -> str:
    ext = ext.replace('.', '')
    name = file.split('/')[-1]
    name = (''.join(i for i in name if i.isalnum())).lower()
    name = name.replace(ext, '')
    return name


def choice_files(config) -> Tuple[str, str, str, str, str]:
    try:
        video = filedialog.askopenfilename(title='Выберите видео')
        filename = os.path.basename(video)
        folder = video.replace(filename, '')
        video_ext = os.path.splitext(video)[-1]
        name = name_generator(video, video_ext)
        video_path = f'{folder}{name}{video_ext}'
        copy = ''
        while os.path.exists(video_path):
            copy += 'copy'
            video_path = f'{folder}{name}_{copy}{video_ext}'
        os.rename(video, video_path)
        video = os.path.basename(video_path)
        value = config['OPTIONS']['subs_extract']
        if value == 'True':
            subs_path = subs_extract(video_path, folder)
            subs_ext = '.ass'
        else:
            subs = filedialog.askopenfilename(title='Выберите субтитры')
            filename = os.path.basename(subs)
            subs_ext = os.path.splitext(subs)[-1]
            name = name_generator(subs, subs_ext)
            subs_path = f'{folder}{name}{subs_ext}'
            copy = ''
            while os.path.exists(subs_path):
                copy += 'copy'
                subs_path = f'{folder}{name}_{copy}{subs_ext}'
            os.rename(subs, subs_path)
        if subs_ext == '.ass':
            subs_edit(subs_path)
        subs = os.path.basename(subs_path)
    except PermissionError:
        tkinter.messagebox.showinfo(
            'Отказано в доступе',
            f'Отказано в доступе к "{folder}". '
            'Попробуйте воспользоваться не системным диском '
            'или не его корневым разделом.'
        )
    except OSError:
        tkinter.messagebox.showinfo(
            'Файлы находятся на разных дисках',
            f'Переместите файлы "{video}" и "{subs}" на один диск.'
        )
    return video_ext, subs_ext, folder, video, subs


def hardsubber() -> None:
    config = create_or_get_config()
    video_ext, subs_ext, folder, video, subs = choice_files(config)
    disk = folder.split(':')[0].lower()
    folder_path = folder.split(':')[1]
    if subs_ext == '.ass':
        param = 'ass'
    else:
        param = 'subtitles'
    value_av = config['OPTIONS']['audiovideo']
    value_v = config['OPTIONS']['video']
    if value_av == 'True':
        sound_param = ' '
    elif value_v == 'True':
        sound_param = ' -an '
    command = (
        f'{disk}: && cd {folder_path} && ffmpeg -i {video} -vf '
        f'{param}={subs} -vcodec libx264 -b 1500k -s 1280x720 '
        f'-acodec copy{sound_param}new_file{video_ext}'
    )
    subprocess.call(command, shell=True)


def main() -> None:
    with open('pic.txt') as file:
        print(file.read())
    checkbox_window()
    tkinter.Tk().withdraw()
    check_config()
    hardsubber()


if __name__ == '__main__':
    main()
