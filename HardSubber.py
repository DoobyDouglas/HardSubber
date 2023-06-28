from PIL import Image, ImageTk
from typing import Tuple, Dict
import subprocess
import tkinter
import os
import pysubs2
import tkinter.messagebox
from threading import Thread
import sys
import tkinter.ttk as ttk
from ttkbootstrap import Style
import json
from configs import (
    get_config,
    get_value,
    save_options,
    SUBS_LANGS_DICT,
    RESOLUTIONS_LIST,
)
from fileworks import choice_files
# pyinstaller --noconfirm --onefile --noconsole --add-data 'background.png;.' HardSubber.py


def hardsubber(master: tkinter.Tk) -> None:
    config = get_config()
    video_ext, subs_ext, folder, video, subs = choice_files(master)
    if video_ext and subs_ext and folder and video and subs:
        master.nametowidget('pb').start()
        disk = folder.split(':')[0].lower()
        folder_path = folder.split(':')[1]
        if subs_ext == '.ass':
            param = 'ass'
        else:
            param = 'subtitles'
        if get_value('audio'):
            sound_param = ' '
        else:
            sound_param = ' -an '
        if config['OPTIONS']['bitrate']:
            bitrate = f" -b {config['OPTIONS']['bitrate']}k "
        else:
            bitrate = ' '
        if config['OPTIONS']['resolution'] != 'ORIGINAL':
            resolution = f" -s {config['OPTIONS']['resolution']} "
        else:
            resolution = ' '
        if get_value('convert_to_mp4'):
            video_ext = '.mp4'
        command = (
            f'{disk}: && cd {folder_path} && ffmpeg -i {video} -vf '
            f'{param}={subs} -vcodec libx264'
            f'{bitrate}{resolution}'
            f'-acodec copy{sound_param}new_file{video_ext}'
        )
        subprocess.call(command, shell=True)
        master.nametowidget('pb').stop()


def main(checkboxes: Dict, master: tkinter.Tk) -> None:
    save_options(checkboxes, master)
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


def get_subs_langs():
    if not os.path.exists('subs_langs.json'):
        with open('subs_langs.json', 'w+') as json_file:
            data = {}
            for key, value in SUBS_LANGS_DICT.items():
                data[key] = value
            json.dump(data, json_file)
    with open('subs_langs.json', 'r') as json_file:
        data = json.load(json_file)
    return data


def menu_setup(menu, key):
    if key == 'subs_lang':
        LIST = SUBS_LANGS_LIST
    else:
        LIST = RESOLUTIONS_LIST
    try:
        if config['OPTIONS'][key] in LIST:
            menu.set(config['OPTIONS'][key])
        else:
            menu.set(LIST[0])
    except KeyError:
        menu.set(LIST[0])


def set_geometry(master: tkinter.Tk):
    width = 300
    height = 236
    s_width = master.winfo_screenwidth()
    s_height = master.winfo_screenheight()
    upper = s_height // 5
    x = (s_width - width) // 2
    y = (s_height - height) // 2
    return f'{width}x{height}+{x}+{y - upper}'


config = get_config()
master = tkinter.Tk(className='HARDSUBBER.main')
master.geometry(set_geometry(master))
master.resizable(False, False)
master.title('HARDSUBBER v1.76')
img = Image.open(resource_path('background.png'))
tk_img = ImageTk.PhotoImage(img)
background_label = tkinter.Label(master, image=tk_img)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

style = Style(theme='pulse')
style.configure('TCheckbutton', background='#ffc0cb')
style.configure('TButton', background='#ffc0cb', foreground='black')
style.configure('TLabel', background='#ffc0cb')
style.configure('Horizontal.TProgressbar', thickness=27)

subs_extract_ = ttk.Label(master, text='Select subtitles to extract:')
subs_extract_.grid(row=0, column=0, sticky=tkinter.W, padx=6, pady=6)
select_resolution = ttk.Label(master, text='Select resolution:')
select_resolution.grid(row=1, column=0, sticky=tkinter.W, padx=6, pady=6)
enter_bitrate = ttk.Label(master, text='Enter bitrate:')
enter_bitrate.grid(row=2, column=0, sticky=tkinter.W, padx=6, pady=6)

SUBS_LANGS_LIST = list(get_subs_langs().keys())

subs_menu = ttk.Combobox(
    master,
    values=SUBS_LANGS_LIST,
    name='subs_menu',
    state='readonly',
    width=12,
)
subs_menu.place(relx=0.5, rely=1.0, anchor="s", x=95, y=-204)
menu_setup(subs_menu, 'subs_lang')

resolution_menu = ttk.Combobox(
    master,
    values=RESOLUTIONS_LIST,
    name='resolution_menu',
    state='readonly',
    width=12,
)
resolution_menu.place(relx=0.5, rely=1.0, anchor="s", x=95, y=-173)
menu_setup(resolution_menu, 'resolution')

bitrate_entry = ttk.Entry(
    master,
    name='bitrate_entry',
    width=14,
)
bitrate_entry.place(relx=0.5, rely=1.0, anchor="s", x=95, y=-142)
if config['OPTIONS']['bitrate']:
    bitrate_entry.insert(1, config['OPTIONS']['bitrate'])

OPTIONS = [
    'audio',
    'subs_extract',
    'subs_cleaner',
    'convert_to_mp4',
]

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
        padding=6,
    )
    checkbox.grid(
        row=i + 3,
        column=0,
        sticky=tkinter.W
    )
    checkboxes[option] = var

save_button = ttk.Button(
    master,
    name='start',
    text='START',
    width=6,
    command=lambda: on_save_click(checkboxes, master),
)
save_button.grid(row=7, column=0, padx=6, sticky=tkinter.W)

progressbar = ttk.Progressbar(
    master,
    mode='determinate',
    name='pb',
    length=224,
    style='Horizontal.TProgressbar',
)
progressbar.place(relx=0.5, rely=1.0, anchor="center", y=-21, x=32)

if __name__ == '__main__':
    master.mainloop()
