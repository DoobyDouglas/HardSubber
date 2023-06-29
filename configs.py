import configparser
import tkinter

DEFAULT_BITRATE = 1500
SUBS_LANGS_DICT = {
    'Russia': 'rus',
    'US': 'eng',
    'Saudi Arabia': 'ara',
    'Germany': 'ger',
    'Latin America': 'spa',
    'France': 'fre',
    'Italy': 'ita',
    'Brasil': 'por'
}
RESOLUTIONS_LIST = [
    'ORIGINAL',
    '1280x720',
    '1920x1080',
    '3840x2160',
]


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read('HARDSUBBER.ini', encoding='utf-8')
    if 'OPTIONS' not in config:
        config['OPTIONS'] = {}
    return config


def get_value(name: str) -> bool:
    return get_config()['OPTIONS'].getboolean(name)


def save_options(checkboxes: dict, master: tkinter.Tk) -> None:
    config = get_config()
    for option, var in checkboxes.items():
        config['OPTIONS'][option] = str(var.get())
    subs_lang = master.nametowidget('subs_menu').get()
    config['OPTIONS']['subs_lang'] = subs_lang
    resolution = master.nametowidget('resolution_menu').get()
    config['OPTIONS']['resolution'] = resolution
    bitrate = master.nametowidget('bitrate_entry').get()
    if bitrate:
        if len(bitrate) < 4:
            for _ in range(4 - len(bitrate)):
                bitrate += '0'
        try:
            bitrate = int(bitrate)
        except ValueError:
            bitrate = DEFAULT_BITRATE
    config['OPTIONS']['bitrate'] = str(bitrate)
    with open('HARDSUBBER.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


if __name__ == '__main__':
    pass
