import numpy as np
import matplotlib.pyplot as pp
import seaborn
import urllib.request

#urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt', 'stations.txt')
#open('stations.txt','r').readlines()[:10]
'''
TASK 1: Convert the data from the txt file into a NumPy array that can be manipulated
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
#concatenate the arrays all of the values that are accessed using the unroll function of the parsed file as long as the second row of the file is the recorded observed data
#this creates a full array of the observed data values

'''
TASK 2: Deal with misleading data (such as -999 values) by integrating missing data
'''

lihue_tmax = get_obs('USW00022536.dly','TMAX')
lihue_tmin = get_obs('USW00022536.dly','TMIN')

pp.plot(lihue_tmax['date'],lihue_tmax['value'])
pp.show()

'''
NEED TO COMMENT
'''
