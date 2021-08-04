import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import functions as fn
#from bs4 import BeautifulSoup
import subprocess, roi_funcs, json, threading, statistics, time, webbrowser, os, re
import concurrent.futures

test_case = 1
name='MRANS'
version='0.1'

#  Class for tkinter Treeview and related functions
class result_window:

    def __init__(self, parent,stat, headings, name):
        # Draw a treeview of a fixed type
        # self.viewer=viewer
        self.stat = stat
        self.parent = parent
        # self.view_func = view_func
        self.fileList = []
        self.file_path = []
        self.tree = ttk.Treeview(self.parent, show='headings', columns=headings)
        self.tree.grid(sticky='NSEW')
        for n in range(len(name)):
            self.tree.heading(headings[n], text=name[n])
        self.tree.column(headings[0], width=30, stretch=tk.NO, anchor='e')
        self.tree.column(headings[1], width=400)


        self.tree.bind('<Button-1>',self.left_click)
        self.tree.bind('<Delete>', self.delete_entry)
        # self.tree.bind(('<Button-3>' ), self.double_left_click)
        self.tree.bind(('<Double-Button-1>'), self.double_left_click)
        # self.tree.bind(('w'), self.double_left_click)
        self.last_focus = None


    def display(self):

        self.delete()
        index = iid = 0
        self.abs=[]
        self.rel=[]
        for row in self.fileList:
            # print(row)
            inPath = row[0][1]

            # pvp = row[3]
            # pop = row[4]

            # p1 = inPath.relative_to(self.file_path)
            # disp = '  >>  '.join(p1.parts)


            self.tree.insert("", index, iid, values=(iid + 1, inPath))

            index = iid = index + 1


    # generate queue for processing
    def queue(self):
        fl = self.fileList
        # id = list(range(0, len(fl)))
        index = self.tree.selection()
        # if any items are selected, modify the file list to be processed
        if len(index) != 0:
            N = [int(i) for i in index]
            fl = [fl[j] for j in N]
            # id = N
        return fl
    # clears selection of all items in treeview
    def clear(self):
        for item in self.tree.selection(): self.tree.selection_remove(item)
        # self.viewer.clearFrame()

    def delete(self):
        self.tree.delete(*self.tree.get_children())

    # display status of a treeview item
    def status(self, iid, stsMsg):
        self.tree.set(iid, 'Status', stsMsg)
        self.parent.update_idletasks()

    def left_click(self, event):
        iid = self.tree.identify_row(event.y)

        self.clickID = iid
        if not iid == '':
            iid = int(iid)
            self.selection = self.fileList[iid][0]


    def double_left_click(self, event):
        iid = self.clickID
        if not iid == '':
            iid = int(iid)
            # self.selection = self.fileList[iid][0]
            self.view_func(self.selection)



    def delete_entry(self, event):
        iid = self.clickID
        if not iid == '':
            iid = int(iid)
            del self.fileList[iid]
            self.delete()
            self.display()
            self.clickID = ''


class MainArea(tk.Frame):
    def __init__(self, master,stat, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.stat = stat
        # self.config = config
        self.overwrite = tk.IntVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.master = master

        # Frame for all controls
        self.f0 = tk.Frame(self, borderwidth=1, relief='raised')
        # self.f0.pack(fill = "both")
        self.f0.grid(row=0, column=0, sticky='NSEW', columnspan=2)

        notebook =ttk.Notebook(self.f0)
        notebook.pack(expand = 1, fill = "both")

        # Frame for first level
        # self.f1 = tk.LabelFrame(notebook, text='Controls', borderwidth=1, padx=10, pady=10, relief='raised')
        self.fr_firstlv = tk.Frame(notebook)
        self.fr_firstlv.grid(row=0, column=0, sticky='NSEW', columnspan = 2)

        self.fr_higherlevel = tk.Frame(notebook, borderwidth=1, padx=10, pady=10, relief='raised')
        self.fr_higherlevel.grid(row=0, column=0, sticky='NSEW', columnspan=2)


        notebook.add(self.fr_firstlv, text ="First Level")
        notebook.add(self.fr_higherlevel, text="Higher Level Analysis")


        # Frame for File list Tree View
        self.fr_results = tk.Frame(self, borderwidth=0, relief='raised', pady=10, padx = 2)
        self.fr_results.grid(row=1, column=0, sticky='NSEW')
        self.fr_results.columnconfigure(0, weight=1)
        self.fr_results.rowconfigure(0, weight=1)

        # Frame for ROI Tree View
        self.fr_task_name = tk.Frame(self, borderwidth=0, relief='raised', pady=10, padx = 2)
        self.fr_task_name.grid(row=1, column=1, sticky='NSEW')
        # self.f3.columnconfigure(0, weight=.5)
        self.fr_task_name.rowconfigure(0, weight=1)

        # Individual elements
        # Display results and status
        self.result_tree = result_window(self.fr_results, stat, ['Number', 'Name', 'Status'], ['#', 'Name', 'Datasets'])
        # Display ROIs
        self.task_tree = result_window(self.fr_task_name, stat, ['Number', 'Name', 'Status'], ['#', 'Tasks', 'Status'])

        # Display results and status
        # self.result_tree = result_window(self.f2, viewer, stat)

        self.file_path = ''
        self.roi_path = ''

        # Controls
        el = fn.Elements(self.fr_firstlv)
        el.button("Database", self.selectPath, 1, 0, 0, tk.W + tk.E, 1)  # Selection of root directory
        el.button("Brain extraction", self.brain_extraction, '', 0, 2, tk.W + tk.E, 1)  # Brain extraction
        el.button("Process", self.process, '', 0, 4, tk.W + tk.E, 1)  # Process dataset
        el.button("Set Structural", self.set_structural, '', 4, 4, tk.W + tk.E, 1)  # Select dataset corresponding to
        # structural scan for BET and registration


        self.search_str = el.textField("Identifier", 20, 1, 0)  # Task or Dataset to be searched for
        self.filters = el.textField("Filters", 20, 1, 1)  # keywords to filter individual datasets
        self.analysis_name = tk.StringVar()
        # self.analysis_name.set('Hello')
        self.analysis_box = el.textField_var("Analysis Name", self.analysis_name, 20, 1, 3)  # Task or Dataset to be searched for

        el.button("Search", self.search, '', 3, 0, tk.N + tk.S, 1)  # button press to start search
        el.button("Clear", self.search, '', 3, 1, tk.N, 1)  # button press to clear selection
        # el.check('Overwrite', self.overwrite, 4, 1)  # checkbox for overwrite option

        ## Higher Level Analysis
        e2 = fn.Elements(self.fr_higherlevel)
        e2.button("Output Location", self.selectPath, 3, 0, 0, tk.W + tk.E, 1)  # Selection of output directory
        e2.button("Run Higher Level Analysis", self.higher_level, '', 0, 1, tk.W + tk.E, 1)  # Generate profile

        self.prevselection = '0'


#####  Main tasks ########################################
        # method for calling directory picker

    def selectPath(self, var):
        self.root = Path(__file__).parent.absolute()

        if test_case == 1:
            self.file_path = self.root/'test_data'
            self.higherlevel_directory = self.root/'test_data'/'grp_level'

        else:
            path = fn.appFuncs.selectPath()
            if var == 1:
                self.file_path = path
            if var == 2:
                self.roi_path = path
            if var == 3:
                self.higherlevel_directory = path

        self.result_tree.file_path = self.file_path
        self.stat.set('Selected Path: %s', self.file_path)
        # self.result_tree.file_path = self.file_path
        self.search_subjects()

    def search_subjects(self):
        self.subject_names = []
        self.subject_list = []
        for item in Path(self.file_path).iterdir():
            self.subject_names.append(item.name)
            self.subject_list.append([item, item.name])
        # print(self.subject_names)
        self.result_tree.fileList = self.aggregated_list(self.subject_list)
        self.result_tree.display()  # display the results
        self.search_tasks()

    def search_tasks(self):

        self.task_list = []
        for pa in self.result_tree.fileList:
            tasks =[]
            task_list = []

            scan = Path(pa[0][0]).rglob(f'*.nii*')
            tasks = [Path(t).name for t in scan]
            task_list += tasks

        for word in task_list:
            if word not in self.task_list:
                self.task_list.append(['', word])
        # print(self.task_list)

        self.task_tree.fileList = self.aggregated_list(self.task_list)
        self.task_tree.display()  # display the results

    def set_structural(self):
        self.structural_scan = [self.task_tree.selection[1], self.task_tree.clickID]
        self.task_tree.status(self.structural_scan[1], 'Structural')
        if not (self.prevselection == self.structural_scan[1]):
            self.task_tree.status(self.prevselection, '')
        self.prevselection = self.task_tree.clickID





    def brain_extraction(self):
        pass


    def generate_timecourse1(self):
        self.analysis_name.set(fn.appFuncs.generate_analysis_name(self.task_tree))

        self.subject_output = []
        # roi_name = self.roi_tree.selection_name
        self.output_dir_name = f'{self.analysis_name.get()}.feat'
        for row in self.result_tree.fileList:
            subject = row[0]
            output_dir = subject / self.output_dir_name
            self.subject_output.append(output_dir)
        # print(self.subject_output)
    #  generates time course for each user in the list
    def generate_timecourse(self):
        # self.analysis_name.set = f'PPI_{roi_name}.feat'

        roi = self.task_tree.selection
        roi_name = self.task_tree.selection_name
        self.analysis_name.set(fn.appFuncs.generate_analysis_name(self.task_tree))

        cluster_name_unbin = roi_name + '_unbin_native.nii.gz'
        cluster_name_bin = roi_name + '_bin_native.nii.gz'
        timecourse_name = f'timecourse_{roi_name}.txt'
        command_list = []



        for row in self.result_tree.fileList:
            file = row[0]
            subject = file
            # subject = Path(file).parent
            ex2std_mat = subject / 'reg' / 'example_func2standard.mat'
            mat_file = subject / 'reg' / 'standard2example_func_tr.mat'
            ref = subject/  'reg' /'example_func.nii.gz'
            ref_ffd = subject/'filtered_func_data.nii.gz'
            # print(f'File : {subject}    and cluster name unbin is {cluster_name_unbin}')

            transformation = ['convert_xfm', '-omat', mat_file, '-inverse', ex2std_mat]
            flirt = ['flirt', '-in', roi, '-init',mat_file, '-ref', ref, '-applyxfm', '-out',  subject/cluster_name_unbin]
            maths = ['fslmaths', subject/cluster_name_unbin, '-bin', subject/cluster_name_bin]
            meants = ['fslmeants', '-i', ref_ffd, '-o', subject/timecourse_name, '-m', subject/cluster_name_bin]

            command_list.append([transformation, flirt, maths, meants])

        self.threader(command_list)
        print('Timecourses Generated!')
        self.stat.set('Timecourses Generated!')
        self.analysis_name



    #  Allows user to create a custom design profile which can then be applied to all datasets
    def generate_profile(self):
        # use a sample profile to load the basics and
        # call FSL from here and run the FEAT tool.
        command_list = []
        command_list_sec = []
        self.subject_output=[]
        id = 1
        roi_name = self.task_tree.selection_name
        self.output_dir_name = f'{self.analysis_name.get()}.feat'
        for row in self.result_tree.fileList:
            subject = row[0]
            # output_dir = subject / f'PPI_{roi_name}.feat'
            output_dir = subject / self.output_dir_name
            subject_dir = subject / 'filtered_func_data'
            subject_timecourse = subject / f'timecourse_{roi_name}.txt'
            self.subject_output.append(output_dir)
            # out_ct = 1
            # while Path(output_dir).is_dir():
            #     output_dir = subject / f'{self.analysis_name.get()}_{out_ct}.feat'
            #     out_ct += 1

            if id == 1:
                sample_profile = self.root / 'sample_design.fsf'
                base_profile = self.root / 'temp' / 'temp_design.fsf'
                subprocess.run(['cp', sample_profile, base_profile])

                # read in the base profile
                files = [base_profile, output_dir, subject_dir, subject_timecourse]
                self.replace(files, 1)
                command = ['feat', base_profile]
                # command_list.append([command])
                # Open Feat setup in FSL with this reference file
                subprocess.run(['Feat', base_profile])
                # reverse the subject specific paths
                self.replace(files, 2)

            subject_profile = self.root / 'temp' / f'temp_{id}.fsf'
            subprocess.run(['cp', base_profile, subject_profile])
            # read in and modify the subject profile
            files = [subject_profile, output_dir, subject_dir, subject_timecourse]
            self.replace(files, 1)
            command = ['feat', subject_profile]
            command_list.append([command])

            reg = Path(subject)/'reg'
            reg_std = Path(subject)/'reg_standard'
            command = ['cp','-r', reg, reg_std, output_dir]
            command_list_sec.append([command])

            id += 1

        self.command_list_process = command_list
        self.command_list_sec_process = command_list_sec
        # print(command_list)

    def process(self):
        self.threader(self.command_list_process)
        # self.process_commands_seq(self.command_list_process)
        # empty the temp folder
        self.clear_dir(self.root/'temp')
        self.stat.set('Processing completed!')
        print('Processing completed!')
        self.process_commands_seq(self.command_list_sec_process)


    def higher_level(self):
        roi_name = self.task_tree.selection_name
        self.stat.set('Select location of output')
        # output_directory = fn.appFuncs.selectPath()
        higherlevel_directory = '/home/quest/Desktop/aNMT_pre_withICAaroma/PPI_grp_level/'
        output_dir = Path(self.higherlevel_directory)/roi_name
        self.stat.set('Output location set')

        subject_output = []
        for row in self.result_tree.fileList:
            subject = row[0]
            path = Path(subject)/f'{fn.appFuncs.generate_analysis_name(self.task_tree)}.feat'
            subject_output.append(path)

        number = len(self.result_tree.fileList)

        # Copy group design file to temp directory
        sample_profile = self.root / 'group_design.fsf'
        group_profile = self.root / 'temp' / 'temp_group_design.fsf'
        subprocess.run(['cp', sample_profile, group_profile])

        # Edit group design file
        with open(group_profile, "r+") as fin:
            data = fin.read()
            data = data.replace('#%#', str(output_dir))
            data = data.replace('#number', str(number))
            fin.write(data)

        ind = ['#$1', '#$2', '#$3']

        with open(group_profile, "r+") as fin:
            data = fin.readlines()

        data_insert_1=[]
        data_insert_2=[]
        data_insert_3=[]
        insert =[]

        for row in range(1,number+1):
            i = str(row)
            data_insert_1.append(f'# 4D AVW data or FEAT directory ({i})\n')
            data_insert_1.append(f'set feat_files({i}) "{subject_output[row-1]}"\n')
            data_insert_1.append(f'\n')

            data_insert_2.append(f'# Higher-level EV value for EV 1 and input {i}\n')
            data_insert_2.append(f'set fmri(evg{i}.1) 1\n')
            data_insert_2.append(f'\n')

            data_insert_3.append(f'# Group membership for input {i}\n')
            data_insert_3.append(f'set fmri(groupmem.{i}) 1\n')
            data_insert_3.append(f'\n')

        insert = [data_insert_1,data_insert_2,data_insert_3]

        for i in range(0,3):
            ind = data.index(f'#${i+1}\n')
            data = data[:ind] + insert[i] +data[ind+1:]

        with open(group_profile, "w") as fin:
            for line in data:
                fin.write(line)

        command = ['Feat',group_profile]
        subprocess.run(command)


    @staticmethod
    def list2str(list):
        # initialize an empty string
        str1 = ""

        # traverse in the string
        for ele in list:
            str1 += ele

            # return string
        return str1

    #####  Filtering results ########################################
    def apply_omit(self,file_list):
        filters = self.search_omit
        if len(filters) != 0:
            filters = filters
            fl = [row for row in file_list if ~any(f in str(row) for f in filters)]
        else:
            fl = file_list
        return fl

    def apply_filters(self, file_list):
        filters = self.filters.get()
        if len(filters) != 0:
            filters = filters.split(";")
            fl = [row for row in file_list if any(f in str(row) for f in filters)]
        else:
            fl = file_list
        return fl

    def aggregated_list(self, filtered_list):
        fl = []
        for row in filtered_list:
            fl.append([row, 1])
        return fl

################################################################
    @staticmethod
    def replace(files, type):
        profile = files[0]
        output_dir = files[1]
        subject_dir = files[2]
        subject_timecourse = files[3]

        fin = open(profile, "rt")
        data = fin.read()

        if type ==1:
            data = data.replace('#%#', str(output_dir))
            data = data.replace('#$#', str(subject_dir))
            data = data.replace('#!#', str(subject_timecourse))
        else:
            print(subject_dir)
            data = data.replace(str(output_dir), '#%#')
            data = data.replace(str(subject_dir), '#$#')
            data = data.replace(str(subject_timecourse), '#!#')
        fin.close()

        fin = open(profile, "wt")
        fin.write(data)
        fin.close()

    def clear_dir(self,dir_path):
        [Path.unlink(e) for e in dir_path.iterdir()]

    def clear_frame(self,frame):
        for widget in frame.winfo_children():
           widget.destroy()

    def threader(self,queue):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.process_commands, queue)

    def process_commands(self, command):
        for f in command:
            subprocess.run(f)

    def process_commands_seq(self, command):
        for a in command:
            for f in a:
                subprocess.run(f)

#-----------------------------------------------------------------------------------------------------------------------

class StatusBar(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief='sunken', anchor='w')
        self.label.pack(fill=tk.X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

#-----------------------------------------------------------------------------------------------------------------------

class MainApp(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        parent.title(name)
        parent.minsize(800,500)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # Components
        # self.viewer = fn.Viewer(viewer_root)
        # self.menubar = Menubar(parent,self.config)
        self.statusbar = StatusBar(parent)
        self.mainarea = MainArea(parent, self.statusbar,  borderwidth=1, relief=tk.RAISED)

        # configurations
        self.mainarea.grid(column=0, row=0, sticky='WENS')
        self.statusbar.grid(column=0, row=1, sticky='WE')
        self.statusbar.set('Ready')

#-----------------------------------------------------------------------------------------------------------------------


root = tk.Tk()
PR = MainApp(root)
root.mainloop()