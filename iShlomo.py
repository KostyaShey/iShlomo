import tkinter as tk
import datetime
from functools import partial
import sqlite3

HEIGHT = 700
WIDTH = 1300
RELBUTTONHEIGHT = 0.05


MONTH = {1 : "JAN", 2 : "FEB", 3 : "MAR", 4 : "APR", 5 : "MAY", 6 : "JUN", 7 : "JUL", 8 : "AUG", 9 : "SEPT", 10 : "OKT", 11 : "NOV", 12 : "DEC"}
TYPEOFEXPENCES = {"MINC" : "Monthly Income", "MEXP" : "Monthly Expence", "INC" : "Additional income", "EXP" : "Additional expence"}
CURRENTDATE = datetime.datetime.now()
currentmonth = CURRENTDATE.month
currentyear = CURRENTDATE.year


#SQLite settings:
conn = sqlite3.connect("iShlomo_db.db")
c = conn.cursor()

#creating a new month and adding the monthly values
def createMonth():

	c.execute('SELECT * FROM MonExpences')
	monexpences = c.fetchall()
	c.execute('CREATE TABLE IF NOT EXISTS {month}{year}("ID" TEXT NOT NULL, "Value" INTEGER, "Name" TEXT, "Type" TEXT, PRIMARY KEY("ID"))'\
		.format(month = MONTH[currentmonth], year = currentyear))
	index = 1
	for i in range(len(monexpences)):
		monthindex = 1
		for digit in monexpences[i][5]:
			if int(digit) == 1 and monthindex == currentmonth:
				c.execute('INSERT OR IGNORE INTO {month}{year} SELECT ID, Value, Name, Type FROM MonExpences WHERE ID = "MEXP{index}"'\
					.format(month = MONTH[currentmonth], year = currentyear, index = index))
			else:
				monthindex += 1
		index +=1
	conn.commit()

	c.execute('SELECT * FROM MonIncome')
	monincome = c.fetchall()
	index2 = 1
	for i in range(len(monincome)):
		monthindex2 = 1
		for digit in monincome[i][5]:
			if int(digit) == 1 and monthindex2 == currentmonth:
				c.execute('INSERT OR IGNORE INTO {month}{year} SELECT ID, Value, Name, Type FROM MonIncome WHERE ID = "MINC{index2}"'\
					.format(month = MONTH[currentmonth], year = currentyear, index2 = index2))
			else:
				monthindex2 += 1
		index2 +=1
	conn.commit()

#checks if the current month and year is equal to the first month and year in the db 
def monthchecker():
	global currentyear
	global currentmonth
	c.execute('SELECT FirstMonth, FirstYear FROM System')
	firstmonandyear = c.fetchall()
	if firstmonandyear[0][0] == currentmonth and firstmonandyear[0][1] == currentyear:
		return True
	else:
		return False

#initializing the first month and the expences tables:
def start():
	c.execute('CREATE TABLE IF NOT EXISTS "MonExpences" ("ID" TEXT NOT NULL,"Name" TEXT NOT NULL, "Value" INTEGER NOT NULL, "Start" TEXT NOT NULL, "End" TEXT NOT NULL, "Month" TEXT NOT NULL, "Type" TEXT, PRIMARY KEY ("ID"))')
	c.execute('CREATE TABLE IF NOT EXISTS "MonIncome" ("ID" TEXT NOT NULL,"Name" TEXT NOT NULL, "Value" INTEGER NOT NULL, "Start" TEXT NOT NULL, "End" TEXT NOT NULL, "Month" TEXT NOT NULL, "Type" TEXT, PRIMARY KEY ("ID"))')
	c.execute('CREATE TABLE IF NOT EXISTS "System" ("ID" INTEGER,"Setup" INTEGER, "FirstMonth" INTEGER, "FirstYear" INTEGER, PRIMARY KEY ("ID"))')
	c.execute('INSERT OR IGNORE INTO System VALUES (1, 0, 0, 0)')
	conn.commit()

	c.execute('SELECT * FROM System')
	booltocheck = c.fetchall()
	if booltocheck[0][1] == 0:
		createMonth()
		c.execute('UPDATE System SET Setup= 1')
		c.execute('UPDATE System SET FirstMonth = {month}'.format(month = currentmonth))
		c.execute('UPDATE System SET FirstYear= {year}'.format(year = currentyear))
		conn.commit()

#use to return the previous month
def monthminusone(currentm, currenty):

	if currentm == 1:
		currentm == 12
		currenty -= 1
	else:
		currentm -= 1
	return currentm, currenty

#fetches all rows in a month
def fetchmonthdata(currentmonth, currentyear):
	c.execute('SELECT * FROM {month}{year}'.format(month = MONTH[currentmonth], year = currentyear))
	monthdata = c.fetchall()
	return monthdata

def update_text_in_textbox(monthdata, Type):
	
	textbox.insert(tk.INSERT, "{Name}\n".format(Name = TYPEOFEXPENCES[Type]))
	for row in monthdata:
		if row[3] == Type:
			textbox.insert(tk.INSERT, "{Name}					{Value} €\n".format(Name = row[2], Value = row[1]))
	textbox.insert(tk.INSERT, "\n")

#updating the output textbox
def update_textbox(currentmonth, currentyear):

	#clearing the textbox:
	textbox.delete(0.0, tk.END)

	monthdata = fetchmonthdata(currentmonth, currentyear)
	update_text_in_textbox(monthdata, "MINC")
	update_text_in_textbox(monthdata, "INC")
	update_text_in_textbox(monthdata, "MEXP")
	update_text_in_textbox(monthdata, "EXP")

def fetchtotalbalance(monthdata):
	total = 0
	for row in monthdata:
		if row[3] == "MINC":
			total += row[1]
		if row[3] == "MEXP":
			total -= row[1]
		if row[3] == "INC":
			total += row[1]
		if row[3] == "EXP":
			total -= row[1]
	return total

def update_text_in_totalbox(monthdata, label, Type):
	
	Dictionaryforstring = {"MINC" : "Total income: ", "MEXP" : "Total expences: ", "MONL" : "Money left: ", "BLM" : "Balance from last month: "}
	
	if Type == "MINC" or Type == "MEXP":
		total = 0
		for row in monthdata:
			if row[3] == Type:
				total += row[1]
		label["text"] = Dictionaryforstring[Type] + str(total) + "€"
	
	if Type == "BLM":
		
		blmtotal = 0
		if monthchecker():
			label["text"] = "Balance from last month: -"
		else:
			monthdata = fetchmonthdata(monthminusone(currentmonth, currentyear)[0], monthminusone(currentmonth, currentyear)[1])
			blmtotal = fetchtotalbalance(monthdata)
			label["text"] = Dictionaryforstring[Type] + str(blmtotal) + " €"
	
	if Type == "MONL":
		total = fetchtotalbalance(monthdata)
		if not monthchecker():
			monthdata = fetchmonthdata(monthminusone(currentmonth, currentyear)[0],monthminusone(currentmonth, currentyear)[1])	
			total += fetchtotalbalance(monthdata)

		label["text"] = Dictionaryforstring[Type] + str(total) + " €"

#updates the labels in the total box
def update_totalbox(currentmonth, currentyear):
	monthdata = fetchmonthdata(currentmonth, currentyear)
	update_text_in_totalbox(monthdata, balancelastmonthlabel, "BLM")
	update_text_in_totalbox(monthdata, totalincomelabel, "MINC")
	update_text_in_totalbox(monthdata, totalexpencelabel, "MEXP")
	update_text_in_totalbox(monthdata, moneyleftlabel, "MONL")


#command for the prev month button
def buttonprevmonth():
	global currentyear
	global currentmonth
	if currentmonth == 1:
		currentyear -= 1
	if currentmonth > 1:
		currentmonth -= 1
	else:
		currentmonth = 12
	if monthchecker():
		prevmonth['state'] = "disabled"
	datelabel['text'] = dateforlabel()
	update_textbox(currentmonth,currentyear)
	update_totalbox(currentmonth, currentyear)

#command for the next month button
def buttonnextmonth():
	global currentyear
	global currentmonth
	if currentmonth == 12:
		currentyear += 1
	if currentmonth < 12:
		currentmonth += 1
	else:
		currentmonth = 1
	createMonth()
	if not monthchecker():
		prevmonth['state'] = "normal"
	datelabel['text'] = dateforlabel()
	update_textbox(currentmonth,currentyear)
	update_totalbox(currentmonth, currentyear)

#updating the date label
def dateforlabel():
	return MONTH[currentmonth] + " " + str(currentyear)

#add a new row to the month
def addrowtomonth(Typeofvalue, inputwindow, NameEntry, ValueEntry):

	#using try and except to validate if the input is type int and displaying a label if not
	try:
		#this should cause an error if the Value is not a digit
		int(ValueEntry.get())
		
		# counting the values in the table to create a unique id
		MonthData = fetchmonthdata(currentmonth, currentyear)
		counter = 0
		for row in MonthData:
			print(row)
			if row[3] == Typeofvalue:
				counter += 1

		params = (Typeofvalue + str(counter + 1), ValueEntry.get(), NameEntry.get(), Typeofvalue)
		c.execute('INSERT INTO {month}{year} VALUES (?, ?, ?, ?)'.format(month = MONTH[currentmonth], year = currentyear), params)
		conn.commit()
		print("Row addded")
		update_textbox(currentmonth,currentyear)
		update_totalbox(currentmonth, currentyear)
		close_window(inputwindow)
	except:
		ValueEntry["fg"] =  "red"
		WarningLabel = tk.Label(inputwindow, text="Use only digits for the Value", fg = "red", bg = "white")
		WarningLabel.place(relx = 0.30, rely = 0.56)

#fetches all row in monthly tables
def fetchmonthlytables(Typeofvalue):
	if Typeofvalue == "MEXP":
		table = "MonExpences"
	else:
		table = "MonIncome"
	c.execute('SELECT * FROM {table}'.format(table = table))
	monthlytable = c.fetchall()
	return monthlytable

#returns bools for the month string in monthly expences
def addtostringwithcheckboxvalues(CheckBox):
	if CheckBox.get() == 1:
		return "1"
	else:
		return "0"

def addrowtomonthlytables(Typeofvalue, inputwindow, NameEntry, ValueEntry,\
			JanVar, FebVar, MarVar, AprVar, MayVar, JunVar, JulVar, AugVar, SepVar, OctVar, NovVar, DecVar, refresh):
	
	#using try and except to validate if the input is type int and displaying a label if not
	try:
		#this should cause an error if the Value is not a digit
		int(ValueEntry.get())
		
		#setting the table to add row
		if Typeofvalue == "MEXP":
			table = "MonExpences"
		else:
			table = "MonIncome"

		# counting the values in the table to create a unique id
		monthlytable = fetchmonthlytables(Typeofvalue)
		counter = 0
		for row in monthlytable:
			print(row)
			counter += 1

		#building a string for the month 
		stringwithcheckboxvalues = ""
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(JanVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(FebVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(MarVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(AprVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(MayVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(JunVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(JulVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(AugVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(SepVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(OctVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(NovVar)
		stringwithcheckboxvalues += addtostringwithcheckboxvalues(DecVar)

		params = (Typeofvalue + str(counter + 1), NameEntry.get(), ValueEntry.get(), "start", "end", stringwithcheckboxvalues, Typeofvalue)
		c.execute('INSERT INTO {table} VALUES (?, ?, ?, ?, ?, ?, ?)'.format(table = table), params)
		conn.commit()
		print("Row addded")
		
		#this will work if the user clicked and safe and add to current month
		if refresh == 1:
			addrowtomonth(Typeofvalue, inputwindow, NameEntry, ValueEntry)

		update_textbox(currentmonth,currentyear)
		update_totalbox(currentmonth, currentyear)
		close_window(inputwindow)

	except:

		ValueEntry["fg"] =  "red"
		WarningLabel = tk.Label(inputwindow, text="Use only digits for the Value", fg = "red", bg = "white")
		WarningLabel.place(relx = 0.30, rely = 0.17)

def close_window(window): 
    window.destroy()

def openinputwindow(Type):
	inputwindow = tk.Toplevel()
	inputwindow.title("Input "+ TYPEOFEXPENCES[Type])

	if Type == "INC" or Type == "EXP":
		
		canvas = tk.Canvas(inputwindow, height = HEIGHT/4, width = WIDTH/4)
		canvas.pack()

		inputframe = tk.Frame(inputwindow, bg = "white")
		inputframe.place(relx = 0.05, rely = 0.05, relwidth = 0.9, relheight = 0.9)

		NameLabel = tk.Label(inputframe, text="Name:", bg = "white")
		NameLabel.place(relx = 0.05, rely = 0.15, relwidth = 0.30)
		NameEntry = tk.Entry(inputframe, bd =5)
		NameEntry.place(relx = 0.30, rely = 0.15, relwidth = 0.55)
		ValueLabel = tk.Label(inputframe, text="Value:", bg = "white")
		ValueLabel.place(relx = 0.05, rely = 0.40, relwidth = 0.30)
		ValueEntry = tk.Entry(inputframe, bd =5)
		ValueEntry.place(relx = 0.30, rely = 0.40, relwidth = 0.55)
	
		closeinput = partial(close_window, inputwindow)
		cancel = tk.Button(inputframe, text = "Cancel", command = closeinput)
		cancel.place(relx = 0.05, rely = 0.70, relheight = RELBUTTONHEIGHT*4, relwidth = 0.40)
		
		saveinput = partial(addrowtomonth, Type, inputwindow, NameEntry, ValueEntry)
		save = tk.Button(inputframe, text = "Save", command = saveinput)
		save.place(relx = 0.55, rely = 0.70, relheight = RELBUTTONHEIGHT*4, relwidth = 0.40)

	if Type == "MINC" or Type == "MEXP":

		canvas = tk.Canvas(inputwindow, height = HEIGHT, width = WIDTH/4)
		canvas.pack()

		inputframe = tk.Frame(inputwindow, bg = "white")
		inputframe.place(relx = 0.05, rely = 0.05, relwidth = 0.9, relheight = 0.9)

		NameLabel = tk.Label(inputframe, text="Name:", bg = "white")
		NameLabel.place(relx = 0.05, rely = 0.03, relwidth = 0.30)
		NameEntry = tk.Entry(inputframe, bd =5)
		NameEntry.place(relx = 0.30, rely = 0.03, relwidth = 0.55)
		ValueLabel = tk.Label(inputframe, text="Value:", bg = "white")
		ValueLabel.place(relx = 0.05, rely = 0.09, relwidth = 0.30)
		ValueEntry = tk.Entry(inputframe, bd =5)
		ValueEntry.place(relx = 0.30, rely = 0.09, relwidth = 0.55)
		
		JanVar = tk.IntVar()
		January = tk.Checkbutton(inputframe, text = "January", variable = JanVar, bg = "white").place(relx = 0.30, rely = 0.19)
		FebVar = tk.IntVar()
		February = tk.Checkbutton(inputframe, text = "February", variable = FebVar, bg = "white").place(relx = 0.59, rely = 0.19)
		MarVar = tk.IntVar()
		March = tk.Checkbutton(inputframe, text = "March", variable = MarVar, bg = "white").place(relx = 0.30, rely = 0.24)
		AprVar = tk.IntVar()
		April = tk.Checkbutton(inputframe, text = "April", variable = AprVar, bg = "white").place(relx = 0.59, rely = 0.24)
		MayVar = tk.IntVar()
		May = tk.Checkbutton(inputframe, text = "May", variable = MayVar, bg = "white").place(relx = 0.30, rely = 0.29)
		JunVar = tk.IntVar()
		June = tk.Checkbutton(inputframe, text = "June", variable = JunVar, bg = "white").place(relx = 0.59, rely = 0.29)
		JulVar = tk.IntVar()
		July = tk.Checkbutton(inputframe, text = "July", variable = JulVar, bg = "white").place(relx = 0.30, rely = 0.34)
		AugVar = tk.IntVar()
		August = tk.Checkbutton(inputframe, text = "August", variable = AugVar, bg = "white").place(relx = 0.59, rely = 0.34)
		SepVar = tk.IntVar()
		September = tk.Checkbutton(inputframe, text = "September", variable = SepVar, bg = "white").place(relx = 0.30, rely = 0.39)
		OctVar = tk.IntVar()
		October = tk.Checkbutton(inputframe, text = "October", variable = OctVar, bg = "white").place(relx = 0.59, rely = 0.39)
		NovVar = tk.IntVar()
		November = tk.Checkbutton(inputframe, text = "November", variable = NovVar, bg = "white").place(relx = 0.30, rely = 0.44)
		DecVar = tk.IntVar()
		December = tk.Checkbutton(inputframe, text = "December", variable = DecVar, bg = "white").place(relx = 0.59, rely = 0.44)

		Placeholder1Label = tk.Label(inputframe, text="Placeholder for start date input", bg = "grey")
		Placeholder1Label.place(relx = 0.05, rely = 0.55, relwidth = 0.90)
		Placeholder2Label = tk.Label(inputframe, text="Placeholder for end date input", bg = "grey")
		Placeholder2Label.place(relx = 0.05, rely = 0.60, relwidth = 0.90)

		saveandrefresh = partial(addrowtomonthlytables, Type, inputwindow, NameEntry, ValueEntry,\
			JanVar, FebVar, MarVar, AprVar, MayVar, JunVar, JulVar, AugVar, SepVar, OctVar, NovVar, DecVar, refresh = 1)
		saveandrefreshmonth = tk.Button(inputframe, text = "Save and add to current month", command = saveandrefresh)
		saveandrefreshmonth.place(relx = 0.05, rely = 0.74, relheight = RELBUTTONHEIGHT*2, relwidth = 0.90)

		closeinput = partial(close_window, inputwindow)
		cancel = tk.Button(inputframe, text = "Cancel", command = closeinput)
		cancel.place(relx = 0.05, rely = 0.87, relheight = RELBUTTONHEIGHT*2, relwidth = 0.40)
		
		saveinput = partial(addrowtomonthlytables, Type, inputwindow, NameEntry, ValueEntry,\
			JanVar, FebVar, MarVar, AprVar, MayVar, JunVar, JulVar, AugVar, SepVar, OctVar, NovVar, DecVar, refresh = 0)
		save = tk.Button(inputframe, text = "Save", command = saveinput)
		save.place(relx = 0.55, rely = 0.87, relheight = RELBUTTONHEIGHT*2, relwidth = 0.40)

	inputwindow.mainloop()

def fetchrowfrommonth(Type, Listwithrows, NameEntry, ValueEntry):
	ID = Listwithrows.curselection()[0] + 1
	c.execute('SELECT * FROM {month}{year} WHERE ID = "{TYpe}{id}"'.format(month = MONTH[currentmonth], year = currentyear, TYpe = Type, id = ID))
	row = c.fetchall()
	NameEntry.delete(0, tk.END)
	NameEntry.insert(tk.END, row[0][2])
	ValueEntry.delete(0, tk.END)
	ValueEntry.insert(tk.END, row[0][1])

def saverowfrommonth(Type, Listwithrows, NameEntry, ValueEntry, editwindow):
	ID = Listwithrows.curselection()[0] + 1
	c.execute('UPDATE {month}{year} SET Name = "{NameValue}", Value = "{ValueValue}" WHERE ID = "{TYpe}{id}"'\
		.format(month = MONTH[currentmonth], year = currentyear, NameValue = NameEntry.get(), ValueValue = ValueEntry.get(), TYpe = Type, id = ID))
	conn.commit()
	close_window(editwindow)
	update_textbox(currentmonth, currentyear)
	update_totalbox(currentmonth, currentyear)

def openeditwindow(Type):
	editwindow = tk.Toplevel()
	editwindow.title("Edit "+ TYPEOFEXPENCES[Type])

	canvas = tk.Canvas(editwindow, height = HEIGHT, width = WIDTH/4)
	canvas.pack()

	editframe = tk.Frame(editwindow, bg = "white")
	editframe.place(relx = 0.05, rely = 0.05, relwidth = 0.9, relheight = 0.9)

	monthdata = fetchmonthdata(currentmonth, currentyear)

	Listwithrows = tk.Listbox(editframe, selectmode = "single")
	index = 1
	for row in monthdata:
		if row[3] == Type:
			Listwithrows.insert(index, row[2])
			index +=1

	Listwithrows.place(relx = 0.05, rely = 0.03, relwidth = 0.9, relheight = 0.3)

	NameLabel = tk.Label(editframe, text="Name:", bg = "white")
	NameLabel.place(relx = 0.05, rely = 0.43, relwidth = 0.30)
	NameEntry = tk.Entry(editframe, bd =5)
	NameEntry.place(relx = 0.30, rely = 0.43, relwidth = 0.55)
	ValueLabel = tk.Label(editframe, text="Value:", bg = "white")
	ValueLabel.place(relx = 0.05, rely = 0.49, relwidth = 0.30)
	ValueEntry = tk.Entry(editframe, bd =5)
	ValueEntry.place(relx = 0.30, rely = 0.49, relwidth = 0.55)

	fetchrow = partial(fetchrowfrommonth, Type, Listwithrows, NameEntry, ValueEntry)
	selectbutton = tk.Button(editframe, text = "Select", command = fetchrow).place(relx = 0.05, rely = 0.35, relheight = RELBUTTONHEIGHT, relwidth = 0.9)

	saverow = partial(saverowfrommonth, Type, Listwithrows, NameEntry, ValueEntry, editwindow)
	savebutton = tk.Button(editframe, text = "Save changes", command = saverow).place(relx = 0.05, rely = 0.55, relheight = RELBUTTONHEIGHT, relwidth = 0.9)

	editwindow.mainloop()

start()

#UI CONFIG
root = tk.Tk()
root.title("iShlomo by KOshey")

#setting up the size and bg image:
canvas = tk.Canvas(root, height = HEIGHT, width = WIDTH)
canvas.pack()

bg_image = tk.PhotoImage(file="money.png")
bg_label= tk.Label(root, image= bg_image)
bg_label.place(relheight = 1, relwidth = 1)


#placing the buttons into the button frame:
buttonframe = tk.Frame(root, bg = "white")
buttonframe.place(relx = 0.05, rely = 0.05, relwidth = 0.15, relheight = 0.9)

openmonthincome = partial(openinputwindow, "MINC")
addmonthincome = tk.Button(buttonframe, text = "Add monthly income", command = openmonthincome).place(relx = 0.05, rely = 0.01, relheight = RELBUTTONHEIGHT, relwidth = 0.9)

openincome = partial(openinputwindow, "INC")
addincome = tk.Button(buttonframe, text = "Add income", command = openincome).place(relx = 0.05, rely = 0.07, relheight = RELBUTTONHEIGHT, relwidth = 0.9)

openmonthexpence = partial(openinputwindow, "MEXP")
addmonthexpence = tk.Button(buttonframe, text = "Add month expence", command = openmonthexpence).place(relx = 0.05, rely = 0.13, relheight = RELBUTTONHEIGHT, relwidth = 0.9)

openexpence = partial(openinputwindow, "EXP")
addexpence = tk.Button(buttonframe, text = "Add expence", command = openexpence).place(relx = 0.05, rely = 0.19, relheight = RELBUTTONHEIGHT, relwidth = 0.9)

openeditexpence = partial(openeditwindow, "EXP")
editexpences = tk.Button(buttonframe, text = "Edit expences", command = openeditexpence).place(relx = 0.05, rely = 0.27, relheight = RELBUTTONHEIGHT, relwidth = 0.9)

openeditincome = partial(openeditwindow, "INC")
editexpences = tk.Button(buttonframe, text = "Edit income", command = openeditincome).place(relx = 0.05, rely = 0.33, relheight = RELBUTTONHEIGHT, relwidth = 0.9)


#frame for the results:
textframe = tk.Frame(root, bg = "white")
textframe.place(relx = 0.21, rely = 0.05, relwidth = 0.74, relheight = 0.8)

prevmonth = tk.Button(textframe, text = "<", command = buttonprevmonth)
prevmonth.place(relx = 0.37, rely = 0.01, relwidth=0.04, relheight=0.05, anchor = "n")
if monthchecker():
	prevmonth['state'] = "disabled"

datelabel = tk.Label(textframe, bg = "#d9d9d9", bd = 10, justify='center', text = dateforlabel())
datelabel.place(relx = 0.5, rely = 0.01, relwidth=0.2, relheight=0.05, anchor = "n")

nextmonth = tk.Button(textframe, text = ">", command = buttonnextmonth).place(relx = 0.63, rely = 0.01, relwidth=0.04, relheight=0.05, anchor = "n")

textbox = tk.Text(textframe, bg = "white")
textbox.place(rely = 0.07, relwidth=1, relheight=0.93)
update_textbox(currentmonth, currentyear)

#frame for month info:
infoframe = tk.Frame(root, bg = "white")
infoframe.place(relx = 0.21, rely = 0.85, relwidth = 0.74, relheight = 0.1)

balancelastmonthlabel = tk.Label(infoframe, bg = "white")
balancelastmonthlabel.place(relx = 0.02, rely = 0.15)
totalincomelabel = tk.Label(infoframe, bg = "white")
totalincomelabel.place(relx = 0.25, rely = 0.15)
totalexpencelabel = tk.Label(infoframe, bg = "white")
totalexpencelabel.place(relx = 0.25, rely = 0.5)
moneyleftlabel = tk.Label(infoframe, bg = "white", text = "moneyleft: ")
moneyleftlabel.place(relx = 0.48, rely = 0.15)
update_totalbox(currentmonth, currentyear)



root.mainloop()