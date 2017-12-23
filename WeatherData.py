import numpy as np
import matplotlib.pyplot as pp
import seaborn
import urllib.request

#urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt', 'stations.txt')
#open('stations.txt','r').readlines()[:10]
'''
TUTORIAL: TASK 1: Convert the data from the txt file into a NumPy array that can be manipulated
'''
stations = {}

for line in open('stations.txt', 'r'): #reads lines of stations file and returns those containing 'GSN'
    if 'GSN' in line: #if GSN is in the line
        fields = line.split() #split the line according to white spaces
        stations[fields[0]] = ' '.join(fields[4:])
#add members to the dictionary 'stations' that contain the first member of the line
#and the name of the station and other info joined by a space

#print(len(stations))

def find_station(s): #function to find stations that match certain criteria
    found = {code: name for code, name in stations.items() if s in name}
    print(found)
#create dictionary of codes and names of stations if they match the criteria

#find_station('LIHUE')
#find_station('SAN DIEGO')
#find_station('MINNEAPOLIS')
#find_station('IRKUTSK')
#finding station numbers for analysis

datastations = ['USW00022536','USW00023188','USW00014922','RSM00030710']
#open('USW00022536.dly', 'r').readlines()[:10]

def parse_file(file): #parses one of the datastations files to create a numpy array
    return np.genfromtxt(file, #use the file
                         delimiter = dly_delimiter, #delimiter for what the column lengths are
                         usecols = dly_usecols, #which columns to use
                         dtype = dly_type, #which type of data they are
                         names = dly_names) #names of columns

#arguments for the genfromtxt method are assigned below accowring to the format of the document
dly_delimiter = [11,4,2,4] + [5,1,1,1]*31 #the code is 11 characters, the year is 4, the month is 2, the type of data is 4, the data is 5, the 1,1,1 are for the flags
dly_usecols = [1,2,3] + [4*i for i in range(1,32)] #we only want the second, third, fourth and fifth elements [0] is not included as we dont need the code
dly_type = [np.int32, np.int32, (np.str,4)] + [np.int32]*31 #the year, month are integers, the data type is string, and the data is also an integer and there are *31 entries
dly_names = ['year', 'month','obs'] + [str(day) for day in range(1,32)] #names of fields are yr,mth,observed data, and day number

lihue = parse_file('USW00022536.dly')

def unroll(data): #function to solve the problem of all of the dates sitting on the same row
    startdate = np.datetime64('{}-{:02}'.format(data['year'],data['month'])) #definites startdate object as np date type yyyy-mm-dd
    dates = np.arange(startdate,startdate + np.timedelta64(1,'M'),np.timedelta64(1,'D')) #creates range of dates from start date of month to one month from then with intervals of 1 day
    rows = [(date,data[str(i+1)]/10) for i,date in enumerate(dates)] #defines rows as list of tuples of the day number, and the observed data pulled from the fed row of the file
    return np.array(rows,dtype=[('date','M8[D]'),('value','d')]) #create an array using the rows with data type month-date and value decimal

#unroll(lihue[0])

def get_obs(filename,obs): #function to get observed data in form that can be manipulated
    return np.concatenate([unroll(row) for row in parse_file(filename) if row[2] == obs])
#concatenate the arrays all of the values that are accessed using the unroll function of the parsed file as long as the second row of the file is the requested data type
#this creates a full array of the observed data values

'''
TUTORIAL: TASK 2: Deal with misleading data (such as -999.9 values) by integrating missing data
'''

'''
TASK 2 - Step 1: Remove all misleading data (=-999.9)
'''
def get_obs(filename,obs): #adjusting original function to get all of the data in a date/value format
    data = np.concatenate([unroll(row) for row in parse_file(filename) if row[2] == obs])
#concatenate the arrays all of the values that are accessed using the unroll function of the parsed file as long as the second row of the file is the requested data type (assign to data variable)
    data['value'][data['value'] == -999.9] = np.nan
#for all the values in the array that match -999.9, assign them to a "missing value" aka Not A Number
    return data #return the data after removing the -999.9 values

lihue_tmax = get_obs('USW00022536.dly','TMAX')
lihue_tmin = get_obs('USW00022536.dly','TMIN')

#pp.plot(lihue_tmax['date'],lihue_tmax['value']) #plot the date value components of the data in the file that matches the max temp
#pp.plot(lihue_tmin['date'],lihue_tmin['value']) #plot the date value components of the data in the file that matche the min temp
#pp.show()

'''
Problem: you cannot caclulate a mean as np.mean cannot evaluate NaN values

TASK 2 - Step 2: Replace misleading data with data that can be used in calculations (using numpy interpolations)
'''

def fill_nans(data):
    dates_float = data['date'].astype(np.float64)
    nan = np.isnan(data['value'])
    data['value'][nan] = np.interp(dates_float[nan],dates_float[~nan],data['value'][~nan])

fill_nans(lihue_tmax)
fill_nans(lihue_tmin)

#np.mean(lihue_tmin['value']),np.mean(lihue_tmax['value'])

'''
TUTORIAL: TASK 3: Smooth the data points' short term fluctuations to help see trends using a running mean
'''

def plot_smoothed(t,win=10): #function to calculate runnning averages
    smoothed = np.correlate(t['value'],np.ones(win)/win,'same')
#create dataset by making each value the average of those in the specified window
#correlate method first argument is the data to be correlated
#second argument is the weighting of each datapoint (1/window)
#third is the length of the returned array ('same' takes the shortest dataset between first and second arguments and uses that length)
    pp.plot(t['date'],smoothed) #plot the smoothed data and dates

#plot_smoothed(lihue_tmin)
#pp.plot(lihue_tmin[10000:12000]['date'],lihue_tmin[10000:12000]['value'])

#plot_smoothed(lihue_tmin[10000:12000])
#plot_smoothed(lihue_tmin[10000:12000],20)
#pp.show()

pp.figure(figsize=(10,6))

for i,code in enumerate(datastations): #for the 4 datastations, plot the min and max smoothed values over 365 days
    pp.subplot(2,2,i+1) #plotting layout of 2 columns and two rows and the graph taking the positon of i + 1 (1,2,3,4)

    plot_smoothed(get_obs('{}.dly'.format(code),'TMIN'),365) #plot the date and smoothed values of tmin for each datastation
    plot_smoothed(get_obs('{}.dly'.format(code),'TMAX'),365) #plot the date and smoothed values of tmin for each datastation

    pp.title(stations[code]) #title each graph with the name of the station
    pp.axis(xmin=np.datetime64('1952'),xmax=np.datetime64('2012'),ymin=-10,ymax=30) #set the axes min,max so all are plotted over same time range

pp.tight_layout() #adjust spacing between graphs and titles
