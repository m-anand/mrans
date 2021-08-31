import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import functions as fn
from bs4 import BeautifulSoup
import subprocess, csv, json, threading, statistics, time, webbrowser, os, re
import concurrent.futures

test_case = 0
name='MRANS'
version='0.1'

#  Class for tkinter Treeview and related functions
class result_window:

    def __init__(self, parent,stat, headings, name, view_func):
        # Draw a treeview of a fixed type
        # self.viewer=viewer
        self.stat = stat
        self.parent = parent
        self.view_func = view_func
        self.fileList = []
        self.file_path = []
        self.tree = ttk.Treeview(self.parent, show='headings', columns=headings)
        self.tree.grid(row=0, column=0, sticky='NSEW')
        s = ttk.Style()
        s.configure('Treeview',rowheight=30)

        for n in range(len(name)):
            self.tree.heading(headings[n], text=name[n])
        self.tree.column(headings[0], width=30, stretch=tk.NO, anchor='e')
        self.tree.column(headings[1], width=500)


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
            self.current_selection = self.fileList[iid][0]


    def double_left_click(self, event):
        iid = self.clickID
        if not iid == '':
            iid = int(iid)
            # self.selection = self.fileList[iid][0]
            self.view_func(self.current_selection)



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

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.master = master

        # Frame for all controls
        self.f0 = tk.Frame(self, borderwidth=1, relief='raised')
        # self.f0.pack(fill = "both")
        self.f0.grid(row=0, column=0, sticky='NSEW', columnspan=1, rowspan=1)

        notebook =ttk.Notebook(self.f0)
        notebook.pack(expand = 1, fill = "both")

        # Frame for first level
        # self.f1 = tk.LabelFrame(notebook, text='Controls', borderwidth=1, padx=10, pady=10, relief='raised')
        self.fr_firstlv = tk.Frame(notebook)
        self.fr_firstlv.grid(row=0, column=0, sticky='NSEW')
        self.fr_firstlv.rowconfigure(1, weight=1)

        self.firstlv_controls =tk.LabelFrame(self.fr_firstlv, text='Control')
        self.firstlv_controls.grid(row=0, column=0, sticky='NSEW')

        self.firstlv_tasks = tk.LabelFrame(self.fr_firstlv, text='Tasks')
        self.firstlv_tasks.grid(row=1, column=0, sticky='NSEW')

        self.firstlv_tasks.rowconfigure(0, weight=1)



        self.fr_higherlevel = tk.Frame(notebook, borderwidth=1, padx=10, pady=10, relief='raised')
        self.fr_higherlevel.grid(row=0, column=0, sticky='NSEW')
        self.fr_higherlevel.rowconfigure(1, weight=1)

        self.higherlv_controls = tk.LabelFrame(self.fr_higherlevel, text='Control')
        self.higherlv_controls.grid(row=0, column=0, sticky='NSEW')

        self.higherlv_tasks = tk.LabelFrame(self.fr_higherlevel, text='Tasks')
        self.higherlv_tasks.grid(row=1, column=0, sticky='NSEW')

        self.higherlv_tasks.rowconfigure(0, weight=1)





        notebook.add(self.fr_firstlv, text ="First Level")
        notebook.add(self.fr_higherlevel, text="Higher Level Analysis")


        # Frame for File list Tree View
        self.fr_results = tk.Frame(self, borderwidth=0, relief='raised', pady=10, padx = 2)
        self.fr_results.grid(row=0, column=1, sticky='NSEW', rowspan=1)
        self.fr_results.columnconfigure(0, weight=1)
        self.fr_results.rowconfigure(0, weight=1)


        # Individual elements
        # Display results and status
        self.result_tree = result_window(self.fr_results, stat, ['Number', 'Name', 'Status'], ['#', 'Name', 'Datasets'], self.extraction_view)
        # Display tasks in first level
        self.task_tree = result_window(self.firstlv_tasks, stat, ['Number', 'Name', 'Status'], ['#', 'Tasks', 'Status'], self.extraction_view)
        # Display tasks in higher level
        self.high_task_tree = result_window(self.higherlv_tasks, stat, ['Number', 'Name', 'Status'], ['#', 'Tasks', 'Status'], self.extraction_view)


        # Display results and status
        # self.result_tree = result_window(self.f2, viewer, stat)

        self.file_path = ''
        self.roi_path = ''

        # Controls
        el = fn.Elements(self.firstlv_controls)
        el.button("Database", self.search_subjects,1, 0, 0, tk.W + tk.E, 1)  # Selection of root directory
        el.button("Brain extraction", self.brain_extraction, '', 2, 2, tk.W + tk.E, 1)  # Brain extraction
        el.button("Generate Profiles", self.generate_profile, '', 0, 2, tk.W + tk.E, 1)  # Brain extraction
        el.button("Process", self.process, '', 0, 4, tk.W + tk.E, 1)  # Process dataset
        el.button("Set Structural", self.set_structural, '', 2, 4, tk.W + tk.E, 1)  # Select dataset corresponding to
        el.button("Generate Report", self.generate_report, '', 6, 0, tk.W + tk.E, 1)  # Select dataset corresponding to
        self.report_name = tk.StringVar()
        el.textField_var('Report Name', self.report_name, 20,5,1)


        # structural scan for BET and registration


        self.bet_thresh = el.textField("BET Frac. Int. Threshold", 5, 1, 0)  # Task or Dataset to be searched for
        self.bet_grad_thresh = el.textField("BET Grad. Threshold", 5, 1, 1)  # Task or Dataset to be searched for
        # self.filters = el.textField("Filters", 20, 1, 1)  # keywords to filter individual datasets
        self.bet_algo_list = ["Robust", "Bias Field Correction"]
        self.bet_algo = tk.StringVar()
        el.popupMenu(self.bet_algo, self.bet_algo_list, 1, 2, 20, 'W')
        self.bet_algo.set(self.bet_algo_list[0])

        # self.analysis_name.set('Hello')
        # self.analysis_box = el.textField_var("Analysis Name", self.analysis_name, 20, 1, 3)  # Task or Dataset to be searched for


        # el.button("Search", self.search, '', 3, 0, tk.N + tk.S, 1)  # button press to start search
        # el.button("Clear", self.search, '', 3, 1, tk.N, 1)  # button press to clear selection
        # el.check('Overwrite', self.overwrite, 4, 1)  # checkbox for overwrite option

        ## Higher Level Analysis
        e2 = fn.Elements(self.higherlv_controls)
        e2.button("Database", self.search_subjects, 2, 0, 0, tk.W + tk.E, 1)  # Selection of output directory
        e2.button("Run Higher Level Analysis", self.higher_level, '', 0, 1, tk.W + tk.E, 1)  # Generate profile

        self.prevselection = '0'

        self.root = Path(__file__).parent.absolute()
        tmp_path = Path(self.root)/'temp'
        if not Path(tmp_path).is_dir():
            os.mkdir(tmp_path)



#####  Main tasks ########################################
        # method for calling directory picker

    def selectPath(self, var):
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
        # self.search_subjects()

    def search_subjects(self, case):
        self.selectPath(case)
        self.subject_names = []
        self.subject_list = []
        for item in Path(self.file_path).iterdir():
            self.subject_names.append(item.name)
            self.subject_list.append([item, item.name])
        # print(self.subject_names)
        self.result_tree.fileList = self.aggregated_list(self.subject_list)
        self.result_tree.display()  # display the results
        if case == 1:
            self.search_tasks()
        if case == 2:
            self.search_feat_tasks()

    def search_tasks(self):
        task_list = []
        unique_list = []
        self.task_list = []
        for pa in self.result_tree.fileList:

            scan = Path(pa[0][0]).rglob(f'*.nii*')
            # find all scans and if any in post processed folders identified by ".feat", exclude them
            tasks = [Path(t).name for t in scan if "feat" not in str(t)]
            task_list += tasks

        for word in task_list:
            if word not in unique_list:
                unique_list.append(word)

        self.task_list = [['',item] for item in unique_list]
        self.task_tree.fileList = self.aggregated_list(self.task_list)
        self.task_tree.display()  # display the results

    def search_feat_tasks(self):
        task_list = []
        unique_list = []
        self.task_list = []
        for pa in self.result_tree.fileList:
            scan = Path(pa[0][0]).rglob(f'*.feat')
            # find all scans and if any in post processed folders identified by ".feat", exclude them
            tasks = [Path(t).name for t in scan]
            task_list += tasks

        for word in task_list:
            if word not in unique_list:
                unique_list.append(word)

        self.high_task_list = [['', item] for item in unique_list]
        self.high_task_tree.fileList = self.aggregated_list(self.high_task_list)
        self.high_task_tree.display()  # display the results

# indicate which 4D file is to be used as structural scan
    def set_structural(self):
        self.structural_scan = [self.task_tree.current_selection[1], self.task_tree.clickID]
        self.task_tree.status(self.structural_scan[1], 'Structural')
        # if structural scan needs to be changed to a new one
        if not (self.prevselection == self.structural_scan[1]):
            self.task_tree.status(self.prevselection, '')
        self.prevselection = self.task_tree.clickID


# Extract brain based on structural scan and entered parameters
    def brain_extraction(self):
        commands = []
        self.stat.set('Performing brain extraction ...')

        queue = self.result_tree.queue()

        for row in queue:
            subject = row[0][0]
            # samp = Path(subject).rglob(self.structural_scan[0])
            # for s in samp: self.sample = s
            # temp = str(self.sample).split('.nii')
            # sample_output = temp[0] + '_brain.nii.gz'
            sample_output, sample = self.get_structural(subject)
            algo = ['-R', '-B']
            bet_in = self.bet_algo_list.index(self.bet_algo.get())


            command = ['bet', str(sample), sample_output, algo[bet_in], '-m', '-f', self.bet_thresh.get(), '-g',
                       self.bet_grad_thresh.get(), '-o']
            # print(command)
            commands.append(command)

        # print(commands)
        self.threader_s(commands)
        self.stat.set('Brain extraction completed')
        self.sample_output = sample_output;

# get the extracted structural scan for a subject
    def get_structural(self,subject):
        samp = Path(subject).rglob(self.structural_scan[0])
        for s in samp: sample = s
        temp = str(sample).split('.nii')
        subject_structural = temp[0] + '_brain.nii.gz'
        return subject_structural, sample

    def get_task_name(self):
        task_name = (str(self.task_tree.current_selection[1]).split('.nii'))[0]
        return task_name

    #     add visualizer for the output
    def extraction_view(self, subject):
        suffix = str(self.structural_scan[0]).split('.nii')
        bet_output = suffix[0] + '_brain.nii.gz'

        base_search = Path(subject[0]).rglob(self.structural_scan[0])
        for b in base_search: base = b
        mask_search = Path(subject[0]).rglob(bet_output)
        for m in mask_search: mask = m

        command = ['fsleyes', '-cs', '-std', str(base), str(mask), '-cm','blue']

        # print(command)
        command_except = ['fsleyes', '-std', str(base), str(mask), '-cm','blue']
        self.update_idletasks()
        try:
            fn.appFuncs.thread(command, True)
        except:
            fn.appFuncs.thread(command_except, True)



    #  Allows user to create a custom design profile which can then be applied to all datasets
    def generate_profile(self):
        # use a sample profile to load the basics and
        # call FSL from here and run the FEAT tool.
        command_list = []
        command_list_sec = []
        self.subject_output=[]
        id = 1
        queue = self.result_tree.queue()
        # self.task_name = (str(self.task_tree.current_selection[1]).split('.nii'))[0]

        self.output_dir_name = f'subject_level_{self.get_task_name()}.feat'

        for row in queue:
            subject = row[0][0]
            output_dir = Path(subject) / self.output_dir_name
            input_data_search = Path(subject).rglob(f'{self.task_tree.current_selection[1]}')
            for s in input_data_search: input_data = s
            subject_structural, sample = self.get_structural(subject)
            # print(subject_structural)


            self.subject_output.append(output_dir)

        #   Set up for sample subject different than others
            if id == 1:
                sample_profile = self.root / 'sample_designs'/'sample_design.fsf'
                base_profile = self.root / 'temp_design.fsf'
                subprocess.run(['cp', sample_profile, base_profile])
        #
        #         # read in the base profile
                files = [base_profile, output_dir, input_data, subject_structural]
                self.replace(files, 1)
                command = ['feat', base_profile]
        #         # command_list.append([command])
        #         # Open Feat setup in FSL with this reference file
                subprocess.run(['Feat', base_profile])
                # reverse the subject specific paths
                self.replace(files, 2)


            # print([subject, input_data, subject_structural])
            subject_profile = self.root / 'temp' / f'temp_{id}.fsf'
            subprocess.run(['cp', base_profile, subject_profile])
            # read in and modify the subject profile
            files = [subject_profile, output_dir, input_data, subject_structural]
            # print(files)
            self.replace(files, 1)
            command = ['feat', subject_profile]
            command_list.append(command)
        #
        #     reg = Path(subject)/'reg'
        #     reg_std = Path(subject)/'reg_standard'
        #     command = ['cp','-r', reg, reg_std, output_dir]
        #     command_list_sec.append([command])
        #
            id += 1

        self.command_list_process = command_list

        files = Path(self.root).glob('temp_design*')
        for file in files:
            Path(file).unlink()

    def process(self):
        self.threader_s(self.command_list_process)
        # self.process_commands_seq(self.command_list_process)
        # empty the temp folder
        self.clear_dir(self.root/'temp')
        self.stat.set('Processing completed!')
        print('Processing completed!')
        # self.process_commands_seq(self.command_list_sec_process)


    def higher_level(self):
        self.stat.set('Select location of output')
        # output_directory = fn.appFuncs.selectPath()
        output_dir = '/home/quest/Drive/Emory/Development/MRANS/Program/mrans/test_data/Group_Analysis/'

        self.stat.set(f'Output location set to {output_dir}')

        subject_output = []
        for row in self.result_tree.fileList:
            subject = row[0][0]
            path = Path(subject)/f'{self.high_task_tree.current_selection[1]}'
            # if Path(path).is_dir():
            subject_output.append(path)

        number = len(self.result_tree.fileList)

        # Copy group design file to temp directory
        sample_profile = self.root /'sample_designs'/'group_design.fsf'
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

        command = ['Feat', group_profile]
        subprocess.run(command)

        files = Path(self.root).glob('group_design*')
        for file in files:
            Path(file).unlink()

    def generate_report(self):
        output_dir_name = f'subject_level_{self.get_task_name()}.feat'
        subject_output = [["Subject Name", "Absolute motion (mm)", "Relative motion (mm)"]]
        for row in self.result_tree.fileList:
            subject = row[0][0]
            path = Path(subject)/output_dir_name
            motion = self.headMotion_stats(path)
            subject_output.append([Path(subject).name, motion[0], motion[1]])

        report_file = Path(self.file_path)/f'{self.report_name.get()}.csv'
        # opening the csv file in 'w+' mode
        file = open(report_file, 'w+', newline='')

        # writing the data into the file
        with file:
            write = csv.writer(file)
            write.writerows(subject_output)







    def headMotion_stats(self, path):
        motion = [0, 0]
        if path.is_dir():
            a = path / "report_prestats.html"
            f = open(str(a), encoding="utf8")
            soup = BeautifulSoup(f, 'lxml')
            f.close
            try:
                W = soup.find_all('p')[-4]
                E = ''.join(W.find('br').next_siblings)
                S = E.split('mm')
                motion = [float(S[0].split('=')[1]), float(S[1].split('=')[1])]
            except:
                motion = [0, 0]
        return motion

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
        input_data = files[2]
        subject_structural = files[3]

        fin = open(profile, "rt")
        data = fin.read()

        if type == 1:
            data = data.replace('#%#', str(output_dir))
            data = data.replace('#$#', str(input_data))
            data = data.replace('#!#', str(subject_structural))
        else:
            # print('Replace 2')

            data = data.replace(str(output_dir).split('.nii')[0], '#%#')
            data = data.replace(str(input_data).split('.nii')[0], '#$#')
            data = data.replace(str(subject_structural).split('.nii')[0], '#!#')
            # print('replace 2 complete')
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
            print(f)
            subprocess.run(f)

    def process_commands_seq(self, command):
        for a in command:
            for f in a:
                subprocess.run(f)


    def threader_s(self,queue):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.process_commands_s, queue)

    def process_commands_s(self, command):
            subprocess.run(command)

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
        parent.minsize(1600,500)
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

# todo add different BETs, and add custom file settings