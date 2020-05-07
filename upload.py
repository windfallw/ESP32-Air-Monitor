import pyboard
import time
import os


def uploadFile(src, dest=None):
    time_start = time.time()
    if dest:
        print('upload:   {0}  --------->  {1}   '.format(src, dest), end='')
        pyb.fs_put(src, dest)
    else:
        print('upload:   {0}  --------->  {0}   '.format(src), end='')
        pyb.fs_put(src, src)
    time_end = time.time()
    print('finish in {0} s'.format(time_end - time_start))


def uploadFolder(folderPath, folderDest=None):
    for filename in os.listdir(folderPath):
        if folderDest:
            src = folderPath + filename
            dest = folderDest + filename
            uploadFile(src, dest)
        else:
            src = folderPath + filename
            uploadFile(src)


if __name__ == '__main__':
    print('\033[1m')

    device = 'COM7'
    pyb = pyboard.Pyboard(device)
    pyb.enter_raw_repl()

    try:
        pyb.fs_mkdir('py')
    except pyboard.PyboardError as e:
        print('pyboard.PyboardError:', e)

    try:
        pyb.fs_mkdir('www')
    except pyboard.PyboardError as e:
        print('pyboard.PyboardError:', e)

    try:
        pyb.fs_mkdir('src')
    except pyboard.PyboardError as e:
        print('pyboard.PyboardError:', e)

    print('\nALL file')
    pyb.fs_ls('/')
    print('\npy Folder')
    pyb.fs_ls('py')
    print('\nsrc Folder')
    pyb.fs_ls('src')
    print('\nwww Folder')
    pyb.fs_ls('www')

    # pyb.fs_rm('config.json')

    # uploadFile('boot.py')
    uploadFile('main.py')
    uploadFile('py/device.py')
    # uploadFile('py/Webclient.py')
    # uploadFile('py/Webserver.py')

    # uploadFile('www/index.html')
    # uploadFile('src/setchart.js')
    # uploadFile('src/setmap.js')

    # uploadFolder('py/')
    # uploadFolder('src/')
    # uploadFolder('www/')

    pyb.exit_raw_repl()
    pyb.close()
