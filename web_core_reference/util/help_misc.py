import hashlib
import json
import os, re
import platform
import subprocess
import sys
import time
from dataclasses import is_dataclass, asdict
from pathlib import Path

from web_core_reference import VERSION
from web_core_reference.configure.config import tr, app_cfg, logger, ROOT_DIR, defaulelang, push_queue
import tqdm

from web_core_reference.task.taskcfg import SignMsg


def create_tqdm_class(callback):
    class QtAwareTqdm(tqdm.tqdm):

        def display(self, msg=None, pos=None):
            super().display(msg, pos)
            _str = str(self).split('%')
            if callback and len(_str) > 0:
                callback(_str[0] + '%')

    return QtAwareTqdm


def show_popup(title, text):
    logger.warning(f"{title}: {text}")
    return None

def show_error(tb_str):
    logger.error(tb_str)
    return None

def open_url(url: str = None):
    import webbrowser
    title_url_dict = {
        'bbs': "https://bbs.pyvideotrans.com",
        'ffmpeg': "https://www.ffmpeg.org/download.html",
        'git': "https://github.com/jianchang512/pyvideotrans",
        'issue': "https://github.com/jianchang512/pyvideotrans/issues",
        'hfmirrorcom': "https://pyvideotrans.com/819",
        'models': "https://github.com/jianchang512/stt/releases/tag/0.0",
        'stt': "https://github.com/jianchang512/stt/",

        'gtrans': "https://pyvideotrans.com/aiocr",
        'cuda': "https://pyvideotrans.com/gpu.html",
        'website': "https://pyvideotrans.com",
        'help': "https://pyvideotrans.com",
        'xinshou': "https://pyvideotrans.com/getstart",
        "about": "https://pyvideotrans.com/about",
        'download': "https://github.com/jianchang512/pyvideotrans/releases",
    }
    if url and url.startswith("http"):
        return webbrowser.open_new_tab(url)
    if url and url in title_url_dict:
        return webbrowser.open_new_tab(title_url_dict[url])
    return


def vail_file(file=None):
    if not file:
        return False
    p = Path(file)
    if not p.exists() or not p.is_file():
        return False
    if p.stat().st_size == 0:
        return False
    return True


def hide_show_element(wrap_layout, show_status):
    def hide_recursive(layout, show_status):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                if not show_status:
                    item.widget().hide()
                else:
                    item.widget().show()
            elif item.layout():
                hide_recursive(item.layout(), show_status)

    hide_recursive(wrap_layout, show_status)


def shutdown_system():
    # 获取当前操作系统类型
    system = platform.system()

    if system == "Windows":
        # Windows 下的关机命令
        subprocess.call("shutdown /s /t 1")
    elif system == "Linux":
        # Linux 下的关机命令
        subprocess.call("poweroff")
    elif system == "Darwin":
        # macOS 下的关机命令
        subprocess.call("sudo shutdown -h now", shell=True)
    else:
        logger.error(f"Unsupported system: {system}")


# 获取 prompt提示词
def get_prompt(ainame, aisendsrt=True):
    prompt_file = get_prompt_file(ainame=ainame, aisendsrt=aisendsrt)
    content = Path(prompt_file).read_text(encoding='utf-8-sig', errors="ignore")
    glossary = ''
    if Path(ROOT_DIR + '/web_core_reference/glossary.txt').exists():
        glossary = Path(ROOT_DIR + '/web_core_reference/glossary.txt').read_text(encoding='utf-8-sig', errors="ignore").strip()
        if glossary:
            glossary = "\n".join(["|" + it.replace("=", '|') + "|" for it in glossary.split('\n')])
            glossary = f"\n\n# Glossary of terms\nTranslations are made strictly according to the following glossary. If a term appears in a sentence, the corresponding translation must be used, not a free translation:\n| Glossary | Translation |\n| --------- | ----- |\n{glossary}\n\n"
    content = content.replace('{GLOSSARY_DICT}', glossary)
    return content


def qwenmt_glossary():
    if Path(ROOT_DIR + '/web_core_reference/glossary.txt').exists():
        glossary = Path(ROOT_DIR + '/web_core_reference/glossary.txt').read_text(encoding='utf-8-sig', errors="ignore").strip()
        if glossary:
            term = []
            for it in glossary.split('\n'):
                tmp = it.split("=")
                if len(tmp) == 2:
                    term.append({"source": tmp[0], "target": tmp[1]})
            return term if len(term) > 0 else None
    return None


# 获取当前需要操作的prompt txt文件
def get_prompt_file(ainame, aisendsrt=True):
    prompt_path = f'{ROOT_DIR}/web_core_reference/'
    prompt_name = f'{ainame}.txt'
    if aisendsrt:
        prompt_path += 'prompts/srt/'
    else:
        prompt_path += 'prompts/text/'
    return f'{prompt_path}{prompt_name}'


def show_glossary_editor(parent=None):
    raise RuntimeError("Glossary editor is unavailable in headless snapshot")

def is_novoice_mp4(novoice_mp4, noextname, uuid=None):
    # 预先创建好的
    # 判断novoice_mp4是否完成
    t = 0

    if noextname not in app_cfg.queue_novice and vail_file(novoice_mp4):
        return True
    if noextname in app_cfg.queue_novice and app_cfg.queue_novice[noextname] == 'end':
        return True
    last_size = 0
    while True:
        if app_cfg.current_status != 'ing' or app_cfg.exit_soft:
            return False
        if vail_file(novoice_mp4):
            current_size = os.path.getsize(novoice_mp4)
            if 0 < last_size == current_size and t > 1200:
                return True
            last_size = current_size

        if noextname not in app_cfg.queue_novice:
            raise RuntimeError(f"{noextname} split no voice videoerror-1")
        if app_cfg.queue_novice[noextname].startswith('error:'):
            raise RuntimeError(f"{noextname} split no voice {app_cfg.queue_novice[noextname]}")

        if app_cfg.queue_novice[noextname] == 'ing':
            size = f'{round(last_size / 1024 / 1024, 2)}MB' if last_size > 0 else ""
            set_process(
                text=f"{noextname} {tr('spilt audio and video')} {size}",
                uuid=uuid)
            time.sleep(1)
            t += 1
            continue
        return True


# 将字符串做 md5 hash处理
def get_md5(input_string: str):
    md5 = hashlib.md5()
    md5.update(input_string.encode('utf-8'))
    return md5.hexdigest()


def pygameaudio(filepath=None):
    try:
        import soundfile as sf
        import sounddevice as sd
        data, fs = sf.read(filepath)
        channels = 1 if data.ndim == 1 else data.shape[1]
        try:
            device_info = sd.query_devices(kind='output')
            max_channels = int(device_info.get('max_output_channels') or channels)
        except Exception:
            max_channels = channels

        if channels == 1 and max_channels >= 2:
            data = data.reshape(-1, 1).repeat(2, axis=1)
        elif channels > max_channels > 0:
            data = data[:, :max_channels]
        sd.play(data, fs)
        sd.wait()
    except Exception as e:
        logger.exception(f'播放试听声音失败:{e}')


def read_last_n_lines(filename, n=100):
    if not Path(filename).exists():
        return []
    from collections import deque
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # 使用 deque 只保留最后 n 行
            last_lines = deque(file, maxlen=n)
        return list(last_lines)  # 返回列表形式
    except FileNotFoundError:
        return []
    except Exception:
        return []


# 综合写入日志，默认sp界面
# type=logs|error|subtitle|end|stop|succeed|set_precent|replace_subtitle|.... 末尾显示类型，
# uuid 任务的唯一id，用于确定插入哪个子队列
def set_process(*, text="", type="logs", uuid=None):
    if app_cfg.exit_soft:
        return
    try:
        if text:
            text = text.replace('\\n', ' ')

        if app_cfg.exec_mode == 'cli':
            print(text)
            return
        log = SignMsg(**{"text": text, "type": type, "uuid": uuid})
        push_queue(uuid or "", log)
    except Exception as e:
        logger.exception(f'set_process：{e}', exc_info=True)


def set_proxy(set_val=''):
    if set_val == 'del':
        app_cfg.proxy = ''
        if os.environ.get('HTTP_PROXY'):
            del os.environ['HTTP_PROXY']
        if os.environ.get('HTTPS_PROXY'):
            del os.environ['HTTPS_PROXY']
        return

    if set_val:
        # 设置代理
        set_val = set_val.lower()
        if not set_val.startswith("http") and not set_val.startswith('sock'):
            set_val = f"http://{set_val}"
        app_cfg.proxy = set_val
        os.environ['HTTP_PROXY'] = set_val
        os.environ['HTTPS_PROXY'] = set_val
        return set_val

    # 获取代理
    http_proxy = app_cfg.proxy or os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')

    if http_proxy:
        http_proxy = http_proxy.lower()
        if not http_proxy.startswith("http") and not http_proxy.startswith('sock'):
            http_proxy = f"http://{http_proxy}"
        return http_proxy
    if sys.platform != 'win32':
        return None
    try:
        import winreg
        # 打开 Windows 注册表
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            # 读取代理设置
            proxy_enable, _ = winreg.QueryValueEx(key, 'ProxyEnable')
            proxy_server, _ = winreg.QueryValueEx(key, 'ProxyServer')
            if proxy_enable == 1 and proxy_server:
                # 是否需要设置代理
                proxy_server = proxy_server.lower()
                if not proxy_server.startswith("http") and not proxy_server.startswith('sock'):
                    proxy_server = "http://" + proxy_server

                return proxy_server
    except Exception:
        pass
    return None


def process_openai_api(url=""):
    if not url:
        return "https://api.openai.com/v1"
    if not url.startswith('http'):
        url = 'http://' + url

    # 删除末尾 /
    url = url.rstrip('/').lower()
    if url.find(".openai.com") > -1:
        return "https://api.openai.com/v1"

    if url.endswith('/v1'):
        return url

    # 存在 /v1/xx的，改为 /v1
    if url.find('/v1/chat/') > -1:
        return re.sub(r'/v1.*$', '/v1', url, flags=re.I | re.S)

    return url


# 序列化

def serial(data: object) -> str:
    if not isinstance(data, list):
        return json.dumps(asdict(data) if is_dataclass(data) else data)
    _newlist = []
    for it in data:
        _newlist.append(asdict(it) if is_dataclass(it) else it)
    return json.dumps(_newlist)


def check_new_version():
    # 查看当前最新版本信息
    try:

        import requests
        # 纯静态文件，仅返回版本信息字符串
        # 只获取当前软件版本号数字和操作系统类型(win32/macos/linux)
        url = f"https://pyvideotrans.com/version.json?version={VERSION}&os={sys.platform}"
        res = requests.get(url)
        res.raise_for_status()
        d = res.json()
        app_cfg.new_version_pvt = d['version']
    except Exception:
        #logger.exception(f'获取最新版本信息失败{e}', exc_info=True)
        pass




def _get_type_name(type_index, name_list):
    if type_index is None or type_index >= len(name_list):
        return '-'
    return name_list[type_index]


def get_recogn_type(type_index=None):
    from web_core_reference.recognition import RECOGN_NAME_LIST
    return _get_type_name(type_index, RECOGN_NAME_LIST)


def get_tanslate_type(type_index=None):
    from web_core_reference.translator import TRANSLASTE_NAME_LIST
    return _get_type_name(type_index, TRANSLASTE_NAME_LIST)


def get_tts_type(type_index=None):
    from web_core_reference.tts import TTS_NAME_LIST
    return _get_type_name(type_index, TTS_NAME_LIST)

