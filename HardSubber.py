from PIL import Image, ImageTk
from tkinter import filedialog
from typing import Tuple
import subprocess
import tkinter
import os
import pysubs2
import configparser
import tkinter.messagebox
from threading import Thread
from typing import Dict
import sys
import tkinter.ttk as ttk
# pyinstaller --noconfirm --onefile --noconsole --add-data 'background.png;.' HardSubber.py


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'OPTIONS' not in config:
        config['OPTIONS'] = {}
    return config


def get_value(name: str) -> bool:
    config = get_config()
    if config['OPTIONS'][name] == 'True':
        return True
    return False


def check_config() -> None:
    if get_value('audiovideo') and get_value('video'):
        tkinter.messagebox.showinfo(
            'Выбраны оба параметра для выходного файла',
            'Выберите только один'
        )
        raise SystemExit


def save_options(checkboxes: dict) -> None:
    config = get_config()
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def comparator(sub: str) -> bool:
    if (
        'text' not in sub
        and 'sign' not in sub
        and 'надпись' not in sub
        and 'caption' not in sub
        and 'title' not in sub
        and 'song' not in sub
        and 'screen' not in sub
        and 'typedigital' not in sub
        and 'phonetics' not in sub
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
    to_delete = []
    search_char = '{'
    if subs.events[0].name:
        for i, sub in enumerate(subs.events):
            if comparator(sub.name.lower()) and search_char not in sub.text:
                to_delete.append(i)
    if subs.events[0].style:
        for i, sub in enumerate(subs.events):
            if comparator(sub.style.lower()) and search_char not in sub.text:
                if i not in to_delete:
                    to_delete.append(i)
    else:
        to_delete = [
            i for i, line in enumerate(subs) if search_char not in line.text
        ]
    to_delete.sort()
    for i in reversed(to_delete):
        del subs[i]
    subs.save(path)


def name_generator(file: str, ext: str) -> str:
    ext = ext.replace('.', '')
    name = file.split('/')[-1]
    name = (''.join(i for i in name if i.isalnum())).lower()
    name = name.replace(ext, '')
    return name


def choice_files(master: tkinter.Tk) -> Tuple[str, str, str, str, str]:
    try:
        video = filedialog.askopenfilename(title='Выберите видео')
        if video:
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
            if get_value('subs_extract') and video_ext == '.mkv':
                master.nametowidget('pb').start()
                subs_path = subs_extract(video_path, folder)
                subs_ext = '.ass'
                master.nametowidget('pb').stop()
            else:
                subs = filedialog.askopenfilename(title='Выберите субтитры')
                if subs:
                    filename = os.path.basename(subs)
                    subs_ext = os.path.splitext(subs)[-1]
                    name = name_generator(subs, subs_ext)
                    subs_path = f'{folder}{name}{subs_ext}'
                    copy = ''
                    while os.path.exists(subs_path):
                        copy += 'copy'
                        subs_path = f'{folder}{name}_{copy}{subs_ext}'
                    os.rename(subs, subs_path)
                else:
                    return None, None, None, None, None
            if subs_ext == '.ass':
                subs_edit(subs_path)
            subs = os.path.basename(subs_path)
        else:
            return None, None, None, None, None
    except PermissionError:
        tkinter.messagebox.showerror(
            'Отказано в доступе',
            f'Отказано в доступе к "{folder}". '
            'Попробуйте воспользоваться не системным диском '
            'или не его корневым разделом.'
        )
    except OSError:
        tkinter.messagebox.showerror(
            'Файлы находятся на разных дисках',
            f'Переместите файлы "{video}" и "{subs}" на один диск.'
        )
    return video_ext, subs_ext, folder, video, subs


def hardsubber(master: tkinter.Tk) -> None:
    video_ext, subs_ext, folder, video, subs = choice_files(master)
    if video_ext and subs_ext and folder and video and subs:
        master.nametowidget('pb').start()
        disk = folder.split(':')[0].lower()
        folder_path = folder.split(':')[1]
        if subs_ext == '.ass':
            param = 'ass'
        else:
            param = 'subtitles'
        if get_value('audiovideo'):
            sound_param = ' '
        elif get_value('video'):
            sound_param = ' -an '
        if get_value('convert_to_mp4'):
            video_ext = '.mp4'
        command = (
            f'{disk}: && cd {folder_path} && ffmpeg -i {video} -vf '
            f'{param}={subs} -vcodec libx264 -b 1500k -s 1280x720 '
            f'-acodec copy{sound_param}new_file{video_ext}'
        )
        subprocess.call(command, shell=True)
        master.nametowidget('pb').stop()


def main(checkboxes: Dict, master: tkinter.Tk) -> None:
    save_options(checkboxes)
    check_config()
    master.nametowidget('start').config(state='disabled')
    hardsubber(master)
    master.nametowidget('start').config(state='normal')


def on_save_click(checkboxes: Dict, master: tkinter.Tk):
    thread = Thread(target=main, args=(checkboxes, master))
    thread.start()


def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, path)


master = tkinter.Tk(className='HARDSUBBER.main')
width = 330
height = 125
s_width = master.winfo_screenwidth()
s_height = master.winfo_screenheight()
upper = s_height // 5
x = (s_width - width) // 2
y = (s_height - height) // 2
master.geometry(f'{width}x{height}+{x}+{y - upper}')
master.resizable(width=False, height=False)
master.title('HARDSUBBER v1.71')
img = Image.open(resource_path('background.png'))
tk_img = ImageTk.PhotoImage(img)
background_label = tkinter.Label(master, image=tk_img)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
checkbox_style = ttk.Style()
checkbox_style.configure('TCheckbutton', background='#ffc0cb')
button_style = ttk.Style()
button_style.configure('TButton', background='#ffc0cb')
OPTIONS = [
    'audiovideo',
    'video',
    'subs_extract',
    'convert_to_mp4',
]
config = get_config()
checkboxes = {}
if 'OPTIONS' not in config:
    config['OPTIONS'] = {}
for i, option in enumerate(OPTIONS):
    var = tkinter.BooleanVar()
    if option in config['OPTIONS']:
        var.set(config['OPTIONS'].getboolean(option))
    else:
        var.set(False)
    checkbox = ttk.Checkbutton(
        master,
        text=option,
        variable=var,
        padding=7,
    )
    checkbox.grid(
        row=i,
        column=0,
        sticky=tkinter.W
    )
    checkboxes[option] = var
save_button = ttk.Button(
    master,
    name='start',
    text='START',
    command=lambda: on_save_click(checkboxes, master),
)
save_button.place(relx=0.5, rely=1.0, anchor="center", y=-65, x=2)
progressbar = ttk.Progressbar(master, mode='determinate', name='pb')
progressbar.grid(
    row=0,
    column=1,
    padx=0,
    pady=3,
    sticky='we'
)

if __name__ == '__main__':
    master.mainloop()
