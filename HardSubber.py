from Options import checkbox_window, create_or_get_config, check_config
from SubsEdit import subs_edit
from tkinter import filedialog
from typing import Tuple
import subprocess
import tkinter
import os
import pysubs2

def name_generator(file: str, ext: str) -> str:
    ext = ext.replace('.', '')
    name = file.split('/')[-1]
    name = (''.join(i for i in name if i.isalnum())).lower()
    name = name.replace(ext, '')
    return name


def choice_files() -> Tuple[str]:
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
        hardsubber()
    except OSError:
        tkinter.messagebox.showinfo(
            'Файлы находятся на разных дисках',
            f'Переместите файлы "{video}" и "{subs}" на один диск.'
        )
        hardsubber()
    return video_ext, subs_ext, folder, video, subs


def hardsubber():
    config = create_or_get_config()
    video_ext, subs_ext, folder, video, subs = choice_files()
    disk = folder.split(':')[0].lower()
    folder_path = folder.split(':')[1]
    if subs_ext == '.ass':
        param = 'ass'
    else:
        param = 'subtitles'
    value = config['OPTIONS']['audiovideo']
    if value == 'True':
        command = (
            f'{disk}: && cd {folder_path} && ffmpeg -i {video} -vf '
            f'{param}={subs} -vcodec libx264 -b 1500k -s 1280x720 '
            f'-acodec copy new_file{video_ext}'
        )
        subprocess.call(command, shell=True)
    value = config['OPTIONS']['video']
    if value == 'True':
        command = (
            f'{disk}: && cd {folder_path} && ffmpeg -i {video} -vf '
            f'{param}={subs} -vcodec libx264 -b 1500k -s 1280x720 '
            f'-acodec copy -an new_file{video_ext}'
        )
        subprocess.call(command, shell=True)
    return True


def main():
    with open('pic.txt') as file:
        print(file.read())
    checkbox_window()
    tkinter.Tk().withdraw()
    check_config()
    hardsubber()


if __name__ == '__main__':
    main()
