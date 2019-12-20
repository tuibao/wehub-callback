import psutil
import subprocess,time
import win32file
import win32pipe
import threading
import winreg

APP_NAME="WeHub.exe"
REG_PATH = R'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths'

def get_wehub_pidList():
    '''获取所有wehub的进程id'''
    wehub_pids = []
    for proc in psutil.process_iter():
        if proc.name()==APP_NAME:
            wehub_pids.append(proc.pid)
    return wehub_pids


def openWeHub(qr_session = None,qr_upload_url= None):
    #开启新的wehub进程，可以传入两个参数（可选）
    #参考：http://wehub.weituibao.com/doc/main/qrcode.html
    #优先从注册表里读安装路径
    reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,REG_PATH,0,(winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
    app_path = winreg.QueryValue(reg_key,APP_NAME)
    launchParam =[app_path]
    if qr_session and len(qr_session)>0:
        launchParam.append('--qr_session')
        launchParam.append(qr_session)
    if qr_upload_url and len(qr_upload_url)>0:
        launchParam.append('--upload_url')
        launchParam.append(qr_upload_url)

    wehub_process = subprocess.Popen(launchParam)
    print ("launch new Wehub process,  pid = %d"%wehub_process.pid)


def quit_WeHub_by_pid(wehub_pid):
    '''优雅地结束掉某一个wehub进程，如果强制kill进程会导致微信崩溃'''
    wehub_pipeName = r'\\.\\pipe\\WeHub'+str(wehub_pid)
    handle = win32file.CreateFile(wehub_pipeName, 
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,None)
    if handle==-1:
        print("connect pipe failed")
        return False
    res = win32pipe.SetNamedPipeHandleState(handle, None, None, None)
    if res == 0:
        print("SetNamedPipeHandleState return code: {res}")
        return False
    quit_cmd = "q".encode("ascii")
    win32file.WriteFile(handle,quit_cmd)
    handle.Close()
    return True

def quit_all_wehub():
    '''结束所有的wehub进程'''
    pid_list = get_wehub_pidList()
    threads=[]
    for pid in pid_list:
        t = threading.Thread(target=quit_WeHub_by_pid,args=(pid,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("quit_all_wehub success")

if __name__ =='__main__':
    #用法如下：
    #pids = get_wehub_pidList()
    #quit_WeHub_by_pid(pids[0])
    #quit_all_wehub()
    #openWeHub("test",r'http://localhost:5678/upload_file')
    print("it is a util script for WeHub")

