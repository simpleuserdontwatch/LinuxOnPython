from tkinter import *
import traceback,os,sys,pickle
from datetime import datetime
from tkinter import simpledialog as sd
from tkinter import filedialog as fd
from io import StringIO
from contextlib import redirect_stdout
from tkinter import messagebox
newline = '\n'
hz = 50
def addfiles():
    global output
    path = fd.askopenfilename(title="Add a file to emulator")
    if path:
        with open(path) as f:
            filesystem["upload"][os.path.basename(f.name)] = f.read()
        output += f'\n"{os.path.basename(f.name)}" uploaded'
def getfiles():
    global output
    path = sd.askstring('File?', f'What file do you want to get?\n{newline.join(curdir.keys())}')
    if path:
        with open(path, 'a+') as f:
            f.write(curdir[path])
        output += f'\n"{path}" was pulled'
def clear():
    global output
    output = ''
def exitfs():
    C.config(cursor="")
    root.attributes('-fullscreen', False)
    root.update()
def fullscreen():
    root.attributes('-fullscreen', True)
    C.config(cursor="none")
    root.update()
def set_fs():
    if root.attributes('-fullscreen'):
        exitfs()
    else:
        fullscreen()
def setwin():
    root.geometry("480x320")
def hhdsave():
    path = fd.asksaveasfilename(title="Save hhd image", filetypes=[("Hard disk image", '*.hhd'),("Any file", '*.*')])
    if path:
        with open(path, 'a+b') as f:
            pickle.dump(filesystem,f)
root = Tk()
if "-5hz" in sys.argv:
    hz = 5
if "-h" in sys.argv:
    root.destroy()
    print('Syntax: python pytest.py [-hhd=<*.hhd>] [Other arguments]')
    print('Arguments: ')
    print('-5hz - Make display refreshing more faster')
    print('-f - Fullscreen at start')
    print('-nomenu - Disables emulator right-click menu')
    print('-hhd=<*.hhd> - Restores a virtual file system')
    sys.exit()
fontadaption = BooleanVar()
addfile = Menu(tearoff=0)
addfile.add_command(label="========Options========")
addfile.add_command(label="Exit", command=root.destroy)
addfile.add_command(label="Add file to emulator", command=addfiles)
addfile.add_command(label="Get file from emulator", command=getfiles)
addfile.add_command(label="Clear output", command=clear)
addfile.add_command(label="Restore original window size", command=setwin)
addfile.add_command(label="Toggle Fullscreen", command=set_fs)
addfile.add_checkbutton(label="Font adaption", onvalue=1, offvalue=0, variable=fontadaption)
addfile.add_command(label="Save HHD image", command=hhdsave)
def do_popup(event):
    try:
        if not ("-nomenu" in sys.argv):
            addfile.tk_popup(event.x_root, event.y_root)
    finally:
        addfile.grab_release()
root.bind('<Button-3>', do_popup)
filesystem = {"home":
              {"user": {}},
              "etc": {"hostname": "LinuxOnPython", ".prefix": "$ "},
              "bin": {"cd": "011000100110100101101110011000010111001001111001",
                      "hostname": "011000100110100101101110011000010111001001111001",
                      "dosshell": "011000100110100101101110011000010111001001111001",
                      "pwd": "011000100110100101101110011000010111001001111001",
                      "python": "011000100110100101101110011000010111001001111001",
                      "exec": "011000100110100101101110011000010111001001111001",
                      "help": "011000100110100101101110011000010111001001111001",
                      "ver": "011000100110100101101110011000010111001001111001",
                      "addonhelp": "011000100110100101101110011000010111001001111001",
                      "date": "011000100110100101101110011000010111001001111001",
                      "cat": "011000100110100101101110011000010111001001111001",
                      "rm": "011000100110100101101110011000010111001001111001",
                      "ls": "011000100110100101101110011000010111001001111001",
                      "help": "011000100110100101101110011000010111001001111001",
                      "rename": "011000100110100101101110011000010111001001111001",
                      "clear": "011000100110100101101110011000010111001001111001",},
              "tmp": {},
              "upload": {},
              "dev": {"sda1": "010101110101010111010101011101"*10,
                      "null": "    "*10,
                      "random": "010101110101010111010101011101"*10,
                      "tty": "010101110101010111010101011101"*10,
                      "ttyS0": "010101110101010111010101011101"*10,
                      "console": "010101110101010111010101011101"*10},
              "scripts": {"helloworld": """
global output
output+='Hello, World!'""",}
              }
try:
    if "-hhd" in sys.argv[1]:
        with open(' '.join(sys.argv[1].split('=')[1:]), 'rb') as f:
                filesystem = pickle.load(f)
except: pass
pwd = '/home/user/'
curdir = filesystem['home']['user']
lastdir = [filesystem,filesystem['home']]
curstate = False
temp = None
temp2 = None
env = {'HOME': '/home/user/', 'HOSTNAME': '/etc/hostname', 'BIN': '/bin/', 'SCRIPTS': '/scripts/'}
def processkey(event):
    global inp, output, win, curdir, lastdir, filesystem, pwd, temp, temp2
    if event.keysym == 'BackSpace':
        inp = inp[0:len(inp)-1]
    elif event.keysym != 'Return':
        inp += event.char
        if logger:
            print(event.char,end='')
    elif event.char == '':
        inp = inp[0:len(inp)-2]
    elif event.keysym == 'Return':
        try:
            if logger:
                print()
            cmdandargs = inp.split()
            cmd = ''.join(cmdandargs[0:1])
            args = cmdandargs[1:]
            if not (cmd == '' or cmd[0:1] == ' '):
                output+='\n'+pwd.replace(homedir, '~/')+filesystem['etc']['.prefix']+inp+'\n'
            else:
                output+='\n'+pwd.replace(homedir, '~/')+filesystem['etc']['.prefix']+inp
                return
            inp=''
            print(cmd, args)
            if cmd == 'cd':
                if args[0] == '/':
                    lastdir = []
                    curdir = filesystem
                    pwd = '/'
                elif args[0] in curdir.keys():
                    if type(curdir[args[0]]) == dict:
                        lastdir.append(curdir)
                        curdir = curdir[args[0]]
                        pwd += args[0] + '/'
                    else:
                        output += 'E: Not a directory'
                elif args[0] == '..':
                    try:
                        curdir = lastdir[-1]
                        del lastdir[-1]
                        pwd = '/'.join(pwd.split('/')[:-2]) + '/'
                    except:
                        output+='E: No last directories found'
                elif args[0][0] == '$':
                    lastdir.clear()
                    temp = filesystem
                    pwd = '/'
                    for i in env[args[0][1:]].split('/')[1:-1]:
                        lastdir.append(temp)
                        temp = temp[i]
                        print(temp, i)
                        pwd += i + '/'
                    curdir = temp
                else:
                    output += 'E: Directory doesnt exist!'
            elif cmd == 'dir' or cmd == 'ls':
                print(curdir.keys())
                output += '\n'.join(curdir.keys())
            elif cmd == 'pwd':
                output += pwd
            elif cmd == 'var':
                for k, v in env.items():
                    output += f'${k} = "{v}"\n'
            elif cmd == 'mkdir':
                try:
                    curdir[args[0]] = {}
                except:
                    output += 'E: No argument has been provided'
            elif cmd == 'cat':
                try:
                    if args[0] in curdir.keys():
                        if type(curdir[args[0]]) == str:
                            print(curdir[args[0]])
                            output += curdir[args[0]]
                        else:
                            output += "E: File you provided is a directory!"
                    elif args[0][0] == '$':
                        temp = filesystem
                        for i in env[args[-1][1:]].split('/')[1:-1]:
                            temp = temp[i]
                            print(temp, i)
                        print(temp[env[args[0][1:]].split('/')[-1]])
                        output += temp[env[args[0][1:]].split('/')[-1]]
                    else:
                        if args[0][0] == '/':
                            temp = filesystem
                            for i in args[-1].split('/')[1:-1]:
                                temp = temp[i]
                                print(temp, i)
                            output += temp[args[0].split('/')[-1]]
                            print(temp[args[0].split('/')[-1]])
                        else:
                            output += 'E: File doesnt exist!'
                except:
                    output+="E: Must provide a file!"
            elif cmd == 'echo':
                try:
                    if args[-2] == '>':
                        if args[-1][0] != '/' and args[-1][0] != '$':
                            curdir[args[-1]] = ' '.join(args[:-2])
                        elif args[-1][0] == '$':
                            temp = filesystem
                            for i in env[args[-1][1:]].split('/')[1:-1]:
                                temp = temp[i]
                                print(temp, i)
                            temp[env[args[-1][1:]].split('/')[-1]] = ' '.join(args[:-2])
                        else:
                            temp = filesystem
                            for i in args[-1].split('/')[1:-1]:
                                temp = temp[i]
                                print(temp, i)
                            print(temp)
                            temp[args[-1].split('/')[-1]] = ' '.join(args[:-2])
                            print(temp)
                except: pass
                if not args[0][0] == '$':
                    output += ' '.join(args)
                else:
                    output += env[args[0][1:]]
            elif cmd == 'touch':
                try:
                    if args[-1][0] != '/':
                        curdir[args[-1]] = ''
                    else:
                        temp = filesystem
                        for i in args[-1].split('/')[1:-1]:
                            temp = temp[i]
                            print(temp, i)
                        print(temp)
                        temp[args[-1].split('/')[-1]] = ''
                        print(temp)
                except: pass
            elif cmd == 'mv':
                try:
                    temp2 = curdir[args[0]]
                    del curdir[args[0]]
                    temp = filesystem
                    for i in args[-1].split('/')[1:-1]:
                        temp = temp[i]
                        print(temp, i)
                    temp[args[0]] = temp2
                    print(temp, temp2)
                except: pass
            elif cmd == 'cp':
                try:
                    temp2 = curdir[args[0]]
                    temp = filesystem
                    for i in args[-1].split('/')[1:-1]:
                        temp = temp[i]
                        print(temp, i)
                    temp[args[0]] = temp2
                    print(temp, temp2)
                except: pass
            elif cmd == 'hostname':
                output += filesystem['etc']['hostname']
            elif cmd == 'rm':
                try:
                    if args[0] in curdir.keys():
                        del curdir[args[0]]
                    else:
                        output+="E: File or directory doesnt exist!"
                except:
                    output+="E: Must provide a file!"
            elif cmd == 'rename':
                try:
                    if args[0] in curdir.keys():
                        curdir[args[1]] = curdir[args[0]]
                        del curdir[args[0]]
                    else:
                        output+="E: File or directory doesnt exist!"
                except:
                    output+="E: Must provide a file!"
            elif cmd == 'dosshell':
                output+="E: Already running dosshell!"
            elif cmd == 'date':
                output += datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            elif cmd == 'python':
                try:
                    if args[0] in curdir:
                        f = StringIO()
                        with redirect_stdout(f):
                            try:
                                exec(curdir[args[0]])
                            except:
                                print(traceback.format_exc())
                        outputut += f.getvalue()
                    else:
                        output += 'E: File doesnt exist!'
                except:
                    output += 'E: No file provided!'
            elif cmd == 'exec':
                try:
                    if args[0] in curdir:
                        try:
                            exec(curdir[args[0]])
                        except:
                            output += traceback.format_exc()

                    else:
                        output += 'E: File doesnt exist!'
                except:
                    output += 'E: No file provided!'
            elif cmd == 'sethostname':
                filesystem['etc']['hostname'] = ' '.join(args)
                output+=f'Hostname was changed to {" ".join(args)}'
            elif cmd == 'clear':
                output = ''
            elif cmd == 'ver':
                output += 'Operating system: LinuxOnPython 0.1\nShell: MSDOS mode shell'
            elif cmd == 'res':
                output += f"{root.winfo_width()}x{root.winfo_height()}"
            elif cmd == "shutdown":
                root.destroy()
            elif cmd == 'help':
                output += """List of commands
help - Shows this
mv <file> <full path> - Moves a file to location
cp <file> <full path> - Copies a file to location
touch <file> - Creates a file
rm <File> - Removes a file
hostname - Prints your host name located in /etc/hostname
echo <String> - Prints a string or creates a file
cat <File> - Prints a file
dir, ls - Prints what is in current directory
cd <Directory | ..> - Goes into a directory
date - Today's date
pwd - Prints where you are
mkdir <name> - Makes a empty directory
rename <file> <new file> - Renames a file
pwd - Prints where you are
mkdir <name> - Makes a empty directory
rename <file> <new file> - Renames a file
exec <file> - Execute a script file (python)
clear - Clears screen
ver - Version of LinuxOnPython
shutdown - Shutdowns computer
var - Gets list of all declared variables
addonhelp - Unofficial commands
"""
            elif cmd == 'addonhelp':
                output += """Addon list
sethostname <Name> - Sets hostname
clear - Clears screen
python <file> - Python interpretter (Note: no python shell)
res - Gets resolution
dosshell - The shell LinuxOnPython runs on"""
            elif cmd[0] == '$' and args[0] == '=':
                env[cmd[1:]] = ' '.join(args[1:])
                print(env)
            elif cmd in filesystem["scripts"]:
                exec(filesystem["scripts"][cmd])
            else:
                output += f'E: Unknown command "{cmd}"'
            filesystem["tmp"]["temp"] = str(temp)
            filesystem["tmp"]["temp2"] = str(temp2)
            filesystem["dev"]["console"] = str(output)
        except:
            output += traceback.format_exc()
root.title(f'LinuxOnPython emulator')
root.geometry("480x320")
root.iconbitmap('linux.ico')
#--Font section--
fontsiz = 10 # Font size
fontnam = "Terminal" # Font name
fontcol = "#cdcdcd" # Font color
fontsty = '' # Font style
fontadapt = False # Automatically adapts font to your window size
fontsizbackup = fontsiz # Dont touch (font size backup to restore font size on font adaption disable)
padx = 3 # Padding of text X
pady = 3 # Padding of text Y
homedir = '/home/user/' # Home directory, if pwd is same as this variable, it transforms into ~
#----------------

#-Welcome screen-
welcome = 'Welcome to LinuxOnPython!\nToday date is '+datetime.today().strftime('%Y-%m-%d')
#----------------

#------Misc------
skipboot = False # Skips boot screen, no longer need to wait
logger = False # Prints what letter was pressed
#----------------
C = Canvas(bg='#060606', highlightthickness=0, width=480, height=320)
C.pack(fill=BOTH, expand=True)
output = "Simple bios ver 1.0\nPress F5 for setup. (aborted)\nBooting the Pykernel..\t\t[Done]\nStarting the init process\nINIT: Allocating 4mb of ram for shell...  [Done]\nINIT: Starting shell..\n" + welcome
inp = ''
win = False
if "-f" in sys.argv:
    set_fs()
def update():
    global output,fontsiz
    C.delete('all')
    if curstate:
        C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty),
            text=output.replace('\\', '/')+'\n'+pwd.replace(homedir, '~/')+filesystem['etc']['.prefix']+inp.replace('\\', '/')+'_', anchor="nw", tags="out")
    else:
        C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty),
            text=output.replace('\\', '/')+'\n'+pwd.replace(homedir, '~/')+filesystem['etc']['.prefix']+inp.replace('\\', '/'), anchor="nw", tags="out")
    if C.bbox('out')[3] > C.winfo_height():
        output = '\n'.join(output.splitlines()[1:])
    root.after(hz,update)
def updcur():
    global curstate, fontsiz
    curstate = not curstate
    root.after(400,updcur)
def fakeboot():
    C.delete('all')
    C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty), text="Simple bios ver 1.0\nPress F5 for setup.", anchor="nw")
    root.after(1000,fakeboot01)
def fakeboot01():
    C.delete('all')
    C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty), text="Simple bios ver 1.0\nPress F5 for setup. (aborted)\nBooting the Pykernel..", anchor="nw")
    root.after(500,fakeboot1)
def fakeboot1():
    C.delete('all')
    C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty), text="Simple bios ver 1.0\nPress F5 for setup. (aborted)\nBooting the Pykernel..\t\t[Done]", anchor="nw")
    root.after(800,fakeboot2)
def fakeboot2():
    C.delete('all')
    C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty), text="Simple bios ver 1.0\nPress F5 for setup. (aborted)\nBooting the Pykernel..\t\t[Done]\nStarting the init process", anchor="nw")
    root.after(1000,fakeboot3)
def fakeboot3():
    C.delete('all')
    C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty), text="Simple bios ver 1.0\nPress F5 for setup. (aborted)\nBooting the Pykernel..\t\t[Done]\nStarting the init process\nINIT: Allocating 4mb of ram for shell...", anchor="nw")
    root.after(1500,fakeboot4)
def fakeboot4():
    C.delete('all')
    C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty), text="Simple bios ver 1.0\nPress F5 for setup. (aborted)\nBooting the Pykernel..\t\t[Done]\nStarting the init process\nINIT: Allocating 4mb of ram for shell...  [Done]", anchor="nw")
    root.after(500,fakeboot5)
def fakeboot5():
    C.delete('all')
    C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty), text="Simple bios ver 1.0\nPress F5 for setup. (aborted)\nBooting the Pykernel..\t\t[Done]\nStarting the init process\nINIT: Allocating 4mb of ram for shell...  [Done]\nINIT: Starting shell..", anchor="nw")
    root.after(1000,update)
    updcur()
def updatefont():
    global fontsiz, fontadapt, fontadaption
    if fontadapt or fontadaption.get():
        fontsiz = round(((root.winfo_height() * 0.55) + (root.winfo_width() * 0.55))*0.019)
    else:
        fontsiz = fontsizbackup
    root.after(10,updatefont)
if not skipboot:
    C.create_text(padx,pady,fill=fontcol,font=(fontnam, fontsiz, fontsty), text="Simple bios ver 1.0", anchor="nw")
    root.after(900,fakeboot)
else:
    output = 'Boot screen aborted.'
    root.after(100,update)
    updcur()
root.after(10,updatefont)
root.bind('<Key>', processkey)
root.mainloop()
