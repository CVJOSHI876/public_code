#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Tue Nov 24 14:29:09 2015

@author: ryankeenan
"""
import pdb
import sys
import os
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"


print "START +===================="
import Tkinter as tk
import ttk
import tkMessageBox as nessagebox
import tkFileDialog as filedialog
import FileDialog
import pickle
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
if sys.version_info >= (3,0):
    from matplotlib import style
import matplotlib.dates as mdates
from functools import partial

import numpy as np
import re
import pandas as pd
import collections
import datetime
 

LARGE_FONT = ("Verdana", 12)
if sys.version_info >= (3,0):
    style.use("ggplot")

np.set_printoptions(suppress = True)
pause = False


def getNewXLdata():
    """function to read in and parse a new XL file.
    returns bigDict, which is a dictionary containing the filepath
    to the original XL file and all the earn/spend data"""

    fileselect = filedialog.askopenfilename() #user can select XL file

    filename = os.path.basename(fileselect)
    print('Opening file: '+fileselect)

    workbook = pd.read_excel(fileselect, index_col=0) # workbook is now a pandas data frame
    
    #Next going to read all the relevant data into dictionary format for convenience/clarity
    spending = False
    rawdatadone = False
    tabearndone = False
    tabspenddone = False
    earnname = []
    spendname = []

    startind = 0

    dates = []
    datestrings = []
    datetimes = []
    datetimedata = workbook.columns
    for idx, datet in enumerate(datetimedata):
        if isinstance(datet, datetime.datetime):
            datetimes.append(datet)
            stringdate = datet.strftime('%d-%m-%Y')
            datestrings.append(stringdate)
            dates.append(stringdate[0:5])

    ndays = len(dates)
    endind = ndays-1
    bigDict = {}
    bigDict["Earn"] = collections.OrderedDict()
    bigDict["Spend"] = collections.OrderedDict()

    
    for linecount in range(len(workbook)): 

        cells = workbook.iloc[linecount]

        strcell = str(cells.name).strip()
        if spending == False:
            if 'Total' in strcell:
                if 'Total earnings' in strcell:
                    spending = True
#                    print('******************')
#                    print('found the end of earning on line: ',linecount+1)
#                    print('******************')
                else:
                    names = strcell.split()
                    earnname.append(names[1])
#                    print('cataloguing another earn source: ',strcell)
            elif (strcell != 'nan'
                    and 'CTR' not in strcell):
                strcell = ' '.join(strcell.split())
                vals=[]
                for idx, cell in enumerate(cells[startind:endind+1]):
                    if type(cell) == unicode: cell = np.nan
                    if not np.isfinite(cell):
                        cell=0
                    vals.append(cell)

                bigDict["Earn"][strcell]={}
                earn = np.array(vals)
                nonZeroInd = (earn > 0.1).nonzero()[0]
                if len(nonZeroInd) >= 3:
                    Active = True
                else: Active = False
                namesplit = strcell.split()
                match = re.search(r'(.+)('+namesplit[-1]+')', strcell)
                bigDict["Earn"][strcell]["DailyTotal"] = earn
                bigDict["Earn"][strcell]["Country"] = match.group(2)
                bigDict["Earn"][strcell]["Account"] = match.group(1).strip()
                bigDict["Earn"][strcell]["Nonzero"] = nonZeroInd
                bigDict["Earn"][strcell]["Active"] = Active

        elif rawdatadone == False:
            if ('Total' in strcell) & ('spend' in strcell):
                if 'spend per day' in strcell:
                    rawdatadone = True
                else:
                    names = strcell.split()
                    spendname.append(names[1])
            elif ('%' not in strcell
                    and 'Total' not in strcell
                    and 'earn' not in strcell
                    and 'spend' not in strcell
                    and 'None' not in strcell
                    and strcell != 'nan'):
                strcell = ' '.join(strcell.split())
                vals=[]
                
                for idx, cell in enumerate(cells[startind:endind+1]):
                    try:
                        if not np.isfinite(cell):
                            cell=0
                        vals.append(cell)
                    except:
                        pdb.set_trace()
                bigDict["Spend"][strcell]={}
                spend = np.array(vals)
                nonZeroInd = (spend > 0.1).nonzero()[0]
                if len(nonZeroInd) >= 3:
                    Active = True
                else: Active = False
                namesplit = strcell.split()
                match = re.search(r'(.+)('+namesplit[-1]+')', strcell)
                bigDict["Spend"][strcell]["DailyTotal"] = spend
                bigDict["Spend"][strcell]["Country"] = match.group(2)
                bigDict["Spend"][strcell]["Account"] = match.group(1).strip()
                bigDict["Spend"][strcell]["Nonzero"] = nonZeroInd
                bigDict["Spend"][strcell]["Active"] = Active


    nearnsource = len(earnname)
    nspendsource = len(spendname)


    earnkeys = bigDict["Earn"].keys()
    spendkeys = bigDict["Spend"].keys()
    Countries = []
    earnAccounts = []
    spendAccounts = []

    for key in earnkeys:
        account = bigDict["Earn"][key]["Account"]
        if account not in earnAccounts:
            earnAccounts.append(account)
        country = bigDict["Earn"][key]["Country"]
        if country not in Countries:
            Countries.append(country)

    for key in spendkeys:
        account = bigDict["Spend"][key]["Account"]
        if account not in spendAccounts:
            spendAccounts.append(account)

    bigDict["EarnAccountNames"] = earnAccounts
    bigDict["SpendAccountNames"] = spendAccounts
    bigDict["Countries"] = collections.OrderedDict()
    bigDict["Countrywise"] = collections.OrderedDict()

    for country in Countries:
        activeEarn = []
        bigDict["Countrywise"][country] = {}
        bigDict["Countries"][country] = {}
        accounts = list(bigDict["Earn"].keys())
        nearnsource = len(accounts)
        earn = np.zeros((ndays,nearnsource))
        idx = 0
        for account in accounts:
            currentCountry = bigDict["Earn"][account]["Country"]
            if  currentCountry == country:
                currentEarn = bigDict["Earn"][account]["DailyTotal"]
                earn[:,idx] = currentEarn
                if bigDict["Earn"][account]["Active"] == True:
                    activeEarn.append(account)
                idx += 1

        bigDict["Countrywise"][country]["Earnings"] = earn
        bigDict["Countrywise"][country]["TotEarn"] = np.sum(earn,1)
        bigDict["Countries"][country]["ActiveEarn"] = activeEarn

        activeSpend = []
        accounts = list(bigDict["Spend"].keys())
        nspendsource = len(accounts)
        spend = np.zeros((ndays,nspendsource))
        idx = 0
        for account in accounts:
            currentCountry = bigDict["Spend"][account]["Country"]
            if  currentCountry == country:
                spend[:,idx] = bigDict["Spend"][account]["DailyTotal"]
                if bigDict["Spend"][account]["Active"] == True:
                    activeSpend.append(account)
                idx += 1

        bigDict["Countrywise"][country]["Spending"] = spend
        bigDict["Countrywise"][country]["TotSpend"] = np.sum(spend,1)
        bigDict["Countrywise"][country]["Profit"] = np.sum(earn,1) - np.sum(spend,1)
        bigDict["Countries"][country]["ActiveSpend"] = activeSpend


    bigDict["Filename"] = filename
    bigDict["Dates"] = dates
    bigDict["Datetimes"] = datetimes



    global bigDict


def resetDates():
    global pause
    pause = False
    global omitInds
    omitInds = []
    print('Resetting Dates...')


def choose_country(name):
    
    global pause
    pause = False
    global bigDict
    global currentCountry
    global currentSpendNames
    global currentEarnNames
    global activeEarnNames
    global activeSpendNames
    global newAnalysisPop
    
    currentCountry = name
    currentSpendNames = [bigDict["Countries"][currentCountry]["ActiveSpend"][0]]
    currentEarnNames = [bigDict["Countries"][currentCountry]["ActiveEarn"][0]]
    activeSpendNames = bigDict["Countries"][currentCountry]["ActiveSpend"]
    activeEarnNames = bigDict["Countries"][currentCountry]["ActiveEarn"]

    newAnalysisPop = True
    DatesTop(event)
    SpendTop(event)
    EarnTop(event)
    AnalysisTop(event)
    
    
def weightPop(event):

    def setValues(pscoreWvar, pcorrWvar, ecorrWvar, eindvWvar, minCutWvar, 
        redCutWvar, incCutWvar, maxCutWvar, psW, pcW, ecW, eiW, 
                        miC, reC, inC, maC):

        if miC > reC:
            miC = np.clip(reC - 0.5, -5, 5)
        if reC > inC:
            reC = np.clip(inC - 0.5, -5, 5)
            miC = np.clip(reC - 0.5, -5, 5)
        if inC > maC:
            inC = np.clip(maC - 0.5, -5, 5)
            reC = np.clip(inC - 0.5, -5, 5)
            miC = np.clip(reC - 0.5, -5, 5)
          
            
        pscoreWvar.set(psW)
        pcorrWvar.set(pcW)
        ecorrWvar.set(ecW)
        eindvWvar.set(eiW)
        minCutWvar.set(miC)
        redCutWvar.set(reC)
        incCutWvar.set(inC)
        maxCutWvar.set(maC)
               
        weightDict["pscoreWvar"] = psW
        weightDict["pcorrWvar"] = pcW
        weightDict["ecorrWvar"] = ecW
        weightDict["eindvWvar"] = eiW
        weightDict["minCutWvar"] = miC
        weightDict["redCutWvar"] = reC
        weightDict["incCutWvar"] = inC
        weightDict["maxCutWvar"] = maC
                  
        
        pickle.dump(weightDict,open('weightPickle.p','wb'),protocol=2)
        UpdateLabelText()
        global pause
        pause = False
        
    popup = tk.Toplevel()
    popup.wm_title("Weight Adjustment")

    pscoreLabel = tk.Label(popup, text="Profit Score\nWeight")
    pscoreLabel.grid(row=0, column=0, ipadx=15)

    pcorrLabel = tk.Label(popup, text="Profit Correlation\nWeight")
    pcorrLabel.grid(row=0,column=1, ipadx=15)

    ecorrLabel = tk.Label(popup, text="Total Earn\nCorrelation Weight")
    ecorrLabel.grid(row=0,column=2, ipadx=15)

    eindvLabel = tk.Label(popup, text="Individual Earn\nCorrelation Weight")
    eindvLabel.grid(row=0,column=3, ipadx=15)

    weightDict = pickle.load(open("weightPickle.p"))
    pscoreWvar = tk.DoubleVar()
    pcorrWvar = tk.DoubleVar()
    ecorrWvar = tk.DoubleVar()
    eindvWvar = tk.DoubleVar()
    minCutWvar = tk.DoubleVar()
    redCutWvar = tk.DoubleVar()
    incCutWvar = tk.DoubleVar()
    maxCutWvar = tk.DoubleVar()

    pscoreWvar.set(weightDict["pscoreWvar"])
    pscoreScale = tk.Scale(popup, from_=0, to=10, resolution=0.1,
         variable=pscoreWvar)
    pscoreScale.grid(row=1, column=0, ipady=10)

    pcorrWvar.set(weightDict["pcorrWvar"])
    pcorrScale = tk.Scale(popup, from_=0, to=10, resolution=0.1,
         variable=pcorrWvar)
    pcorrScale.grid(row=1, column=1, ipady=10)

    ecorrWvar.set(weightDict["ecorrWvar"])
    ecorrScale = tk.Scale(popup, from_=0, to=10, resolution=0.1,
         variable=ecorrWvar)
    ecorrScale.grid(row=1, column=2, ipady=10)

    eindvWvar.set(weightDict["eindvWvar"])
    eindvScale = tk.Scale(popup, from_=0, to=10, resolution=0.1,
         variable=eindvWvar)
    eindvScale.grid(row=1, column=3, ipady=10)

    emptyLabel = tk.Label(popup, text="    ")
    emptyLabel.grid(row=2,column=0, ipadx=15)

    minCutLabel = tk.Label(popup, text="MINIMIZE\ncutoff score")
    minCutLabel.grid(row=3, column=0, ipadx=15)

    redCutLabel = tk.Label(popup, text="REDUCE\ncutoff score")
    redCutLabel.grid(row=3,column=1, ipadx=15)

    incCutLabel = tk.Label(popup, text="INCREASE\ncutoff score")
    incCutLabel.grid(row=3,column=2, ipadx=15)

    maxCutLabel = tk.Label(popup, text="MAXIMIZE\ncutoff score")
    maxCutLabel.grid(row=3,column=3, ipadx=15)

    minCutWvar.set(weightDict["minCutWvar"])
    minCutScale = tk.Scale(popup, from_=-5, to=5, resolution=0.1,
         variable=minCutWvar)
    minCutScale.grid(row=4, column=0, ipady=10)

    redCutWvar.set(weightDict["redCutWvar"])
    redCutScale = tk.Scale(popup, from_=-5, to=5, resolution=0.1,
         variable=redCutWvar)
    redCutScale.grid(row=4, column=1, ipady=10)

    incCutWvar.set(weightDict["incCutWvar"])
    incCutScale = tk.Scale(popup, from_=-5, to=5, resolution=0.1,
         variable=incCutWvar)
    incCutScale.grid(row=4, column=2, ipady=10)

    maxCutWvar.set(weightDict["maxCutWvar"])
    maxCutScale = tk.Scale(popup, from_=-5, to=5, resolution=0.1,
         variable=maxCutWvar)
    maxCutScale.grid(row=4, column=3, ipady=10)

    emptyLabel2 = tk.Label(popup, text="    ")
    emptyLabel2.grid(row=5,column=0, ipadx=15)

    B1 = ttk.Button(popup, text='Apply', command = lambda: setValues(pscoreWvar, 
        pcorrWvar, ecorrWvar, eindvWvar, minCutWvar, 
        redCutWvar, incCutWvar, maxCutWvar, pscoreWvar.get(), 
        pcorrWvar.get(), ecorrWvar.get(), eindvWvar.get(), minCutWvar.get(), 
        redCutWvar.get(), incCutWvar.get(), maxCutWvar.get()))
    
    B1.grid(row=6, column=0, ipady=10)

    B2 = ttk.Button(popup, text='Reset', command = lambda: setValues(pscoreWvar, 
        pcorrWvar, ecorrWvar, eindvWvar, minCutWvar, 
        redCutWvar, incCutWvar, maxCutWvar, 1.0, 1.0, 1.0, 1.0, -2.0, -1.0, 1.0, 2.0))
    
    B2.grid(row=6, column=1, ipady=10)

    B3 = ttk.Button(popup, text='Close', command = popup.destroy)
    B3.grid(row=6, column=3, ipady=10)

    popup.geometry('550x420+0+500')    



def setpop1(event):

    popup = tk.Toplevel()
    popup.wm_title("Spend Score Basics")


    msg = """    There are four items being added together to come up with the "score" for each \
spend source.  These are identified in the "Analysis Text" window between the ">>> <<<" for each \
spend source in the "Detailed Spend Analysis" section. In detail, these are:\n
1) Profitable Fraction of Days or "profit score": takes on a value 0 to 1 representing # of positive profit days \
divided by total # of days.\n
2) Profit Correlation Score: The value "R" of the correlation between spend and profit, weighted \
by fraction of total spend for each account, and relative fluctuation in spend and profit (see \
correlation and weights description for details).  In principle, this score can take on a value between \
negative 2 and positive 2.\n
3) Overall Earn Correlation Score: Same as for profit above, the value of the correlation weighted \
by fraction of spend and relative fluctuation in spend and earn (score between \
negative 2 and positive 2).\n
4) Individual Earning Score: Will contain as many values as there are earn sources, same idea as \
above, where each value represents correlation spend and earn, weighted by fraction of spend and \
relative fluctuation between spend and earn (each score ranges between \
negative 2 and positive 2).  The sum of individual earn scores is then divided by number of earn sources.\n
    The basic idea behind the scoring scheme is to rank each of the spending sources \
by performance, based on some overall characteristics.  We focus primarily on correlation with \
earnings and profit, but also with consideration for what percentage of the time a given country \
is profiting, what fraction of total spending each account represents, and the relative \
fluctuations between spend, earn, and profit.\n
    In the "Analysis Text Window", The text at the top shows "Individual Spend Recommendations", \
we list each spend source, a recommendation (i.e., MAXIMIZE, REDUCE, etc.) and a score.  Below this,\
a breakdown of the correlation between the spend and earn sources currently selected.  Scroll down to find, \
"Detailed Spend Analysis", where we show the various scoring values and considerations for each \
spend source.  Values that appear between >>> <<< symbols are the actual values that are summed \
to arrive at the final score, namely, Profitable Fraction of Days, Profit Correlation Score, \
Overall Earn Correlation Score, and Individual Earning Score, each multiplied by the user selected weight. """

    entry = tk.Label(popup, text=msg,
                    anchor=tk.NW, justify=tk.LEFT)

    def y(event, entry=entry):
    # FIXME: make this a global method, to prevent function object creation
    # for every label.
        pad = 0
        pad += int(str(entry['bd']))
        pad += int(str(entry['padx']))
        pad *= 2
        entry.configure(wraplength = event.width - pad)
        
    entry.bind("<Configure>", y )
    entry.pack(side='top', fill='x', pady=10)
    B1 = ttk.Button(popup, text='Okay', command =  popup.destroy)
    B1.pack()
    popup.geometry('600x600+200+100')    
#    popup.mainloop()

def setpop2(event):

    popup = tk.Toplevel()
    popup.wm_title("Profit Score")


    msg = """Is this country profiting?\n
    We assign a value (to the variable profitScore) according to the fraction of days that are \
profitable over the dates selected, i.e., if every day yielded positive profit, then we assign \
a value of 1, if half the days were profitable, we assign a value of 0.5.  We don't penalize \
any individual spend accounts for days, or fraction of days, that yield losses, because simply \
observing a loss can't be attributed directly to a particular account (this will be done later \
through correlation analysis).  Profit score is then multiplied by the user selected weight."""

    entry = tk.Label(popup, text=msg,
                    anchor=tk.NW, justify=tk.LEFT)

    def y(event, entry=entry):
    # FIXME: make this a global method, to prevent function object creation
    # for every label.
        pad = 0
        pad += int(str(entry['bd']))
        pad += int(str(entry['padx']))
        pad *= 2
        entry.configure(wraplength = event.width - pad)
        
    entry.bind("<Configure>", y )
    entry.pack(side='top', fill='x', pady=10)
    B1 = ttk.Button(popup, text='Okay', command =  popup.destroy)
    B1.pack()
    popup.geometry('300x300+210+110')    
#    popup.mainloop()

def setpop3(event):

    popup = tk.Toplevel()
    popup.wm_title("Correlation Analysis")


    msg = """Is this spend account correlated with earnings and/or profit/loss?\n
    We run a correlation analysis to determine if a given spend account is significantly \
correlated with earnings and/or profit/loss.  We assume that a correlation coefficient, \
R, that is in the range -0.3 < R < 0.3 is not significant so a value of zero is assigned \
(to variables earnCorrScore, profitCorrScore) in that case.  If R < -0.3 or R > 0.3, \
then the value of R itself is assigned to the score, i.e., if R = 0.57, then the account \
receives 0.57 points, if R = -0.8, then the score value is -0.8.  We then correlate spending \
with each individual earn source, seeking to assign value (variable indvEarnCorr) where there \
is a significant correlation between individual spend and earn.\n
    A correlation can be driven by a single data point.  To avoid this bias, we run the \
correlation analysis iteratively throwing out one date at a time to identify outliers \
that may be driving a biased correlation.  We throw out the largest outlier when deriving \
the correlation to be used in scoring.  In principle, it would be possible to iteratively throw \
out more outliers to test/ensure the stability of the correlation, but this may slow things \
down considerably, given that all correlations are re-run whenever the date selection changes.\n
    The three separate correlation scores are then multiplied by the user selected weights for each, \
namely, the values from the "profit correlation", "total earn", and "individual earn" weight sliders \
in the weight adjustment window."""

    entry = tk.Label(popup, text=msg,
                    anchor=tk.NW, justify=tk.LEFT)

    def y(event, entry=entry):
    # FIXME: make this a global method, to prevent function object creation
    # for every label.
        pad = 0
        pad += int(str(entry['bd']))
        pad += int(str(entry['padx']))
        pad *= 2
        entry.configure(wraplength = event.width - pad)
        
    entry.bind("<Configure>", y )
    entry.pack(side='top', fill='x', pady=10)
    B1 = ttk.Button(popup, text='Okay', command =  popup.destroy)
    B1.pack()
    popup.geometry('450x400+220+120')    
#    popup.mainloop()

def setpop4(event):

    popup = tk.Toplevel()
    popup.wm_title("Weights")


    msg = """Weights:\n
    There are two kinds of weights that go into calculating a spend account's score.  These are \
internal weights (hard-coded, not changeable by the user) and adjustable weights (the user sets \
these weights in the "weight adjustment" window.  What follows is a description of the internal \
weights.  The user changeable weights are simply factors to multiply each score by when computing \ 
the final score.\n
    Internally, we wish to weight each value assigned above with some kind of assessment of whether \
or not the observed correlation is reflecting reality or not.  To do this, we consider both what \
percentage of total spending each accounts represents, as well as the fluctuation in spending \
and earning.  The logic behind this is, first, that an account which represents a large fraction \
of total spending should have a measurable effect on earnings/profit, while an account that \
represents a small fraction of total spending should have a lesser effect.  Similarly, if a \
correlation is observed, and we assume the relationship between spending and earn/profit is \
linear (i.e., spend twice as much, earn / profit / lose twice as much), then we can say that \
the relative fluctuations in spending and earning should be of similar magnitude.  At this \
point, the values of the weights are assigned as follows:\n
1) fraction of overall Spend weight:
    each significant correlation between individual spend and earnings/profit is given a weight \
equal to 1+fraction_of_total_spend, i.e., if an account represents 90% of total spend, it gets \
a weight of 1.9, if an account represents 1% of total spend it gets a weight of 1.01.  This \
is meant to augment the score of high percentage spending accounts where a correlation is \
found, while not necessarily penalizing small percentage spend accounts.\n
2) overall Earn weight:
    same as for fraction of spending, i.e., weight = 1+fraction_of_total_earn.  This applies \
to correlations between individual spend and individual earn sources.  Again, meant to augment \
the score for a correlation found where an earn account represents a large percentage of \
earnings, while not necessarily penalizing a small percentage account.\n
3) fluctuation in earn/spend weight:
    This weight is meant to ensure that correlations are only given full weight when the \
fluctuation in earning or profit is of the same order as fluctuation in spending.  At this \
point, if fluctuations in spending are within a factor of 10 of fluctuations in  \
earnings/profit, then weight=1, meaning, no penalty to any significant correlation. \
Outside a factor of 10, weight = 2 + log10(fluxRatio).  This function goes rapidly to zero \
as fluxRatio gets smaller, and is equal to zero when fluxRatio = 0.01.  All weights for \
fluxRatio < 0.01 are set to zero."""

    entry = tk.Label(popup, text=msg,
                    anchor=tk.NW, justify=tk.LEFT)

    def y(event, entry=entry):
    # FIXME: make this a global method, to prevent function object creation
    # for every label.
        pad = 0
        pad += int(str(entry['bd']))
        pad += int(str(entry['padx']))
        pad *= 2
        entry.configure(wraplength = event.width - pad)
        
    entry.bind("<Configure>", y )
    entry.pack(side='top', fill='x', pady=10)
    B1 = ttk.Button(popup, text='Okay', command =  popup.destroy)
    B1.pack()
    popup.geometry('600x600+230+130')    
#    popup.mainloop()


def update_spend():

    global currentSpendIndices
    global currentSpendNames
    global activeSpendNames
    global pause

    onList=[]
    for var in spendVars:
        onList.append(var.get())
        
    if not any(onList):
        onList[0] = 1
        spendVars[0].set(1)
        
    onList = np.int_(onList)
    currentSpendIndices = (onList > 0).nonzero()[0]
    currentSpendNames = [activeSpendNames[i] for i in currentSpendIndices]
    if not firstAnalysisPop:
        UpdateLabelText()
    pause = False

def deselectall_spend():
    global currentSpendIndices
    global currentSpendNames
    global activeSpendNames
    global pause
    currentSpendIndices = []
    currentSpendNames = []
    for idx, var in enumerate(spendVars):
        spendVars[idx].set(0)
    pause = False
    if not firstAnalysisPop:
        UpdateLabelText()

def selectall_spend():
    global currentSpendIndices
    global currentSpendNames
    global activeSpendNames
    global pause
    currentSpendIndices = []
    currentSpendNames = []
    for ix, name in enumerate(activeSpendNames):
        print('spendVar index:',ix)
        currentSpendIndices.append(ix)
        currentSpendNames.append(activeSpendNames[ix])
        spendVars[ix].set(1)
    pause = False

    if not firstAnalysisPop:
        UpdateLabelText()

def SpendTop(event):

    global firstSpendPop
    if not firstSpendPop:
        if spendPop.winfo_exists():
            spendPop.destroy()
    spendPop = tk.Toplevel()
    spendList = bigDict["Countries"][currentCountry]["ActiveSpend"]
    label = tk.Label(spendPop, text="Spend Accounts")
    label.pack(side='top', fill='x')
    frame = tk.Frame(spendPop, pady=10)
    B2 = tk.Button(frame, text='de-Select All',
                        command=deselectall_spend)
    B2.grid(row=0,column=1)
    B3 = tk.Button(frame, text='Select All',
                        command=selectall_spend)
    B3.grid(row=0,column=0)
    frame.pack()
    vsb = tk.Scrollbar(spendPop, orient="vertical")
    text = tk.Text(spendPop, width=30, height=20,
                            yscrollcommand=vsb.set)
    vsb.config(command=text.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    text.pack(side="left", fill="both", expand=True)

    spendVars = []
    cbs = collections.OrderedDict()

    for idx, item in enumerate(spendList):
        spendVars.append(tk.IntVar())
        cbs[item] = tk.Checkbutton(text, text=item, variable=spendVars[idx],
                            command=update_spend)
        if idx == 0:
            cbs[item].toggle()

        text.window_create("end", window=cbs[item])
        text.insert("end", "\n")

    global spendVars
    firstSpendPop = False
    global spendPop
    update_spend()
    spendPop.geometry('200x300+0+500')
    
def update_earn():

    global currentEarnIndices
    global currentEarnNames
    global activeEarnNames
    global pause

    onList=[]
    for var in earnVars:
        onList.append(var.get())
        
    if not any(onList):
        onList[0] = 1
        earnVars[0].set(1)
        
    onList = np.int_(onList)
    currentEarnIndices = (onList > 0).nonzero()[0]
    currentEarnNames = [activeEarnNames[i] for i in currentEarnIndices]
    
    if not firstAnalysisPop:
        UpdateLabelText()

    pause = False

def deselectall_earn():
    global currentEarnIndices
    global currentEarnNames
    global activeEarnNames
    global pause
    currentEarnIndices = []
    currentEarnNames = []
    for idx, var in enumerate(earnVars):
        earnVars[idx].set(0)
            
    if not firstAnalysisPop:
        UpdateLabelText()
    pause = False

    
def selectall_earn():
    global currentEarnIndices
    global currentEarnNames
    global activeEarnNames
    global pause
    currentEarnIndices = []
    currentEarnNames = []
    for idx, name in enumerate(activeEarnNames):
        currentEarnIndices.append(idx)
        currentEarnNames.append(activeEarnNames[idx])
        earnVars[idx].set(1)
        
    if not firstAnalysisPop:
        UpdateLabelText()
    pause = False
    

def EarnTop(event):

    global firstEarnPop
    if not firstEarnPop:
        if earnPop.winfo_exists():
            earnPop.destroy()
    earnPop = tk.Toplevel()
    earnList = bigDict["Countries"][currentCountry]["ActiveEarn"]
    label = tk.Label(earnPop, text="Earn Accounts")
    label.pack(side='top', fill='x')
    frame = tk.Frame(earnPop, pady=10)
    B2 = tk.Button(frame, text='de-Select All',
                        command=deselectall_earn)
    B2.grid(row=0,column=1)
    B3 = tk.Button(frame, text='Select All',
                        command=selectall_earn)
    B3.grid(row=0,column=0)
    frame.pack()
    vsb = tk.Scrollbar(earnPop, orient="vertical")
    text = tk.Text(earnPop, width=30, height=20,
                            yscrollcommand=vsb.set)
    vsb.config(command=text.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    text.pack(side="left", fill="both", expand=True)

    earnVars = []
    cbs = collections.OrderedDict()

    for idx, item in enumerate(earnList):
        earnVars.append(tk.IntVar())
        cbs[item] = tk.Checkbutton(text, text=item, variable=earnVars[idx],
                            command=update_earn)
        cbs[item].toggle()

        text.window_create("end", window=cbs[item])
        text.insert("end", "\n")

    global earnVars
    firstEarnPop = False
    global earnPop
    update_earn()
    earnPop.geometry('200x300+205+500')
    
def updates():
    global omitInds
    global pause
    onList=[]
    for var in varis:
        onList.append(var.get())
    onList = np.int_(onList)
    omitInds = (onList == 0).nonzero()[0]
    pause = False
    if not firstAnalysisPop:
        UpdateLabelText()
   
def selectall_dates():
    for index, var in enumerate(varis):
        varis[index].set(1)
    updates()
  
def deselectall_dates():
    for index, var in enumerate(varis):
        varis[index].set(0)
    updates()

def DatesTop(event):

    global firstDatePop
    if not firstDatePop:
        if dateTop.winfo_exists():
            dateTop.destroy()

    dateTop = tk.Toplevel()
    dateList = bigDict["Dates"]
    label = tk.Label(dateTop, text="Date Selector")
    label.pack(side='top', fill='x')
    frame = tk.Frame(dateTop, pady=10, padx=10)
    B2 = tk.Button(frame, text='Select All',
                        command=selectall_dates)
    B2.pack(side=tk.TOP)
    frame.pack(side=tk.TOP)
    B1 = tk.Button(frame, text='de-Select All',
                        command=deselectall_dates)
    B1.pack(side=tk.TOP)

    vsb = tk.Scrollbar(dateTop, orient="vertical")
    text = tk.Text(dateTop, width=30, height=20,
                            yscrollcommand=vsb.set)
    vsb.config(command=text.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    text.pack(side="left", fill="both", expand=True)

    varis = []
    cbs = collections.OrderedDict()

    for idx, item in enumerate(dateList):
        varis.append(tk.IntVar())
        cbs[item] = tk.Checkbutton(text, text=item, variable=varis[idx],
                command=updates)
        cbs[item].toggle()
        text.window_create("end", window=cbs[item])
        text.insert("end", "\n")


    global varis
    firstDatePop = False
    global dateTop
    updates()
    dateTop.geometry('150x300+405+500')
    
def UpdateLabelText():
    
#Here we're considering the combination of selected spend and earn sources
    global newAnalysisPop
    if newAnalysisPop:
        AnalysisTop(event)
        
    global labelDict
    dates = bigDict['Dates']    
    spendgood=[]
    for name in currentSpendNames:
        spendgood.extend(list(bigDict["Spend"][name]["Nonzero"]))

    spendgood = np.array(spendgood)
    spendgood = np.unique(spendgood)
    inrange = ((spendgood >= newStartInd) & (spendgood <= newEndInd)).nonzero()[0]
    spendgood = spendgood[inrange]
    
    earngood=[]
    for name in currentEarnNames:
        earngood.extend(list(bigDict["Earn"][name]["Nonzero"]))

    earngood = np.array(earngood)
    earngood = np.unique(earngood)
    inrange = ((earngood >= newStartInd) & (earngood <= newEndInd)).nonzero()[0]
    earngood = earngood[inrange]

    #Here we've found where valid spending and earning data exist for selected accounts
    good = np.array(list(set(spendgood).intersection(earngood)))
    
    #omitInds below consists of dates that have been deselected (if any)
    if any(omitInds):
        for elem in omitInds:
            ind = (good == elem).nonzero()
            if ind: good = np.delete(good, ind)

    if len(good) >= 4:   #Only attempt to do analysis with 4 or more valid dates
        
        #now summing up the relevent spend and earn data
        for idx, name in enumerate(currentSpendNames):
    
            if idx == 0: spenddata = np.array(bigDict["Spend"][name]["DailyTotal"])
            else: spenddata += np.array(bigDict["Spend"][name]["DailyTotal"])
    
        for idx, name in enumerate(currentEarnNames):
    
            if idx == 0: earndata = np.array(bigDict["Earn"][name]["DailyTotal"])
            else: earndata += np.array(bigDict["Earn"][name]["DailyTotal"])
    
        totspend = bigDict["Countrywise"][currentCountry]["TotSpend"]
        profit = bigDict["Countrywise"][currentCountry]["Profit"]
        percspend = round(100*np.sum(spenddata[good])/np.sum(totspend[good]),1)
    
        percProfitDays = round((len((profit[good] > 0).nonzero()[0])/len(good)), 2)
        totalProfit = round(np.sum(profit),2)
    
        corr = np.corrcoef(spenddata[good],earndata[good])
        corrall = round(corr[0,1],2)
        corravgarr = np.empty(len(good))
        corrstdarr = np.empty(len(good))
        
        #going through and throwing out one day at a time to validate correlation
        for idx, elem in enumerate(good):
            testinds = np.delete(good, idx)
            testcorr = np.empty(len(testinds))
    
            for jdx, elem in enumerate(testinds):
                testgood = np.delete(testinds, jdx)
                corr = np.corrcoef(spenddata[testgood],earndata[testgood])
                testcorr[jdx] = corr[0,1]
    
            corravgarr[idx] = np.mean(testcorr)
            corrstdarr[idx] = np.std(testcorr)
    
        avgcval = round(np.mean(corravgarr),2)
        avgsval = round(np.std(corravgarr),2)
        goodind = np.argmax(abs(corravgarr - corrall))
        outcval = round(corravgarr[goodind],2)
        outsval = round(corrstdarr[goodind],2)
        outind = good[goodind]


        if len(currentSpendNames) > 1:
            saccountsHead = 'Selected Spending Accounts: '
            saccountsInfo = 'These Accounts Represent '
        else:
            saccountsHead = 'Selected Spending Account: '
            saccountsInfo = 'This Account Represents '
    
        if len(currentEarnNames) > 1:
            eaccountsHead = 'Selected Earning Accounts: '
            eaccountsInfo = 'These Accounts Represent '
        else:
            eaccountsHead = 'Selected Earning Account: '
            eaccountsInfo = 'This Account Represents '
    
        spendString = saccountsHead
        firstBreak = False
        secondBreak = False
        thirdBreak = False
        breakSize1 = 30 #characters in spendString after which to insert a break
        breakSize2 = 30 #characters in spendString after which to insert a break
        
        for indx, name in enumerate(currentSpendNames):
            if indx == 0:
                spendString += name.split()[0]
            else:
                spendString += '+'+name.split()[0]
            if len(spendString) > breakSize1 and not firstBreak and name != currentSpendNames[-1]:
                spendString += '\n'
                firstBreak = True
            if len(spendString) > breakSize1+breakSize2 and not secondBreak and name != currentSpendNames[-1]:
                spendString += '\n'
                secondBreak = True
            if len(spendString) > breakSize1+breakSize2+breakSize2 and not thirdBreak and name != currentSpendNames[-1]:
                spendString += '\n'
                thirdBreak = True
        
        earnString = eaccountsHead
        firstBreak = False
        secondBreak = False
        thirdBreak = False
        
        for indx, name in enumerate(currentEarnNames):
            if indx == 0:
                earnString += name.split()[0]
            else:
                earnString += '+'+name.split()[0]
            if len(earnString) > 30 and not firstBreak and name != currentEarnNames[-1]:
                earnString += '\n'
                firstBreak = True
            if len(earnString) > 60 and not secondBreak and name != currentEarnNames[-1]:
                earnString += '\n'
                secondBreak = True
            if len(earnString) > 90 and not thirdBreak and name != currentEarnNames[-1]:
                earnString += '\n'
                thirdBreak = True

        if outcval <= -0.5: corrStatement = 'a strong negative'
        if outcval > -0.5 and outcval <= -0.3: corrStatement = 'a weak negative'
        if outcval > -0.3 and outcval <= 0.3: corrStatement = 'no significant'
        if outcval >= 0.3 and outcval < 0.5: corrStatement = 'a weak positive'
        if outcval >= 0.5: corrStatement = 'a strong positive'
    
        upperLabelText = str('\n==========================\nCountry: '+currentCountry+'\n'
                        +spendString+'\n\n'
                        +saccountsInfo+str(percspend)+'%\n of total spending in '+currentCountry+'\n\n'
                        +earnString+'\n\n'
                        +'Date Range: '+dates[good[0]]+' to '+dates[good[-1]]+'\n'
                        +'(Single Outlier Exclusion '+dates[outind]+')\n\n'
                        +'The correlation coefficient '+'R = '+str(outcval)+' +/- '+str(avgsval)+',\n'
                        +'implies that spending shows '+corrStatement+'\ncorrelation with the selected earn accounts')
       

#######################################################
#NOW DOING INDIVIDUAL SPEND RECOMMENDATIONS
######################################################## 

        try: 
            weightDict = pickle.load(open("weightPickle.p"))
        except:
            weightDict = {}        
            weightDict["pscoreWvar"] = 1.0
            weightDict["pcorrWvar"] = 1.0
            weightDict["ecorrWvar"] = 1.0
            weightDict["eindvWvar"] = 1.0
            weightDict["minCutWvar"] = -2.0
            weightDict["redCutWvar"] = -1.0
            weightDict["incCutWvar"] = 1.0
            weightDict["maxCutWvar"] = 2.0
             
            pickle.dump(weightDict,open('weightPickle.p','wb'),protocol=2)
        
        pscoreWeight = weightDict["pscoreWvar"]
        pcorrWeight = weightDict["pcorrWvar"]
        ecorrWeight = weightDict["ecorrWvar"]
        eindvWeight = weightDict["eindvWvar"]
        minCut = weightDict["minCutWvar"]
        redCut = weightDict["redCutWvar"]
        incCut = weightDict["incCutWvar"]
        maxCut = weightDict["maxCutWvar"]
        global weightDict
        
        recList1 = []
        recList2 = []
        colorList = []
        
        #these next three lines may have already been done above, but may not have, given selected earn/spend
        totspend = bigDict["Countrywise"][currentCountry]["TotSpend"]
        profit = bigDict["Countrywise"][currentCountry]["Profit"]
        totalProfit = round(np.sum(profit),2)
    
        earnCorrScore = np.zeros(len(activeSpendNames)) #to hold spend-earn correlation values (zeroed in the range -0.3 < R < 0.3)
        earnCorrValue = np.zeros(len(activeSpendNames)) #to hold actual values (not-zeroed in the range -0.3 < R < 0.3)
        indvEarnScore = np.zeros(len(activeSpendNames)) #sum of correlation values spend-indvEarn
    
        fracSpendScore= np.zeros(len(activeSpendNames)) #fraction of total spending
        profitCorrScore = np.zeros(len(activeSpendNames)) #correlation with profit score (zeroed in the range -0.3 < R < 0.3)
        profitCorrValue =  np.zeros(len(activeSpendNames)) #corr with profit, not-zeroed
        profitScore = np.zeros(len(activeSpendNames))  #fraction of profitable days
        totalScore = np.zeros(len(activeSpendNames))  #sum of scores
        indvEarnScore = np.zeros(len(activeSpendNames)) #sum of correlation values spend-indvEarn
  
        ipercspend = np.zeros(len(activeSpendNames))
        spendFlux = np.zeros(len(activeSpendNames))  #fractional fluctuation of spend (stdv/mean)
        spendRange = np.zeros(len(activeSpendNames))  #fractional fluctuation of spend (stdv/mean)
        wspendFlux = np.zeros(len(activeSpendNames))  #weighted fractional fluctuation of spend (stdv/mean)
        earnFlux = np.zeros(len(activeSpendNames))   #fractional fluctuation of earn (stdv/mean)
        profitFlux =  np.zeros(len(activeSpendNames)) #fractional fluctuation of profit (stdv/mean)
        profitRange =  np.zeros(len(activeSpendNames)) #fractional fluctuation of profit (stdv/mean)
        spendEarnWeight = np.zeros(len(activeSpendNames)) 
        spendProfitWeight = np.zeros(len(activeSpendNames)) 
        eTotalScore = np.zeros(len(activeSpendNames)) 
        pTotalScore = np.zeros(len(activeSpendNames)) 
              
        allEarn = np.array(bigDict["Countrywise"][currentCountry]["TotEarn"]) #retrieve earn totals for this country
        allEgood = (allEarn > 0).nonzero()[0] #identify nonzero earnings dates
    
        for nameidx, name in enumerate(activeSpendNames):  #looping through spend accounts one at a time
    
    
            spendgood = list(bigDict["Spend"][name]["Nonzero"])  #find all valid spend dates
            spendgood = np.array(spendgood)  
            spenddata = np.array(bigDict["Spend"][name]["DailyTotal"])  #this is all spend data for this account, not just "good"
            if any(omitInds):   #excluding any selected dates
                for elem in omitInds:
                    ind = (spendgood == elem).nonzero()
                    if ind: spendgood = np.delete(spendgood, ind)   
    
            segood = np.array(list(set(spendgood).intersection(allEgood)))
            ipercspend[nameidx] = np.sum(spenddata[segood])/np.sum(totspend[segood])  #calculate % of spend in this acct.
            fracSpendScore[nameidx] = ipercspend[nameidx]  #assign fractional percent as score for this acct.
    
            #here we multiply spending fluctuation by percent of spending to get the expected impact
            # of this account on total profit or total earn
            spendFlux[nameidx] = np.std(spenddata[segood])/np.mean(spenddata[segood])
            wspendFlux[nameidx] = ipercspend[nameidx]*spendFlux[nameidx]
            print spenddata[segood]
    
            earnFlux[nameidx] = round(np.std(allEarn[segood])/np.mean(allEarn[segood]),2)
            profitFlux[nameidx] = np.clip(round(np.std(profit[segood])/abs(np.mean(profit[segood])),2),0,1)
    
    
    
            #In the next 2 lines we're storing the full range of spend/profit change over the dates
            #selected.  Not doing anything with this at the moment, but maybe going to implement
            #something that penalizes spend accounts that have a negative correlation with profit
            #and the range in spending matches the range in profit/loss, which would indicate 
            #that a particular account is likely driving the reduction of profit indicated by
            #the negative correlation.  
            spendRange[nameidx] = round(np.max(spenddata[segood]) - np.min(spenddata[segood]),2)
            profitRange[nameidx] = round(np.max(profit[segood]) - np.min(profit[segood]),2)
    
            profitScore[nameidx] = round(pscoreWeight*(np.float(len((profit[segood] > 0).nonzero()[0]))/len(segood)), 2)
           
            if wspendFlux[nameidx] >= earnFlux[nameidx]:
                spendEarnWeight[nameidx] = 1.0 + np.clip(round(1.5 + np.log10(earnFlux[nameidx]/wspendFlux[nameidx]),3),0,1)
            else: spendEarnWeight[nameidx] = 1.0 + np.clip(round(1.5 + np.log10(wspendFlux[nameidx]/earnFlux[nameidx]),3),0,1)
    
            if wspendFlux[nameidx] >= profitFlux[nameidx]:
                spendProfitWeight[nameidx] = 1.0 + np.clip(round(1.5 + np.log10(profitFlux[nameidx]/wspendFlux[nameidx]),3),0,1)
            else: spendProfitWeight[nameidx] = 1.0 + np.clip(round(1.5 + np.log10(wspendFlux[nameidx]/profitFlux[nameidx]),3),0,1)
    
    
            if len(segood) >= 4:
                secorrarr = np.empty(len(segood))  #empty array to hold iterated correlation values
                spcorrarr = np.empty(len(segood))
                for idx, elem in enumerate(segood):  #looping through discarding one date at a time to find largest outlier
                    testinds = np.delete(segood, idx) #
                    testcorr = np.corrcoef(spenddata[testinds],allEarn[testinds]) #recorrelating with one day thrown out       
                    testcorr2 = np.corrcoef(spenddata[testinds],profit[testinds]) #recorrelating with one day thrown out       
                    secorrarr[idx] = testcorr[0,1]
                    spcorrarr[idx] = testcorr2[0,1]
        
                #here we're just taking the biggest outlier to represent reality, without going the
                #one layer deeper to check stability
                semeancval = round(np.mean(secorrarr),2)
                segoodind = np.argmax(abs(secorrarr - semeancval))
                seoutcval = round(secorrarr[segoodind],2)
                earnCorrValue[nameidx] = seoutcval
                if seoutcval <= -0.3 or seoutcval >= 0.3: earnCorrScore[nameidx] = seoutcval            
        
                spmeancval = round(np.mean(spcorrarr),2)
                spgoodind = np.argmax(abs(spcorrarr - spmeancval))
                spoutcval = round(spcorrarr[spgoodind],2) 
                profitCorrValue[nameidx] = spoutcval
                if spoutcval <= -0.3 or spoutcval >= 0.3: profitCorrScore[nameidx] = spoutcval         
    
    
            #now preparing to correlate with individual earn sources
            indvEarnCorr = np.zeros(len(currentEarnNames))-99 #array to hold correlation values for each earn account to current spend acct.
            indvEarnValue = np.zeros(len(currentEarnNames))-99
            indvEarnFlux = np.zeros(len(currentEarnNames))-99
            indvEarnFrac = np.zeros(len(currentEarnNames))
            fluxRatio = np.zeros(len(currentEarnNames))-99  
            indvWeight = np.zeros(len(currentEarnNames))
            
            for eind, ename in enumerate(currentEarnNames):  #looping through active earn accounts to correlate with each separately
                
                egood = bigDict["Earn"][ename]["Nonzero"]  #all valid earn values
                agood = np.array(list(set(spendgood).intersection(egood)))  #intersecting valid spend and earn dates
    
                if len(agood) >= 5:                
    
                    earn = np.array(bigDict["Earn"][ename]["DailyTotal"])  #all possible earn data
    
                    #this next line might look funny, but we're recording the fraction of 
                    #earnings represented in the present account over all valid dates
                    #being considered presently, so, for example, if there are 10 valid dates
                    #but only 3 days of earnings on this account, fraction will be lower
                    #than considering only dates where earnings are recorded
                    indvEarnFrac[eind] = round(np.sum(earn[segood])/np.sum(allEarn[segood]),3)
                    corr = np.corrcoef(spenddata[agood],earn[agood])  #correlating valid spend and earn
                    corrarr = np.empty(len(agood))  #empty array to hold iterated correlation values
               
                    for idx, elem in enumerate(agood):  #looping through discarding one date at a time to find largest outlier
                        testinds = np.delete(agood, idx) #
                        corr = np.corrcoef(spenddata[testinds],earn[testinds]) #recorrelating with one day thrown out       
                        corrarr[idx] = corr[0,1]
            
                    #again finding the outlier and calling that reality
                    meancval = round(np.mean(corrarr),2)
                    meanstd = round(np.std(corrarr),2)
                    goodind = np.argmax(abs(corrarr - meancval))
                    outcval = round(corrarr[goodind],2)
                    outind = agood[goodind]
                    indvEarnCorr[eind] = outcval
                    indvEarnValue[eind] = outcval
                    indvEarnFlux[eind] = np.std(earn[agood])/np.mean(earn[agood])
            
            #here we're setting non-significant correlation values to zero.        
            nonsig = ((indvEarnCorr > -0.3) & (indvEarnCorr < 0.3)).nonzero()[0]
            if any(nonsig): indvEarnCorr[nonsig] = 0
            nonvalid = (indvEarnCorr <= -1).nonzero()[0]
            if any(nonvalid):
                indvEarnCorr[nonvalid] = 0
                indvEarnValue[nonvalid] = np.nan
                    
            nonvalid = (indvEarnCorr >= 1).nonzero()[0]
            if any(nonvalid): 
                indvEarnCorr[nonvalid] = 0
                indvEarnValue[nonvalid] = np.nan
                    
    
    
            #Here we're calculating relative fluctuation in earnings and assigning a weight given 
            #the associated fluctuation in spending
            for elidx, element in enumerate(indvEarnFlux):
                if element != -99:
                    fluxRatio[elidx] = round(spendFlux[nameidx]/indvEarnFlux[elidx],3)
                    if spendFlux[nameidx] >= indvEarnFlux[elidx]:
                        indvWeight[elidx] = round(1.5 + np.log10(indvEarnFlux[elidx]/spendFlux[nameidx]),3)
                    else:  indvWeight[elidx] = round(1.5 + np.log10(spendFlux[nameidx]/indvEarnFlux[elidx]),3)
                    
            indvWeight = np.clip(indvWeight,0,1)        
            indvActualEscore = (1+fracSpendScore[nameidx])*indvEarnCorr*indvWeight*(1+indvEarnFrac)
            for sidx, score in enumerate(indvActualEscore):
                indvActualEscore[sidx] = round(score,2)
                
            indvEarnScore[nameidx] = round(eindvWeight*np.sum(indvActualEscore)/len(activeEarnNames),2)
    
            eTotalScore[nameidx] = ecorrWeight*((1+fracSpendScore[nameidx])*earnCorrScore[nameidx]*spendEarnWeight[nameidx])
            pTotalScore[nameidx] = pcorrWeight*((1+fracSpendScore[nameidx])*profitCorrScore[nameidx]*spendProfitWeight[nameidx])
            totalScore[nameidx] = round((pTotalScore[nameidx] + indvEarnScore[nameidx] +\
                                    eTotalScore[nameidx] + profitScore[nameidx]),2)
    
            if totalScore[nameidx] <= minCut: 
                recStart = 'MINIMIZE'
                colorList.append("#DC143C")
            if totalScore[nameidx] > minCut and totalScore[nameidx] <= redCut: 
                recStart = 'REDUCE'
                colorList.append("#FF8C00")
            if totalScore[nameidx] > redCut and totalScore[nameidx] < incCut: 
                recStart = 'NO CHANGE'
                colorList.append("#696969")
            if totalScore[nameidx] >= incCut and totalScore[nameidx] < maxCut: 
                recStart = 'INCREASE'
                colorList.append("#228B22")
            if totalScore[nameidx] >= maxCut: 
                recStart = 'MAXIMIZE'
                colorList.append("#0000CD")
    
            recStatement1 = recStart\
                        +'\tScore: '+str(totalScore[nameidx])#\
    #                        +'\nProfit Score: '+str(profitScore[nameidx])\
    #                        +'\nCorrelation with Profit Score: '+str(profitCorrScore[nameidx])\
    #                        +'\nCorrelation with Earn Score: '+str(earnCorrScore[nameidx])\
    #                        +'\nCorrelation with Individual Earn Score:'\
    #                        +'\n'+str(earncorr)\
    #                        +'\nFraction of Total Spending Score: '+str(fracSpendScore[nameidx])\
    #                        +'\nSpending fluctuation +/- '+str(spendflux)+'%'\
    #                        +'\nEarning fluctuation +/- '+str(earnflux)+'%'\
    #                        +'\n-----------------------------------'
    #        recStatement2 = recStart\
    #                    +'\tScore: '+str(totalScore[nameidx])\
    #                    +'\nProfitable Fraction of Days: '+'>>> '+str(profitScore[nameidx])+' <<<'\
    #                    +'\nFraction of Total Spend: '+str(fracSpendScore[nameidx])\
    #                    +'\nSpending fluctuation +/- '+str(spendFlux[nameidx])\
    #                    +'\nWeighted Spending fluctuation +/- '+str(wspendFlux[nameidx])\
    #                    +'\nOverall Earning fluctuation +/- '+str(earnFlux[nameidx])\
    #                    +'\nOverall Profit fluctuation +/- '+str(profitFlux[nameidx])\
    #                    +'\nCorrelation with Total Profit: '+str(profitCorrValue[nameidx])\
    #                    +'\nCorrelation with Total Earn: '+str(earnCorrValue[nameidx])\
    #                    +'\nSpend-Profit Weight: '+str(spendProfitWeight[nameidx])\
    #                    +'\nSpend-Earn Weight: '+str(spendEarnWeight[nameidx])\
    #                    +'\nProfit Correlation Score: '+'>>> '+str(round((1+fracSpendScore[nameidx])*spendProfitWeight[nameidx]*profitCorrScore[nameidx],2))+' <<<'\
    #                    +'\nOverall Earn Correlation Score: '+'>>> '+str(round((1+fracSpendScore[nameidx])*spendEarnWeight[nameidx]*earnCorrScore[nameidx],2))+' <<<'\
    #                    +'\nFraction of Total Earn:'\
    #                    +'\n'+str(indvEarnFrac)\
    #                    +'\nCorrelation with Individual Earn:'\
    #                    +'\n'+str(indvEarnValue)\
    #                    +'\nIndividual Earn/Spend weights:'\
    #                    +'\n'+str(indvWeight)\
    #                    +'\nIndividual Earning Score:'\
    #                    +'\n'+'>>> '+str(indvActualEscore)+' <<<'\
    #                    +'\n-----------------------------------'
            
            recStatement2 = recStart\
                        +'\tScore: '+str(totalScore[nameidx])\
                        +'\nProfitable Fraction of Days Score: '+'>>> '+str(round(profitScore[nameidx],2))+' <<<'\
                        +'\nFraction of Total Spend: '+str(fracSpendScore[nameidx])\
                        +'\nCorrelation with Total Profit: '+str(profitCorrValue[nameidx])\
                        +'\nCorrelation with Total Earn: '+str(earnCorrValue[nameidx])\
                        +'\nProfit Correlation Score: '+'>>> '+str(round(pTotalScore[nameidx],2))+' <<<'\
                        +'\nOverall Earn Correlation Score: '+'>>> '+str(round(eTotalScore[nameidx],2))+' <<<'\
                        +'\nCorrelation with Individual Earn:'\
                        +'\n'+str(indvEarnValue)\
                        +'\nIndividual Earning Score:'\
                        +'\n'+'>>> '+str(indvActualEscore)+' <<<'\
                        +'\n-----------------------------------'
                        
            
            recName = name.split()[0]
            if len(recName) <= 8: 
                recString1 = recName+':\t\t'+recStatement1
                recString2 = recName+':\t\t'+recStatement2
            else:
                recString1 = recName+':\t'+recStatement1
                recString2 = recName+':\t'+recStatement2
                
            recList1.append(recString1)
    
            recList2.append(recString2)

        #if currentCountry == 'USA': pdb.set_trace()     
        
        labelString='\n\n=============================\n'\
                        +'Profit Score Weight = '+str(pscoreWeight)\
                        +'\nProfit Correlation Weight = '+str(pcorrWeight)\
                        +'\nTotal Earn Correlation Weight = '+str(ecorrWeight)\
                        +'\nIndividual Earn Correlation Weight = '+str(round(eindvWeight,2))\
                        +'\n-----------------------------------\n'    
                  
        labelDict["upperLabelText"].set(upperLabelText + labelString)         
    
        for idx, name in enumerate(activeSpendNames):
        
            if idx == 0: 
                labelDict[name]["longText"].set('\n\n'+recList2[idx])
            else: labelDict[name]["longText"].set(recList2[idx])
            labelDict[name]["shortText"].set(recList1[idx])
            labelDict[name]["color"].set(colorList[idx])
            labelDict[name]["shortlabel"].configure(fg=labelDict[name]["color"].get())
            labelDict[name]["longlabel"].configure(fg=labelDict[name]["color"].get())
            
    
        
    else: 
        
        eTotalScore = np.zeros(len(activeSpendNames)) 
        pTotalScore = np.zeros(len(activeSpendNames)) 
        profitScore = np.zeros(len(activeSpendNames))  
        totalScore = np.zeros(len(activeSpendNames))  
        indvEarnScore = np.zeros(len(activeSpendNames)) 
     
        labelDict["upperLabelText"].set('')         

        for idx, name in enumerate(activeSpendNames):
        
            labelDict[name]["longText"].set('')
            labelDict[name]["shortText"].set('')
            labelDict[name]["color"].set('')

    global totalScore, pTotalScore, indvEarnScore, eTotalScore, profitScore
    global labelDict
#    pickle.dump(labelDict,open('labelPickle.p','wb'),protocol=2)
    
def AnalysisTop(event):

    global firstAnalysisPop, newAnalysisPop
    
    if (not firstAnalysisPop) or newAnalysisPop:
        if analysisPop.winfo_exists():
            analysisPop.destroy()
            
    if newAnalysisPop: newAnalysisPop = False

    analysisPop = tk.Toplevel()
    label = tk.Label(analysisPop, text="Analysis Text")
    label.pack(side='top', fill='x')

    labelDict = collections.OrderedDict()
    labelDict["upperLabelText"] = tk.StringVar()
    for idx, name in enumerate(activeSpendNames):
        
        labelDict[name] = {}
        labelDict[name]["longText"] = tk.StringVar()
        labelDict[name]["shortText"] = tk.StringVar()
        labelDict[name]["color"] = tk.StringVar()
    
    vsb = tk.Scrollbar(analysisPop, orient="vertical")

    text = tk.Text(analysisPop, width=30, height=20, state='disabled', 
                    fg='black',
                    yscrollcommand=vsb.set, highlightthickness=0)

    vsb.config(command=text.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
  
        
#    label = tk.Label(text, textvariable=labelDict["upperLabelText"], justify='left',
#        font = "Times 14 bold")
#    text.window_create("end", window=label)
#    for idx, name in enumerate(activeSpendNames):
        
#        label = tk.Label(text, textvariable=labelDict[name]["shortText"], justify='left', 
#            fg = labelDict[name]["color"].get(), 
#            font = "Times 16 bold")
#        text.window_create("end", window=label)

#    for idx, name in enumerate(activeSpendNames):
        
#        label = tk.Label(text, textvariable=labelDict[name]["longText"], justify='left', 
#            fg = labelDict[name]["color"].get(), 
#            font = "Times 16 bold")
#        text.window_create("end", window=label)

    labelDict["upperLabel"] = tk.Label(text, textvariable=labelDict["upperLabelText"], justify='left',
        font = "Times 14 bold")
    
    for idx, name in enumerate(activeSpendNames):
        
        labelDict[name]["shortlabel"] = tk.Label(text, textvariable=labelDict[name]["shortText"], 
            justify='left', 
            font = "Times 16 bold")
        text.window_create("end", window=labelDict[name]["shortlabel"])

    text.window_create("end", window=labelDict["upperLabel"])
    for idx, name in enumerate(activeSpendNames):
        
        labelDict[name]["longlabel"] = tk.Label(text, textvariable=labelDict[name]["longText"], 
            justify='left', 
            font = "Times 16 bold")
        text.window_create("end", window=labelDict[name]["longlabel"])

            

    text.pack(side="left", fill="both", expand=True)

  
    global labelDict
    UpdateLabelText()
    
    firstAnalysisPop = False
    global analysisPop
    analysisPop.geometry('400x775+558+0')


    
def newInstance(event):
    global pause
    pause = False
    global app
    global appGeometry
    app.destroy()
    
    app = AnalysisApp()
    app.geometry(appGeometry)
    ani0 = animation.FuncAnimation(f0, animate, interval=500)
    app.update()
    app.mainloop()

def changePlot(self, plotName):


    global pause
    pause = False
    global plotChoice
    plotChoice = plotName

    if plotChoice == 'earnVspend':
        self.show_frame(PageOne)
    elif plotChoice == 'profitVspend':
        self.show_frame(PageTwo)
    elif plotChoice == 'spendKnuckle':
        self.show_frame(PageThree)




def animate(i):

    global pause
    if not pause:
        global totalScore, pTotalScore, indvEarnScore, eTotalScore, profitScore, weightDict
        dates = bigDict['Dates']
        profit = bigDict["Countrywise"][currentCountry]["Profit"]
        alphaLevel = 0.25
        colors = ['#800517','#9F000F','#9F000F','#E42217','#FF2400',
                      '#C35817','#CC6600','#FF8040','#F88158','#F9966B',
                      '#FBB917','#FDD017','#FFFF00','#FFDB58','#FFF380',
                      '#6AA121','#6CBB3C','#52D017','#A1C935','#54C571',
                      '#3B9C9C','#5CB3FF','#6495ED','#1589FF','#2B65EC',
                      '#0000A0','#6C2DC7','#842DCE','#893BFF','#A23BEC','#9E7BFF' ]
    
        spendgood=[]
        for name in currentSpendNames:
            spendgood.extend(list(bigDict["Spend"][name]["Nonzero"]))
    
        spendgood = np.array(spendgood)
        spendgood = np.unique(spendgood)
        inrange = ((spendgood >= newStartInd) & (spendgood <= newEndInd)).nonzero()[0]
        spendgood = spendgood[inrange]
        
        earngood=[]
        for name in currentEarnNames:
            earngood.extend(list(bigDict["Earn"][name]["Nonzero"]))
    
        earngood = np.array(earngood)
        earngood = np.unique(earngood)
        inrange = ((earngood >= newStartInd) & (earngood <= newEndInd)).nonzero()[0]
        earngood = earngood[inrange]

        good = np.array(list(set(spendgood).intersection(earngood)))

        if any(omitInds):
            for elem in omitInds:
                ind = (good == elem).nonzero()
                if ind: good = np.delete(good, ind)

#############################################################################
#############   PLOT A0 BELOW  ################################################
#############################################################################
        
        if plotChoice == 'scoreBars':     
            
            a0.clear()
            ind = np.arange(len(totalScore))
            width = 0.15
            a0.bar(ind, totalScore, width, label='Total Score', color='#000000')
            a0.bar(ind+width, profitScore, width, color='#3090C7', label='Profit Score')
            a0.bar(ind+2*width, pTotalScore, width, color='#C76730', label='Profit Correlation')
            a0.bar(ind+3*width, eTotalScore, width, color='#C454A8', label='Total Earn')
            a0.bar(ind+4*width, indvEarnScore, width, color='#54C571', label='Indvidual Earn')
            tickNames = []
            for accname in activeSpendNames:
                tickNames.append(accname.split()[0])
            a0.set_xticks(ind + 2*width)
            a0.set_xticklabels(tickNames, rotation=60, ha='right')
            a0.plot([0,len(totalScore)],[weightDict["minCutWvar"],weightDict["minCutWvar"]], 
               color='#DC143C' )
            a0.plot([0,len(totalScore)],[weightDict["redCutWvar"],weightDict["redCutWvar"]], 
               color='#FF8C00' )
            a0.plot([0,len(totalScore)],[weightDict["incCutWvar"],weightDict["incCutWvar"]], 
               color='#228B22' )
            a0.plot([0,len(totalScore)],[weightDict["maxCutWvar"],weightDict["maxCutWvar"]], 
               color='#0000CD' )
            
            a0.legend(loc='upper right', bbox_to_anchor=(1.01, 1.38), fontsize =10)
            
            ymin = np.min(np.append(weightDict["minCutWvar"], [totalScore, profitScore,
                    pTotalScore, eTotalScore, indvEarnScore])) - 0.1
            ymax = np.max(np.append(weightDict["maxCutWvar"], [totalScore, profitScore,
                    pTotalScore, eTotalScore, indvEarnScore])) + 0.1

            a0.set_ylabel('Score Breakdown')
            a0.set_ylim([ymin, ymax])
            a0.text(len(totalScore)+0.01*len(totalScore), weightDict["minCutWvar"], 'MINIMIZE', 
                style='italic', color='#DC143C')
            a0.text(len(totalScore)+0.01*len(totalScore), weightDict["redCutWvar"], 'REDUCE', 
                style='italic', color='#FF8C00')
            a0.text(len(totalScore)+0.01*len(totalScore), weightDict["incCutWvar"], 'INCREASE', 
                style='italic', color='#228B22')
            a0.text(len(totalScore)+0.01*len(totalScore), weightDict["maxCutWvar"], 'MAXIMIZE', 
                style='italic', color='#0000CD')
        #bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
            
#############################################################################
#############   PLOT A1 BELOW  ################################################
#############################################################################
        
        if plotChoice == 'earnVspend':     
            
            a1.clear()
    
            if len(good) >= 1:
                
                for idx, name in enumerate(currentSpendNames):
        
                    if idx == 0: spenddata = np.array(bigDict["Spend"][name]["DailyTotal"])
                    else: spenddata += np.array(bigDict["Spend"][name]["DailyTotal"])
        
                for idx, name in enumerate(currentEarnNames):
        
                    if idx == 0: earndata = np.array(bigDict["Earn"][name]["DailyTotal"])
                    else: earndata += np.array(bigDict["Earn"][name]["DailyTotal"])
        
    
                spendString = 'Spend/day ('
                firstBreak = False
                secondBreak = False
                thirdBreak = False
                breakSize = 30 #characters in spendString after which to insert a break
                for indx, name in enumerate(currentSpendNames):
                    if indx == 0:
                        spendString += name.split()[0]
                    else:
                        spendString += '+'+name.split()[0]
                    if len(spendString) > breakSize and not firstBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        firstBreak = True
                    if len(spendString) > breakSize*2 and not secondBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        secondBreak = True
                    if len(spendString) > breakSize*3 and not thirdBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        thirdBreak = True
                        
                spendString += ')'
        
                earnString = 'Earn/day ('
                firstBreak = False
                secondBreak = False
                thirdBreak = False
                
                for indx, name in enumerate(currentEarnNames):
                    if indx == 0:
                        earnString += name.split()[0]
                    else:
                        earnString += '+'+name.split()[0]
                    if len(earnString) > 25 and not firstBreak and name != currentEarnNames[-1]:
                        earnString += '\n'
                        firstBreak = True
                    if len(earnString) > 50 and not secondBreak and name != currentEarnNames[-1]:
                        earnString += '\n'
                        secondBreak = True
                    if len(earnString) > 75 and not thirdBreak and name != currentEarnNames[-1]:
                        earnString += '\n'
                        thirdBreak = True
                                  
                earnString += ')'
                
        
                a1.plot(spenddata[good], earndata[good],'bo')
                a1.plot(spenddata[good], earndata[good],'r--')
    
                for elem in good:
                    font_dict = {'family':'serif', 'color':colors[elem], 'size':15}
                    a1.text(spenddata[elem],earndata[elem],dates[elem], fontdict=font_dict)
    
                a1.set_ylabel(earnString)
                a1.set_xlabel(spendString)    
                f1xminmax = f1.gca().get_xlim()
                a1.plot(f1xminmax, [0,0], 'k--', linewidth=3.0 )
        
    
         
                a1.set_title(currentCountry+': '+dates[good[0]]+' to '+dates[good[-1]])
       
                f1yminmax = f1.gca().get_ylim()
     
                if f1yminmax[0] < 0 and f1yminmax[1] > 0:
                    a1.fill_between(f1xminmax, f1yminmax[0], 0, facecolor='red', alpha=alphaLevel)   
                elif f1yminmax[1] <= 0:
                    a1.fill_between(f1xminmax, f1yminmax[0], 0, facecolor='red', alpha=alphaLevel)

#############################################################################
#############   PLOT A2 BELOW  ################################################
#############################################################################
        
     
        elif plotChoice == 'profitVspend':
            
            a2.clear()
    
            if len(spendgood) >= 1:
                
                for idx, name in enumerate(currentSpendNames):
        
                    if idx == 0: spenddata = np.array(bigDict["Spend"][name]["DailyTotal"])
                    else: spenddata += np.array(bigDict["Spend"][name]["DailyTotal"])
    
    
                spendString = 'Spend/day ('
                firstBreak = False
                secondBreak = False
                thirdBreak = False
                breakSize = 30 #characters in spendString after which to insert a break
                for indx, name in enumerate(currentSpendNames):
                    if indx == 0:
                        spendString += name.split()[0]
                    else:
                        spendString += '+'+name.split()[0]
                    if len(spendString) > breakSize and not firstBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        firstBreak = True
                    if len(spendString) > breakSize*2 and not secondBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        secondBreak = True
                    if len(spendString) > breakSize*3 and not thirdBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        thirdBreak = True
                        
                spendString += ')'
        
    
                a2.plot(spenddata[spendgood], profit[spendgood],'bo')
                a2.plot(spenddata[spendgood], profit[spendgood],'r--')
    
                for elem in spendgood:
                    font_dict = {'family':'serif', 'color':colors[elem], 'size':15}
                    a2.text(spenddata[elem],profit[elem],dates[elem], fontdict=font_dict)
    
                a2.set_ylabel('Total Profit per day')
                a2.set_xlabel(spendString)    
                a2.set_title(currentCountry+': '+dates[good[0]]+' to '+dates[good[-1]])
  
                #f2xminmax = f2.gca().get_xlim()
                #a2.plot(f2xminmax, [0,0], 'k--', linewidth=3.0 )
        
    
         
     
                #f2yminmax = f2.gca().get_ylim()
     
                #if f2yminmax[0] < 0 and f2yminmax[1] > 0:
                #    a2.fill_between(f2xminmax, f2yminmax[0], 0, facecolor='red', alpha=alphaLevel)   
                #elif f2yminmax[1] <= 0:
                #    a2.fill_between(f2xminmax, f2yminmax[0], 0, facecolor='red', alpha=alphaLevel)
                    
        elif plotChoice == 'spendKnuckle':
            
            a3.clear()
    
            if len(spendgood) >= 1:
                
                for idx, name in enumerate(currentSpendNames):
        
                    if idx == 0: spenddata = np.array(bigDict["Spend"][name]["DailyTotal"])
                    else: spenddata += np.array(bigDict["Spend"][name]["DailyTotal"])
    
    
                spendString = 'Spend/day ('
                firstBreak = False
                secondBreak = False
                thirdBreak = False
                breakSize = 30 #characters in spendString after which to insert a break
                for indx, name in enumerate(currentSpendNames):
                    if indx == 0:
                        spendString += name.split()[0]
                    else:
                        spendString += '+'+name.split()[0]
                    if len(spendString) > breakSize and not firstBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        firstBreak = True
                    if len(spendString) > breakSize*2 and not secondBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        secondBreak = True
                    if len(spendString) > breakSize*3 and not thirdBreak and name != currentSpendNames[-1]:
                        spendString += '\n'
                        thirdBreak = True
                        
                spendString += ')'
        
    
                a3.plot(spenddata[spendgood], profit[spendgood],'bo')
                a3.plot(spenddata[spendgood], profit[spendgood],'r--')
    
                for elem in spendgood:
                    font_dict = {'family':'serif', 'color':colors[elem], 'size':15}
                    a3.text(spenddata[elem],profit[elem],dates[elem], fontdict=font_dict)
    
                a3.set_ylabel('Total Profit per day')
                a3.set_xlabel(spendString)    
                f3xminmax = f3.gca().get_xlim()
                a3.plot(f3xminmax, [0,0], 'k--', linewidth=3.0 )
        
    
         
                a3.set_title(currentCountry+': '+dates[good[0]]+' to '+dates[good[-1]])
       
                f3yminmax = f3.gca().get_ylim()
     
                if f3yminmax[0] < 0 and f3yminmax[1] > 0:
                    a3.fill_between(f3xminmax, f3yminmax[0], 0, facecolor='red', alpha=alphaLevel)   
                elif f3yminmax[1] <= 0:
                    a3.fill_between(f3xminmax, f3yminmax[0], 0, facecolor='red', alpha=alphaLevel)
                    
       
        pause = True

f0 = Figure(figsize=(7,5.2))
a0 = f0.add_subplot(111)
f0.subplots_adjust(bottom=0.25, top=0.8, right=0.85, left=0.1)
f1 = Figure(figsize=(7,4.7))
a1 = f1.add_subplot(111)
#f1.subplots_adjust(bottom=0.2, left=0.2)
f2 = Figure(figsize=(7,4.7))
a2 = f2.add_subplot(111)
#f2.subplots_adjust(bottom=0.2, left=0.2)
f3 = Figure(figsize=(7,4.7))
a3 = f3.add_subplot(111)
#f2.subplots_adjust(bottom=0.2, left=0.2)


#f1 = Figure()
#a1 = f1.add_subplot(111)
#f2 = Figure()
#a2 = f2.add_subplot(111)

def exitCommand(event):
    print("quitting...")
    sys.exit(0)

class AnalysisApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)


        container = tk.Frame(self)
        container.grid(sticky='NSEW', row=0, column=0)
        event=False
        global event
        self.update()
        getNewXLdata()

        tk.Tk.wm_title(self, bigDict["Filename"])
        countryNames = list(bigDict["Countries"].keys())
        for country in countryNames:
            if bigDict["Countries"][country]["ActiveEarn"] == []:
                countryNames.remove(country)
            elif  bigDict["Countries"][country]["ActiveSpend"] == []:
                countryNames.remove(country)
                
        currentCountry = countryNames[0]
        plotChoice = 'scoreBars'
        activeSpendNames = bigDict["Countries"][currentCountry]["ActiveSpend"]
        activeEarnNames = bigDict["Countries"][currentCountry]["ActiveEarn"]
        currentSpendNames = [activeSpendNames[0]]
        currentEarnNames = [activeEarnNames[0]]
        currentSpendIndices = [0]
        currentEarnIndices = [0]
        newStartInd = 0
        newEndInd = len(bigDict["Dates"]) - 1
        omitInds = []
        global bigDict, currentCountry, plotChoice, currentSpendNames
        global currentEarnNames, currentSpendIndices
        global currentEarnIndices, newStartInd, newEndInd, omitInds
        global activeSpendNames, activeEarnNames

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        settingsmenu = tk.Menu(menubar, tearoff=0)
        
   
        settingsmenu.add_command(label="Spend Score Basics", command=lambda: setpop1(event), 
            accelerator='Cmd-B')
        settingsmenu.add_command(label="Profit Score", command=lambda: setpop2(event), 
            accelerator='Cmd-P')
        settingsmenu.add_command(label="Correlation Analysis", command=lambda: setpop3(event), 
            accelerator='Cmd-C')
        settingsmenu.add_command(label="Weights", command=lambda: setpop4(event), 
            accelerator='Cmd-Y')


        filemenu.add_cascade(label="Documentation", menu=settingsmenu)
#        filemenu.add_command(label='Exit', command=lambda: exitCommand(), accelerator='Ctrl+Q')
        filemenu.add_command(label="Open New Excel File", command=lambda: newInstance(event),accelerator='Cmd-O')
        filemenu.add_command(label="Change Weights", command=lambda: weightPop(event), accelerator='Cmd-W')


        filemenu.add_command(label='Exit', command=lambda: exitCommand(event), accelerator='Cmd-X')     
        menubar.add_cascade(label='File', menu=filemenu)

#        plotmenu = tk.Menu(menubar, tearoff=0)

#        plotmenu.add_command(label='Spend vs. Earn', command=lambda: changePlot(self, 'earnVspend'))
        #plotmenu.add_command(label='Profit vs. Spend', command=lambda: changePlot(self, 'profitVspend'))
        #plotmenu.add_command(label="Spend vs. Knuckle", command=lambda: changePlot(self, 'spendKnuckle'))
#        plotmenu.add_command(label="Earn Accounts", command=lambda: changePlot(self, 'earnAccounts'))

#        menubar.add_cascade(label='Plot', menu=plotmenu)

        
        countrymenu = tk.Menu(menubar, tearoff=0)
        popupwindowmenu = tk.Menu(menubar, tearoff=0)

        for name in countryNames:
            countrymenu.add_command(label=name, command=partial(choose_country, name))
        menubar.add_cascade(label='Country', menu=countrymenu)

        popupwindowmenu.add_command(label="New Spend Accounts Window", command=lambda: SpendTop(event),
            accelerator='Cmd-S')
        popupwindowmenu.add_command(label='New Earn Accounts Window', command=lambda: EarnTop(event),
            accelerator='Cmd-E')
        popupwindowmenu.add_command(label='New Date Selector Window', command=lambda: DatesTop(event),
            accelerator='Cmd-D') 
        popupwindowmenu.add_command(label='New Analysis Text Window', command=lambda: AnalysisTop(event),
            accelerator='Cmd-A') 
        menubar.add_cascade(label='Selection Windows', menu=popupwindowmenu)

        tk.Tk.config(self, menu=menubar)



        self.bind_all("<Command-x>", exitCommand)
        self.bind_all("<Command-s>", SpendTop)
        self.bind_all("<Command-e>", EarnTop)
        self.bind_all("<Command-d>", DatesTop)
        self.bind_all("<Command-a>", AnalysisTop)
        self.bind_all("<Command-w>", weightPop)
        self.bind_all("<Command-b>", setpop1)
        self.bind_all("<Command-p>", setpop2)
        self.bind_all("<Command-c>", setpop3)
        self.bind_all("<Command-y>", setpop4)
        self.bind_all("<Command-o>", newInstance)

        firstDatePop = True
        global firstDatePop
        firstSpendPop = True
        global firstSpendPop
        firstEarnPop = True
        global firstEarnPop
        firstAnalysisPop = True
        newAnalysisPop = False
        global firstAnalysisPop
        global newAnalysisPop
        firstRecPop = True
        global firstRecPop


        self.frames = {}

#        for F in (PageOne, PageTwo, PageThree):            
#            frame = F(container, self)
#            self.frames[F] = frame
#            frame.grid(row=0, column=0, sticky="nsew")

            
        frame1 = PageOne(container, self)
        self.frames[PageOne] = frame1
        frame1.grid(row=0, column=0, sticky="nsew")

#        frame2 = PageTwo(container, self)
#        self.frames[PageTwo] = frame2
#        frame2.grid(row=0, column=0, sticky="nsew")

        self.show_frame(PageOne)
       
        DatesTop(event)
        SpendTop(event)
        EarnTop(event)
        AnalysisTop(event)
        
    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


        


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
#        label = tk.Label(self, text="Score Breakdown", font=LARGE_FONT)
#        label.pack(pady=10, padx=10)
        frame = tk.Frame(self)
        frame.pack(side=tk.LEFT)

        canvas = FigureCanvasTkAgg(f0, frame)
        canvas.draw()

        canvas._tkcanvas.config(highlightthickness=0)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, frame)
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Spend vs. Profit", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        frame = tk.Frame(self)
        frame.pack(side=tk.LEFT)

        canvas = FigureCanvasTkAgg(f2, frame)
        canvas.draw()
        
        canvas._tkcanvas.config(highlightthickness=0)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, frame)
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Spend vs. Knuckle", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        frame = tk.Frame(self)
        frame.pack(side=tk.LEFT)

        canvas = FigureCanvasTkAgg(f3, frame)
        canvas._tkcanvas.config(highlightthickness=0)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, frame)
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)


app = AnalysisApp()
appGeometry = "555x455+0+0"
app.geometry(appGeometry)

ani0 = animation.FuncAnimation(f0, animate, interval=500)
#ani1 = animation.FuncAnimation(f1, animate, interval=500)
#ani2 = animation.FuncAnimation(f2, animate, interval=500)
#ani2 = animation.FuncAnimation(f3, animate, interval=500)

app.mainloop()
