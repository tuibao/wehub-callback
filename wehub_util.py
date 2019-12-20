import psutil
import subprocess,time
import win32api
import win32con
import win32file
import win32pipe
import win32event
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
    process_handle = None
    pipe_handle = None
    wehub_pipeName = r'\\.\\pipe\\WeHub'+str(wehub_pid)
    try:
        process_handle  = win32api.OpenProcess(win32con.SYNCHRONIZE,False,wehub_pid)
        pipe_handle = win32file.CreateFile(wehub_pipeName, 
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,None)
        win32pipe.SetNamedPipeHandleState(pipe_handle, None, None, None)
        quit_cmd = "q".encode("ascii")
        if win32file.WriteFile(pipe_handle,quit_cmd):
             print("quit_cmd have sent")

        if process_handle:
            #等待进程退出
            print("wait for wehub[%d] terminate..."%wehub_pid)
            win32event.WaitForSingleObject(process_handle, 5000)
            print("wehub[%d] exited"%wehub_pid)
    except Exception as e:
        raise e
    finally:
        if pipe_handle:
            pipe_handle.Close()
        if process_handle:
            process_handle.Close()

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
    #quit_WeHub_by_pid(9492)
    #quit_all_wehub()
    #openWeHub("test",r'http://localhost:5678/upload_file')
    print("it is an util script for WeHub")

