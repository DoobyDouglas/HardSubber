from tkinter import filedialog
from typing import Tuple
import ffmpeg
import tkinter
import os
import pysubs2
import tkinter.messagebox
from configs import get_value, get_config, SUBS_LANGS_DICT
from ffmpeg._run import Error


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


def subs_extract(video_path, folder, master) -> str or None:
    lang = SUBS_LANGS_DICT[get_config()['OPTIONS']['subs_lang']]
    input_file = ffmpeg.input(video_path)
    subs_path = f'{folder}subs.ass'
    copy = ''
    while os.path.exists(subs_path):
        copy += 'copy'
        subs_path = f'{folder}subs_{copy}.ass'
    master.nametowidget('pb').start()
    try:
        output = ffmpeg.output(
            input_file, subs_path, map=f'0:s:m:language:{lang}'
        )
        ffmpeg.run(output)
        master.nametowidget('pb').stop()
        return subs_path
    except Error:
        master.nametowidget('pb').stop()
        tkinter.messagebox.showerror(
            'Нет субтитров',
            'Выбранного языка субтитров нет в видео.'
        )
        return None


def subs_edit(path: str) -> None:
    subs = pysubs2.load(path)
    to_delete = []
    char = '{'
    for i, sub in enumerate(subs.events):
        if comparator(sub.name.lower()):
            to_delete.append(i)
        elif comparator(sub.name.lower()):
            to_delete.append(i)
    if len(to_delete) == len(subs.events):
        to_delete = [
            i for i, sub in enumerate(subs.events) if char not in sub.text
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


def choice_files(
        master: tkinter.Tk
        ) -> (
        Tuple[str or None,
              str or None,
              str or None,
              str or None,
              str or None]
        ):
    try:
        video = filedialog.askopenfilename(
            title='Выберите видео',
            filetypes=[('Видео mkv и mp4', '*.mkv *.mp4')],
        )
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
                subs_path = subs_extract(video_path, folder, master)
                subs_ext = '.ass'
            else:
                subs = filedialog.askopenfilename(
                    title='Выберите субтитры',
                    filetypes=[('Субтитры ass и srt', '*.ass *.srt')]
                )
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
            if subs_path:
                if subs_ext == '.ass':
                    if get_value('subs_cleaner'):
                        subs_edit(subs_path)
                subs = os.path.basename(subs_path)
            else:
                subs = None
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


if __name__ == '__main__':
    pass
