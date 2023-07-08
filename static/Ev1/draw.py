import matplotlib.pyplot as plt


days = {"1":"Pazartesi","2":"Sali","3":"Carsamba","4":"Persembe","5":"Cuma","6":"Cumartesi","7":"Pazar"}

columns = ["Zaman", "Aydinlatma","Sac kurutucu","Buzdolabi" ,"kettle","Tost makinasi",
            "kahve makinasi","firin","camasir makinasi","bulasik makinasi","camasir kurutma",
            "Elektrik makinasi","Firin","Modem","TV","Klima","Toplam","olcekli"]

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
    time = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    sumOfLoads = []
    loadMat.remove([])
    for each in loadMat:
        print(each)
        sumOfLoads.append(each[len(each)-2])

    plt.figure(1)
    plt.title(days[day])
    plt.plot(time,sumOfLoads)
    plt.xlabel("Zaman")
    plt.ylabel("Tüketilen Toplam Yük Miktarı")
    plt.savefig(days[day])
    plt.show()
