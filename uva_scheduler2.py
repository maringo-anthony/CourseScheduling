# Anthony Maringo Alm4cu

import re
import urllib.request
import requests
import tkinter as tk


def get_departments():
    """Go to Lou's list home page and get all of the department codes to use for URL"""
    department_code_list = []
    department_name_list = []
    lous_home_HTML = "http://rabi.phys.virginia.edu/mySIS/CS2/index.php?Semester=1198"
    lous_home_HTML = requests.get(lous_home_HTML).text  # get html from lous list
    lous_home_HTML = lous_home_HTML.replace("&amp;", "&")  # fix & sign formatting

    department_regex = r'Group=(\w+)(\"?\'?)>([\w\s\&\;\,\-]*)<'
    department_finder = re.compile(department_regex)
    for match in department_finder.finditer(
            lous_home_HTML):  # make a list of dept codes and list of dept names in parallel
        department_code_list.append(match.group(1))
        department_name_list.append(match.group(3))

    print(department_code_list)
    print(department_name_list)


def find_boundary():
    """FIND THE BOUNDARY IN HTML OF LOU'S LIST WHERE THE DESIRED COURSE IS MENTIONED"""
    global text
    top_of_section = text.index('B' + course_name + course_number)
    text = text[top_of_section + 1:]
    try:
        bottom_of_section = text.index('B' + course_name)
    except:
        section_start_regex = r'(SectionStart T B[\w]*[\d]*\' style)'
        section_start_finder = re.compile(section_start_regex)
        for match in section_start_finder.finditer(text):
            bottom_of_section = text.index(match.group(1))
            break
    finally:
        text = text[:bottom_of_section]


def find_professors():
    """MAKE A LIST OF ALL OF THE PROFESSORS FROM LOU'S LIST"""
    global professor_list, text
    professor_regex = r'OLgetAJAX\(\'ldap\.php\?Name=([\w\-\s]*)'
    professor_finder = re.compile(professor_regex)

    professor_list = []

    for match in professor_finder.finditer(text):
        professor_list.append(match.group(1))


def find_class_info():
    """Makes lists of various information about each class using parallel lists"""

    global all_course_names_list, sections_list, desired_sections_list, desired_course_list, sections_dict, prof_section_dict
    find_professors()
    course_name_regex = r"""<tr class=\'Section(Odd|Even) S (\w*)(\d*)\'><td align=\'right\'><a href=\'javascript:void\(0\);\' class=\"Link\" onclick=\"SectionTip\('\d*','(\d*)'\);"""
    course_name_finder = re.compile(course_name_regex)

    all_course_names_list = []
    sections_list = []
    desired_course_list = []
    desired_sections_list = []

    # MAKE LIST OF ALL CLASSES ON THE PAGE
    for match in course_name_finder.finditer(text):
        all_course_names_list.append(match.group(2))
        sections_list.append(match.group(4))

    # MAKE LIST OF JUST THE CLASSES DESIRED
    for i in range(len(all_course_names_list)):
        if all_course_names_list[i] == course_name + course_number:
            desired_course_list.append(all_course_names_list[i])
            desired_sections_list.append(sections_list[i])

    # MAKE DICTIONARY OF CLASS TIMES

    multi_time_regex = """<tr class=\'Section(Odd|Even) S (\w*)(\d*).*\('\d*','(\d*)'\);.*Name=([\w\s-]+).*<td>([MoTuWeThFr]+) ([\d][\d]?:[\d]{2})(AM|PM) - ([\d][\d]?:[\d]{2})(AM|PM).*(\s<tr class='Section(Odd|Even) S (\w*)(\d*)'><td></td><td>.*<strong>([\w\s]+).*<td>([MoTuWeThFr]+) ([\d][\d]?:[\d]{2})(AM|PM) - ([\d][\d]?:[\d]{2})(AM|PM)</td><td>([\w\s]+) (\d)+</td></tr>)*"""
    multi_time_finder = re.compile(multi_time_regex)

    # NEW multi_time_regex match groups

    # g2 = course name/ number CHEM1410
    # g4 = section
    # g5 = Professor name
    # g6 = Day of the week of first meeting
    # g7 = start time of first meeting
    # g8 = AM/PM
    # g9 = end time of first meeting
    # g10= AM/PM
    # g15 = Professor name
    # g16 = Day of the week of second meeting
    # g17 = start time of the second meeting
    # g18 = AM/PM
    # g19 = end time of second meeting
    # G20 = AM/PM

    sections_dict = {}  # dictionary of each section with its start and end times as lists
    # {'SECTION_NUMBER': [[START_TIMES],[END_TIMES]]}
    prof_section_dict = {}  # {'PROF_NAME':[SECTIONS]}
    for match in multi_time_finder.finditer(text):  # make sections_dict
        if match.group(16) is None:
            start_list = [match.group(7) + match.group(8)]
            end_list = [match.group(9) + match.group(10)]
        else:
            start_list = [match.group(7) + match.group(8),
                          match.group(17) + match.group(18)]  # list of all start times for this section
            end_list = [match.group(9) + match.group(10),
                        match.group(19) + match.group(20)]  # list of all end times for this section
        if match.group(5) not in prof_section_dict:
            prof_section_dict[match.group(5)] = [match.group(4)]
        else:
            prof_section_dict[match.group(5)].append(match.group(4))

        sections_dict[match.group(4)] = [start_list, end_list]


def convert_to_military(time):
    """convert to military time"""
    time = str(time)
    if "12" in time:
        time = time.replace(":", "")
        time = time[:-2]
        return int(time)
    elif "AM" in time:
        time = time[:-2]
        time = time.replace(":", "")
        if len(time) == 3:
            time = "0" + time
            return int(time)
        return int(time)

    else:
        time = time[:-2]
        split_time = time.split(':')
        split_time[0] = str(int(split_time[0]) + 12)
        time = split_time[0] + split_time[1]
        return int(time)


def user_filter():
    """Narrows classes down based on time constraints"""
    global start_time_desired, end_time_desired, professor_list, sections_dict
    sections_dict_keys = []

    # CONVERT ALL TIMES TO MILITARY TIME FOR COMPARISON

    for key in sections_dict:
        for list in sections_dict[key]:
            for i in range(len(list)):
                list[i] = convert_to_military(list[i])

    # FIND ONLY CLASSES IN A GIVEN TIME RANGE

    for key in sections_dict.keys():  # get all of the sections as keys to iterate through dict
        sections_dict_keys.append(key)

    for key in sections_dict_keys:  # check to see if class is too early
        for i in range(len(sections_dict[key][0])):
            if sections_dict[key][0][i] < start_time_desired:
                sections_dict.pop(key)
                break

    sections_dict_keys.clear()  # get all of the sections as keys again
    for key in sections_dict.keys():
        sections_dict_keys.append(key)

    for key in sections_dict_keys:  # check to see if class is too late
        for i in range(len(sections_dict[key][1])):
            if sections_dict[key][1][i] > end_time_desired:
                sections_dict.pop(key)
                break

    for key in prof_section_dict:
        temp_list = []

        for i in range(len(prof_section_dict[key])):
            if prof_section_dict[key][i] in sections_dict.keys():
                temp_list.append(prof_section_dict[key][i])
        prof_section_dict[key] = temp_list


def get_vagrades_data():
    """get the data from va grades website"""
    global prof_gpa_dict, prof_gpa_list
    prof_gpa_dict = {}  # dictionary of each professor and their average gpa for this course
    prof_gpa_list = []  # list with every professor and gpa for each section that they have taught of this course

    vagrades_url = "https://vagrades.com/api/uvaclass/" + course_name + course_number
    web_data = requests.get(vagrades_url).text  # get all data from the page about this course
    sections_index = web_data.index("sections")  # find where the list of sections begins and trim text
    web_data = web_data[sections_index:]

    prof_gpa_regex = r"""\{"id".*?gpa":([\d\.]+).*?instructor":"([\w\s-]+).*?\},?"""
    prof_gpa_finder = re.compile(prof_gpa_regex)

    for match in prof_gpa_finder.finditer(web_data):  # parse the data for the professor and their gpa of each section
        prof_gpa_list.append([match.group(2), match.group(1)])  # group 2 is the professor, group 1 is the gpa
        prof_gpa_dict[match.group(2)] = None  # set each professor in the dict to be ready for cumulative gpa


def check_vagrades():
    """Creates sorted list of professors teaching this semester by gpa"""
    get_vagrades_data()
    global prof_gpa_dict, prof_gpa_list, prof_list, prof_gpa_list, prof_section_dict

    prof_gpa_dict_key = []  # make a list of all keys to iterate through dict
    for key in prof_gpa_dict.keys():
        prof_gpa_dict_key.append(key)

    for key in prof_gpa_dict_key:  # remove professors that are not teaching in that time
        if key not in prof_section_dict or len(prof_section_dict[key]) is 0:
            prof_gpa_dict.pop(key)

    prof_gpa_dict_key.clear()
    prof_gpa_dict_key = prof_gpa_dict.keys()

    for professor in prof_gpa_dict_key:  # calculate each professors GPA and add to prof_gpa_dict
        total_gpa = 0
        num_sections = 0
        for i in range(len(prof_gpa_list)):
            if professor in prof_gpa_list[i]:
                num_sections += 1
                total_gpa += float(prof_gpa_list[i][1])
        prof_gpa_dict[professor] = total_gpa / num_sections

    prof_list = list(prof_gpa_dict.keys())
    for key in prof_section_dict:  # includes prof if the professor has no data in VA Grades for this course
        if key not in prof_list:
            prof_list.append(key)
            prof_gpa_dict[key] = 0

    prof_gpa_list.clear()
    for i in range(len(prof_list)):
        prof_gpa_list.append(str(prof_gpa_dict[prof_list[i]]))
    prof_gpa_list, prof_list = zip(*sorted(zip(prof_gpa_list, prof_list)))  # sort the professors by gpa
    prof_list = list(prof_list)
    prof_gpa_list = list(prof_gpa_list)
    prof_gpa_list.reverse()
    prof_list.reverse()



def get_gui_input():
    """Get user input from within the GUI"""
    global course_desired, start_time_desired, end_time_desired, department, text, course_name, course_number, prof_gpa_listbox, prof_gpa_dict

    prof_gpa_listbox.delete(0, 'end')
    department = dept_entry_box.get()
    course_desired = course_entry_box.get()
    start_time_desired = convert_to_military(start_time_listbox.get(start_time_listbox.curselection()))
    end_time_desired = convert_to_military(end_time_listbox.get(end_time_listbox.curselection()))

    lous_url_base = """http://rabi.phys.virginia.edu/mySIS/CS2/page.php?Semester=1198&Type=Group&Group="""
    lous_url = lous_url_base + department

    with urllib.request.urlopen(lous_url) as stream:  # the variable stream will be read in from the webpage url
        text = stream.read().decode('utf-8')

    course_name = (course_desired[:course_desired.find(' ')]).strip().upper()
    course_number = (course_desired[course_desired.find(' ') + 1:]).strip()

    find_boundary()

    find_class_info()
    user_filter()
    check_vagrades()

    for i in range(len(prof_list)):
        prof_gpa_listbox.insert("end", str(i + 1) + '. ' + prof_list[i] + " (" + str(
            round(prof_gpa_dict[prof_list[i]], 2)) + ")")
    prof_gpa_listbox.pack()


def gui():
    """Make the GUI appear with all appropriate fields"""
    global dept_entry_box, course_entry_box, start_time_listbox, end_time_listbox, prof_gpa_listbox
    # UVA BLUE: #222f4a
    # UVA ORANGE: #e26f19

    time_frame_width = 20

    root = tk.Tk()
    canvas = tk.Canvas(root, height=600, width=600)
    canvas.pack()

    # Main Frame
    main_frame = tk.Frame(root, bg="#222f4a", bd=5)  # frame everything else is placed in
    main_frame.place(relx=.5, rely=.1, relwidth=.8, relheight=.8, anchor='n')

    dept_label = tk.Label(main_frame, bg="#e26f19", fg="#ffffff", borderwidth=5, text="Enter your department name:")
    dept_label.pack(fill="x")

    dept_entry_box = tk.Entry(main_frame, bg="#ffffff", borderwidth=5, highlightbackground="#222f4a")
    dept_entry_box.pack()

    course_label = tk.Label(main_frame, bg="#e26f19", fg="#ffffff", borderwidth=5,
                            text="Enter your course name. EX. CS 1110:")
    course_label.pack(fill="x")

    course_entry_box = tk.Entry(main_frame, bg="#ffffff", borderwidth=5, highlightbackground="#222f4a")
    course_entry_box.pack()

    # Time label frame
    time_lbl_frame = tk.Frame(main_frame, bd=5, bg="#222f4a", )
    time_lbl_frame.pack(fill="x")

    start_label = tk.Label(time_lbl_frame, bg="#e26f19", fg="#ffffff", borderwidth=5,
                           text="Select the earliest start time.", width=time_frame_width)
    start_label.pack(side="left")

    end_label = tk.Label(time_lbl_frame, bg="#e26f19", fg="#ffffff", borderwidth=5, width=time_frame_width,
                         text="Select your latest end time.")
    end_label.pack(side="right")

    # Time selection frame
    time_sel_frame = tk.Frame(main_frame, bd=5, bg="#222f4a")
    time_sel_frame.pack(fill="x")

    # Start time selection
    start_frame = tk.Frame(time_sel_frame, bd=0, bg="#222f4a", width=time_frame_width)
    start_frame.pack(side="left", anchor="n")

    start_time_listbox = tk.Listbox(start_frame, bd=0, height=5, exportselection=False)
    start_time_listbox.pack(side="left", fill="y")

    start_time_scroll_bar = tk.Scrollbar(start_frame, bd=0, orient="vertical",
                                         highlightbackground="#222f4a",
                                         command=start_time_listbox.yview)
    start_time_scroll_bar.config(command=start_time_listbox.yview)
    start_time_scroll_bar.pack(side="right", fill="y")

    start_time_listbox.config(yscrollcommand=start_time_scroll_bar.set)

    for line in range(8, 12):
        start_time_listbox.insert("end", str(line) + ":00 AM")
    start_time_listbox.insert("end", "12:00 PM")

    for line in range(1, 9):
        start_time_listbox.insert("end", str(line) + ":00 PM")

    # End time selection
    end_frame = tk.Frame(time_sel_frame, bd=0, bg="#222f4a", width=time_frame_width)
    end_frame.pack(side="right", anchor="n")

    end_time_listbox = tk.Listbox(end_frame, bd=0, height=5, exportselection=False)
    end_time_listbox.pack(side="left", fill="y")

    end_time_scroll_bar = tk.Scrollbar(end_frame, bd=0, orient="vertical", bg="#ffffff",
                                       highlightbackground="#222f4a",
                                       command=end_time_listbox.yview)
    end_time_scroll_bar.config(command=end_time_listbox.yview)
    end_time_scroll_bar.pack(side="right", fill="y")

    end_time_listbox.config(yscrollcommand=end_time_scroll_bar.set)

    for line in range(8, 12):
        end_time_listbox.insert("end", str(line) + ":00 AM")
    end_time_listbox.insert("end", "12:00 PM")

    for line in range(1, 9):
        end_time_listbox.insert("end", str(line) + ":00 PM")

    get_departments()

    # Professor ranking
    prof_gpa_label = tk.Label(main_frame, bg="#e26f19", fg="#ffffff", borderwidth=5,
                              text="Professor ranked based on GPA:")
    prof_gpa_label.pack(fill="x")

    prof_gpa_frame = tk.Frame(main_frame, bd=5, bg="#222f4a", width=time_frame_width)
    prof_gpa_frame.pack(anchor="n")

    prof_gpa_listbox = tk.Listbox(prof_gpa_frame, bd=0, height=5, exportselection=False)
    prof_gpa_listbox.pack(side="left", fill="y")

    prof_gpa_scroll_bar = tk.Scrollbar(prof_gpa_frame, bd=0, orient="vertical", bg="#ffffff",
                                       highlightbackground="#222f4a",
                                       command=prof_gpa_listbox.yview)
    prof_gpa_scroll_bar.config(command=prof_gpa_listbox.yview)
    prof_gpa_scroll_bar.pack(side="right", fill="y")

    prof_gpa_listbox.config(yscrollcommand=prof_gpa_scroll_bar.set)

    enter = tk.Button(main_frame, text="Press to Submit Info", command=get_gui_input, bg="#ffffff",
                      highlightbackground="#222f4a")
    enter.pack()
    root.mainloop()


gui()

# figure out how to login to course forum
# find the ratings on course forum for a each professor
# sort the professors by rating
# display a list in order of gpa ranking and list of rating ranking
# allow users to put in multiple classes at once and display all the info at the same time
# GUI with selection of department, type in class code(CS 1110), and box to put in time preference
# get rid of all commented stuff
