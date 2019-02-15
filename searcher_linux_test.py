import os
import subprocess
import multiprocessing
import sys
import tkinter
from tkinter import filedialog

def searcher(arg_list):
    filename = arg_list[0]
    search_string = arg_list[1]
    found = {}
    if '.pdf' in filename:
        with open(filename, 'rb') as file:
            pdfReader = PyPDF2.PdfFileReader(file)
            for page in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(page)
                page_text = pageObj.extractText().lower()
                if search_string in page_text:
                    if not filename in found:
                        found[filename] = []
                    found[filename].append(page+1)
    else:
        try:
            raw_text = ''
            with open(filename, 'r') as file:
                raw_text = file.read().lower()
        except:
            print(f'worker crashed on {filename}')
        if search_string in raw_text:
            found[filename] = 0
    print(f'Worker has searched {filename}')
    return found

if __name__ == "__main__":
    global search_string
    global dirname
    cwd = os.getcwd()
    root = tkinter.Tk()
    root.withdraw()
    dirname = filedialog.askdirectory(parent=root,initialdir=cwd,title='Please select a directory')
    os.chdir(dirname)
    found = {}
    path, dirs, files = next(os.walk(dirname))
    file_count = len(files)
    search_string = input('String to search in files: ').lower()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # chdir(foldername(script_location))
    file_list = []
    file_counter = 0
    for path, subdirs, files in os.walk(dirname):
        for filename in files:
            file_list.append([path+'/'+filename, search_string])
            file_counter += 1
    print(f'{file_counter} files')
    pool = multiprocessing.Pool(10)
    results = pool.map(searcher, file_list)
    for output in results:
        for i in output:
            found[i] = output[i]

    print('') # Clear '\r'
    if len(found) != 0:
        print('FILENAME: PAGE_NR (if pdf)')
        print('Matches:')
        for i, match in enumerate(found):
            print(f'({i}) {match}, page: {found[match]}')
    else:
        print('No matches found')
        quit()
    while True:
        try:
            choose_open = input('Choose which to open: ')
        except:
            print("quitting...")
            quit()
        if choose_open == 'q':
            quit()
        elif choose_open == '--list':
            for i, match in enumerate(found):
                print(f'({i}) {match}, page: {found[match]}')
            continue
        try:
            choosen = int(choose_open)
        except:
            continue
        if choosen >= len(found) or choosen < 0:
            print('Not a file')
            continue

        os.chdir(dirname) # Reset
        for i, match in enumerate(found):
            if i == choosen:
                if '.pdf' in match:
                    print(f'Pages: {found[match]}')
                    page_choose = input('Which page: ')
                    process =  subprocess.Popen([r'C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader/AcroRd32.exe',
                                                 '/n', '/A',
                                                 'page=' + str(page_choose),
                                                 match],
                                                shell=False,
                                                stdout=subprocess.PIPE)
                    #process.wait()
                else:
                    if sys.platform == "win32":
                        os.startfile(match)
                    else:
                        opener ="open" if sys.platform == "darwin" else "xdg-open"
                        subprocess.call([opener, match])
