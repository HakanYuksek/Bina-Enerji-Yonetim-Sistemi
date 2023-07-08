import sqlite3


conn = sqlite3.connect("DB.db")
cur = conn.cursor()


# Let's hold the day in the dict
days = {"1":"Pazartesi","2":"Sali","3":"Carsamba","4":"Persembe","5":"Cuma","6":"Cumartesi","7":"Pazar"}

columns = ["Zaman", "Aydinlatma","Sac kurutucu","Buzdolabi" ,"kettle","Tost makinasi",
            "kahve makinasi","firin","camasir makinasi","bulasik makinasi","camasir kurutma",
            "Elektrik makinasi","Firin","Modem","TV","Klima","Toplam","olcekli"]

# 0: Low, 1: Medium, 2: High Priority
priority = [0,1,1,2,2,1,0,0,1,2,2,1,0,0,0]

threshold = 4000

# We should read the data by the day
for day in days.keys():

    print("---------------------------------------")
    print(days[day]," --------->")
    print("----------------------------------------")

    fileName ="C:\\Users\\USER\\Desktop\\Dersler\\dördüncü sınıf\\Çok Disiplinli Tasarım Projesi\\Yük Öteleme\\Ev3\\"+day+".txt"

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
        values = "3,"+day
        while j < len(line):
            if "," in line[j]:
                line[j] = line[j].replace(",",".")
            inThisHour.append(float(line[j]))
            values += ","+str(line[j]) 
            j += 1

        loadMat.append(inThisHour)
        if len(values) >=19:
            query = "insert into Loads(userID,day,hour,Aydınlatma,Sac_kurutucu,Buzdolabi,kettle,Tost_makinesi,kahve_makinesi,firin,camasir_makinesi,bulasık_makinesi,camasir_kurutma,Elektrik_makinasi,firin1,Modem,TV,Klima,Elektrikli_Arac_Sarzi,Toplam,olcekli) Values("+values[:len(values)]+")"
            print(query)
            cur.execute(query)
            conn.commit()
        i += 1
        print("ekledim")

    # We read the for this day
    # Now we can apply the algorithm for this day
    loadMat.remove([])
    



conn.close()
