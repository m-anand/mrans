import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import subprocess, json, threading, statistics, time, webbrowser, os, re
import concurrent.futures


# helper class for common gui widgets
class Elements:
    def __init__(self, master):
        self.master = master

    # method for all button processes
    def button(self, char, funct, lambdaVal, x_, y_, algn, rows):
        if lambdaVal == '':
            self.b = tk.Button(self.master, text=char, command=funct)
        else:
            self.b = tk.Button(self.master, text=char, command=lambda: funct(lambdaVal))
        self.b.grid(row=y_, column=x_, sticky=algn, rowspan=rows, ipadx=5, ipady=5)

    # method for calling a text entry dialog
    def textField(self, lbl, w_, x_, y_):
        textField = tk.Entry(self.master, width=w_)
        textField.grid(row=y_, column=x_ + 1, sticky=tk.W, ipadx=5, ipady=5)
        textField_lbl = tk.Label(self.master, text=lbl)
        textField_lbl.grid(row=y_, column=x_, sticky=tk.E, ipadx=5, ipady=5)
        return textField

    def textField_var(self, lbl,var, w_, x_, y_):
        textField = tk.Entry(self.master, textvariable=var, width=w_)
        textField.grid(row=y_, column=x_ + 1, sticky=tk.W, ipadx=5, ipady=5)
        textField_lbl = tk.Label(self.master, text=lbl)
        textField_lbl.grid(row=y_, column=x_, sticky=tk.E, ipadx=5, ipady=5)
        return textField

    def check(self, char, var, x_, y_):
        check = tk.Checkbutton(self.master, text=char, variable=var)
        check.grid(column=x_, row=y_)

    def label1(self, char, x_, y_, algn, rows, cols):
        self.b = tk.Label(self.master, text=char)
        self.b.grid(row=y_, column=x_, sticky=algn, rowspan=rows, columnspan=cols)

    def label2(self, charVariable, x_, y_, algn):
        b = tk.Label(self.master, textvariable=charVariable)
        b.grid(row=y_, column=x_, sticky=algn)
        return b


    def popupMenu(self, charVariable,choices,x_,y_,width,stick):
        popupMenu=tk.OptionMenu(self.master, charVariable, *choices)
        popupMenu.configure(width=width)
        popupMenu.grid(row=y_, column=x_, sticky=stick)
        # self.labelMenu=tk.Label(self.master,text=label)
        # self.labelMenu.grid(row=y_, column=x_-1)


class appFuncs:
    @staticmethod
    def thread(*args):
        n=1
        for i in args:
            if n==0:
               self = i
            if n==1:
                command = i
            if n==2:
                is_daemon = i
            n+=1
        # self.update_idletasks()
        x = threading.Thread(target=subprocess.run, args=[command])
        x.daemon = is_daemon
        x.start()

    def process(self,command):
        subprocess.run(command)


    # Generates file dialog box
    @staticmethod
    def selectPath():
        file_path = '' #todo replace with current path
        f = tk.filedialog.askdirectory()
        if f != '':
            file_path = f
        return file_path

    @staticmethod
    def select_file(title):
        file_path = ''
        f = tk.filedialog.askopenfilename(title=title, filetypes =(("NIFTI files","*.nii.gz*"),("all files","*.*")))
        if f != '':
            file_path = f
        return file_path

        # generates output folder path
    @staticmethod
    def generate_analysis_name(roi_tree):
        roi_name = roi_tree.selection_name
        name = f'PPI_{roi_name}'
        return name


    # generates output folder path
    @staticmethod
    def generateOutpath(inPath, prefix, suffix):
        z=inPath.stem.replace(prefix,'');  z=z+suffix
        outPath = (Path(inPath).parent) / z
        return outPath

    @staticmethod
    def generateProcessedOutpath(path):
        fo=Path(path).glob('*.feat')
        processedOutpath=''
        for i in fo:
           processedOutpath=i
        return processedOutpath

    # Identify previously processed datasets
    @staticmethod
    def prevProcessed(outPath):
        pvp = 0
        if Path(outPath).is_dir(): pvp = 1
        return pvp

    @staticmethod
    def postProcessed(path):
        # idenitfy if the dataset has been processed through ICA and post-processed as well
        pop = 0
        # is feat file present?
        # print(path)
        fo=Path(path).glob('*.feat')
        for i in fo:
            if i.is_dir() == True:
                pop = 1
        return pop

    @staticmethod
    def postProcessed_identifier(path):
        # if melodic.ica is a sibling directory, then this is assumed to be post-processed dataset generated from
        # ICA-AROMA processed data
        pop_i = 0
        fo = Path(path).parent/'melodic.ica'
        if fo.is_dir() == True: pop_i = 1
        return pop_i

    @staticmethod
    def write_to_file(file_obj,text,loc):
        pass




class Viewer:

    def __init__(self,parent):
        self.parent = parent
        parent.protocol("WM_DELETE_WINDOW", self.do_nothing)
        parent.minsize(300, 400)
        self.parent.title(': Image Viewer')
        self.fr = tk.Frame(parent,borderwidth=1, padx=20,pady=10)
        self.fr.pack(fill = "both", expand = True)

    def display(self, im_list, mode):
        self.clearFrame(self.fr)

        # Unprocessed viewer
        if mode == 1:
            self.main_im_list = im_list
            self.labels = ['Psychological', 'Physiological', 'Interaction (Pos)', 'Interaction (Neg)']
            frame = self.fr
            self.main_image_viewer(frame)

        # Processed but not post processed
        if mode == 2:
            frame = self.fr
            self.IC_im_list = im_list
            self.scroll_viewer_setup(frame)
            self.scroll_viewer()


    def main_image_viewer(self, frame):
        el = Elements(frame)
        for i in range(0, len(self.main_im_list)):
            el.label1(self.labels[i], 0, 2*i, 'nesw', 1, 1)
            self.fr.rowconfigure(2*i+1, weight=1)
            im_path = self.main_im_list[i]
            photo = tk.PhotoImage(file=im_path)
            label = tk.Label(frame, image=photo, pady=20)
            label.photo = photo
            label.grid(row=2*i+1)


    def scroll_viewer_setup(self,fr):
        self.ic = len(self.IC_im_list)
        self.j = 0
        self.count = tk.StringVar()
        self.count.set(f'{self.j + 1} of {self.ic} Motion associated independent components')
        el = Elements(fr)
        el.button('Previous', self.scroll, -1, 0, 0, 'e', 1)
        el.button('  Next  ', self.scroll, 1, 1, 0, 'w', 1)
        el.label2(self.count, 2, 0, 'w')
        self.frame_scroll = tk.Frame(fr, borderwidth=1,  padx=20, pady=10)
        self.frame_scroll.grid(row=1, columnspan=10, sticky='nsew')


    def scroll(self, scr):
        self.j += scr
        if (self.j >= self.ic):
            self.j = self.ic-1
        if self.j<0:
            self.j = 0
        self.count.set(f'{self.j + 1} of {self.ic} components')
        self.clearFrame(self.frame_scroll)
        self.scroll_viewer()

    def scroll_viewer(self):
        ic_im_path = self.IC_im_list[self.j]
        photo = tk.PhotoImage(file=ic_im_path)
        label = tk.Label(self.frame_scroll, image=photo, pady=20)
        label.photo = photo
        label.grid(row=0, sticky='nsew')

    def clearFrame(self,frame):
        # destroy all widgets from frame
        for widget in frame.winfo_children():
           widget.destroy()

    @staticmethod
    def do_nothing():
        pass
