import matplotlib.pyplot as plt

# We should read the data by the day
for day in days.keys():

    print("---------------------------------------")
    print(days[day]," --------->")
    print("----------------------------------------")

    fileName = day+".txt"

    file = open(fileName,"r")

    # The first two line of the file is unnecessary for us
    file.readline()
    file.readline()
    i = 0

    # This matrix holds the load knowledge for one day
    loadMat = []

    # Let's read the data from the file
    while i < 25:
        line = str(file.readline())
        line = line.split()
        
        # This holds the loads for this hour
        inThisHour = []

        j = 0
        while j < len(line):
            if "," in line[j]:
                line[j] = line[j].replace(",",".")
            inThisHour.append(float(line[j]))
            j += 1

        loadMat.append(inThisHour)
        
        i += 1



    # Let's draw the results
    time = []
    sumOfLoads = []
    for each in loadMat:
        time.append(each[0])
        sumOfLoads.append(each[len(each)-2])

    plt.figure(1)
    plt.title(days[day])
    plt.plot(time,sumOfLoads)
    plt.xlabel("Time")
    plt.ylabel("Loads")
    plt.savefig(days[day])
    plt.show()
