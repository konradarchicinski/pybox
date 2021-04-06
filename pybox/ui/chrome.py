#!/usr/bin/env python
import sys
import subprocess as sps
import os

# CRED: the entire module comes from external project `Eel`, only minor fixes
# were added to adapt the module to the functionality of the current project
# https://github.com/samuelhwilliams/Eel/blob/master/eel/chrome.py

name = 'Google Chrome/Chromium'


def run(start_urls, chrome_path=None, options=None):
    """Runs the Google Chrome browser.

    Args:

        start_urls (list): urls to open at the browser startup.
        chrome_path (str, optional): specific directory of the Google Chrome
            browser executable file. Defaults to None.
        options (list, optional): additional command-line arguments passed
            while browser startup. Defaults to None.
    """
    if chrome_path is None:
        chrome_path = find_path()
    if options is None:
        options = dict(app_mode=True, cmdline_args=list())

    if options['app_mode']:
        for url in start_urls:
            sps.Popen([chrome_path, '--app=%s' % url] + options['cmdline_args'],
                      stdout=sps.PIPE,
                      stderr=sps.PIPE,
                      stdin=sps.PIPE)
    else:
        args = options['cmdline_args'] + start_urls
        sps.Popen([chrome_path, '--new-window'] + args,
                  stdout=sps.PIPE,
                  stderr=sys.stderr,
                  stdin=sps.PIPE)


def find_path():
    """Finds the directory in which Google Chrome executable is stored."""
    if sys.platform in ['win32', 'win64']:
        return _find_chrome_win()
    elif sys.platform == 'darwin':
        return _find_chrome_mac() or _find_chromium_mac()
    elif sys.platform.startswith('linux'):
        return _find_chrome_linux()
    else:
        return None


def _find_chrome_mac():
    default_dir = r'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if os.path.exists(default_dir):
        return default_dir
    # use mdfind ci to locate Chrome in alternate locations and return the first one
    name = 'Google Chrome.app'
    alternate_dirs = [
        x for x in sps.check_output(["mdfind", name]).decode().split('\n')
        if x.endswith(name)
    ]
    if len(alternate_dirs):
        return alternate_dirs[0] + '/Contents/MacOS/Google Chrome'
    return None


def _find_chromium_mac():
    default_dir = r'/Applications/Chromium.app/Contents/MacOS/Chromium'
    if os.path.exists(default_dir):
        return default_dir
    # use mdfind ci to locate Chromium in alternate locations and return the first one
    name = 'Chromium.app'
    alternate_dirs = [
        x for x in sps.check_output(["mdfind", name]).decode().split('\n')
        if x.endswith(name)
    ]
    if len(alternate_dirs):
        return alternate_dirs[0] + '/Contents/MacOS/Chromium'
    return None


def _find_chrome_linux():
    import whichcraft as wch
    chrome_names = [
        'chromium-browser', 'chromium', 'google-chrome', 'google-chrome-stable'
    ]

    for name in chrome_names:
        chrome = wch.which(name)
        if chrome is not None:
            return chrome
    return None


def _find_chrome_win():
    import winreg as reg
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'

    chrome_path = None
    for install_type in reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE:
        try:
            reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
            chrome_path = reg.QueryValue(reg_key, None)
            reg_key.Close()
            if not os.path.isfile(chrome_path):
                continue
        except WindowsError:
            continue
        else:
            break

    return chrome_path
