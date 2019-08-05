import os
import subprocess
import time

import pythoncom
import win32com.client
from win32com.client import Dispatch, GetActiveObject

from .exceptions import NoExcelWorkbookException


def _kill_excel():
    os.system('taskkill /f /im excel.exe')

def _load_excel(visible=True):
    xl = Dispatch('Excel.Application')
    xl.Visible = visible

    return xl

def _connect_to_running_excel(visible=True):
    xl = GetActiveObject('Excel.Application')
    xl.Visible = visible

    return xl

def _restart_excel_with_addins_and_attach(restart_sleep=15, start_sleep=30, max_retries=3):
    _kill_excel()
    time.sleep(restart_sleep)
    return _start_excel_with_addins_and_attach(sleep=start_sleep, tries_remaining=max_retries)

def _start_excel_with_addins_and_attach(sleep=30, tries_remaining=3):

    if tries_remaining <= 0:
        raise NoExcelWorkbookException('Tried 3 times and was still not able to start Excel and connect to open workbook')

    try:
        excel = _start_excel_and_attach(sleep=sleep)
    except NoExcelWorkbookException:
        time.sleep(10)
        _kill_excel()
        time.sleep(30)
        excel = _start_excel_with_addins_and_attach(sleep=sleep, tries_remaining=tries_remaining - 1)

    return excel

def _start_excel_and_attach(sleep=30):
    _start_excel_with_addins(sleep=sleep)
    return _get_excel_running_workbook('Book1.xlsx')

def _start_excel_with_addins(sleep=30):
    command = new_excel_command()
    subprocess.Popen(command)
    time.sleep(sleep)

def _get_excel_running_workbook(workbook_name):
    lenstr = len(workbook_name)
    obj = None
    rot = pythoncom.GetRunningObjectTable()
    rotenum = rot.EnumRunning()

    while True:
        monikers = rotenum.Next()
        if not monikers: break

        ctx = pythoncom.CreateBindCtx(0)
        name = monikers[0].GetDisplayName(ctx, None)

        if name[-lenstr:] == workbook_name:
            obj = rot.GetObject(monikers[0])


    if obj is None:
        raise NoExcelWorkbookException(f'Could not find open workbook {workbook_name}')

    workbook = win32com.client.gencache.EnsureDispatch(obj.QueryInterface(pythoncom.IID_IDispatch))

    return workbook.Application

def new_excel_command():
    ### TEMP
    # Need to not hardcode filepaths. Can generalize by writing functions to find excel and create blank workbook
    excel_filepath = r'C:\Program Files (x86)\Microsoft Office\Office16\EXCEL.EXE'
    workbook_filepath = r'C:\Users\derobertisna.UFAD\Dropbox (Personal)\UF\Andy\ETF Project\Temp\Book1.xlsx'
    return _new_excel_command(excel_filepath, workbook_filepath)


def _new_excel_command(excel_filepath, workbook_filepath):
    return f'"{excel_filepath}" "{workbook_filepath}"'

