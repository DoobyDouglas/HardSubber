from Options import checkbox_window, create_or_get_config, check_config
from tkinter import filedialog
import subprocess
import tkinter
import os


def choice_files():
    video = filedialog.askopenfilename(title='Выберите видео')
    filename = os.path.basename(video)
    video_ext = os.path.splitext(video)[-1]
    folder = video.replace(filename, '')
    os.rename(video, folder + 'video' + video_ext)
    subs = filedialog.askopenfilename(title='Выберите субтитры')
    filename = os.path.basename(subs)
    subs_ext = os.path.splitext(subs)[-1]
    os.rename(subs, folder + 'subs' + subs_ext)
    return video_ext, subs_ext, folder


def hardsubber():
    config = create_or_get_config()
    video_ext, subs_ext, folder = choice_files()
    disk = folder.split(':')[0].lower()
    folder_path = folder.split(':')[1]
    if subs_ext == '.ass':
        param = 'ass'
    else:
        param = 'subtitles'
    value = config['OPTIONS']['audiovideo']
    if value == 'True':
        command = (
            f'{disk}: && cd {folder_path} && ffmpeg -i video{video_ext} -vf '
            f'{param}=subs{subs_ext} -vcodec libx264 -b 1500k -s 1280x720 '
            f'-acodec aac -ab 256k new_file{video_ext}'
        )
        subprocess.call(command, shell=True)
    value = config['OPTIONS']['video']
    if value == 'True':
        command = (
            f'{disk}: && cd {folder_path} && ffmpeg -i video{video_ext} -vf '
            f'{param}=subs{subs_ext} -vcodec libx264 -b 1500k -s 1280x720 '
            f'-acodec aac -an new_file{video_ext}'
        )
        subprocess.call(command, shell=True)


def main():
    checkbox_window()
    tkinter.Tk().withdraw()
    check_config()
    hardsubber()


if __name__ == '__main__':
    main()
