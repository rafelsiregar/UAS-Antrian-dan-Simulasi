import random
import numpy as np
import time
import copy

class Process: 
    def __init__(self, id, arrival_time, maximum_service_time):
        self.id = id
        self.arrival_time = arrival_time
        self.waiting_time = 0
        self.maximum_service_time = maximum_service_time
        self.departure_time = 0

    def set_departure_time(self, departure_time):
        self.departure_time=departure_time



def maximum_time(obj):
    return obj.maximum_service_time



class Simulation:
    def __init__(self, iat, max_service_time, bounds):
        #Clock
        self.clock = 0.0
        #Waktu Kedatangan
        self.arrival_time = self.generate_interarrival(iat)
        #Waktu Keberangkatan
        self.departure_time = float('inf')
        #ID Proses
        self.id_process = 1
        #Jumlah proses di sistem (indeks ke 0 selalu merupakan yang dilayani)
        self.process_list = []
        #Jumlah proses dalam sistem
        self.num_in_system = 0
        #Jumlah kedatangan
        self.num_arrival = 0
        #Jumlah keberangkatan
        self.num_processed = 0
        #Total Waiting Time
        self.total_waiting_time = 0.0
        #Inter Arrival Time
        self.mean_iat = iat
        #Service Time
        self.mean_max_service_time = max_service_time
        #Actual Time
        self.actual_service_time = random.uniform(bounds[0], bounds[1])
        #Status bergabung
        self.status = False
        #Jumlah waiting time lebih dari 5 menit
        self.num_customer_mtf = 0
        #Waiting time
        self.maximum_waiting_time = 0


    def generate_interarrival(self,iat):
        return np.random.exponential(1./iat)

    def generate_max_service_time(self, mean_max_service_time):
        return np.random.exponential(1./mean_max_service_time)

    #Kalau dijalankan secara FIFO
    def advance_time_fifo(self):
        event = min(self.arrival_time,self.departure_time)
        print("---------------------------------------------------------------------")
        print("Last Arrival Time : {}".format(round(self.arrival_time, 2)))
        print("Last Departure Time : {}".format(round(self.departure_time, 2)))
        print("---------------------------------------------------------------------")
        self.clock = event
        if self.arrival_time < self.departure_time:
            self.handle_arrival()
        else:
            self.handle_departure()
        #print("---------------------------------------------------------------------")
        

    def handle_arrival(self):
        max_service_time = self.generate_max_service_time(self.mean_max_service_time)
        #Melihat apakah proses akan bergabung atau tidak
        if self.actual_service_time > max_service_time:
            self.status = False
        else : 
            self.status = True
        #Kalau jadi gabung
        if self.status == True :
            #Jumlah proses dalam sistem
            self.num_in_system+=1
            #Menambah customer ke kedatangan di server A
            self.num_arrival +=1
            #Memasukkan proses ke dalam queue
            self.id_process = hex(random.getrandbits(8))
            self.process_list.append(Process(self.id_process, self.arrival_time, max_service_time))
            if self.num_in_system<=1:
                print("Queue is empty, serving process {}".format(self.id_process))
                #Mengeluarkan dari daftar antrian
                self.departure_time=self.clock+self.actual_service_time  
                self.process_list[0].set_departure_time(self.departure_time)
            else :
                print("Queue is busy, please wait")

        #Kalau tidak jadi gabung
        else :
            print("Process is not processed because the actual time service is more than maximum")
        self.arrival_time = self.clock+self.generate_interarrival(self.mean_iat)

    def handle_departure(self):
        #Proses meninggalkan CPU
        self.process_list.pop(0)
        self.num_in_system-=1
        print("Process has leaved at time {}".format(round(self.clock,2)))
        #Menambah jumlah proses yang keluar
        self.num_processed+=1
        #Kalau masih ada proses lain di dalam sistem
        if self.num_in_system>0 :
            print("There are still {} process(es) in the system.".format(self.num_in_system))
            #Menghitung delay time untuk proeses yang akan dilayani selanjutnya
            waiting_time = self.clock-self.process_list[0].arrival_time
            self.maximum_waiting_time = max(waiting_time, self.maximum_waiting_time)
            if waiting_time >= 5 : 
                self.num_customer_mtf += 1
            print("Ready to serve process {} after delay for {} minutes".format(self.process_list[0].id, round(waiting_time,2)))
            self.total_waiting_time+=waiting_time
            #Menghitung proses yang ada di paling depan
            self.departure_time=self.clock+self.actual_service_time
        #Kalau gaada proses lain, departure time dinyatakan infinity karena tidak ada proses yang perlu dijalankan
        else :
            self.departure_time=float('inf')
            print("CPU is idle")

    def advance_time_sjf(self):
        event = min(self.arrival_time,self.departure_time)
        print("---------------------------------------------------------------------")
        print("Last Arrival Time : {}".format(round(self.arrival_time, 2)))
        print("Last Departure Time : {}".format(round(self.departure_time, 2)))
        print("---------------------------------------------------------------------")
        self.clock = event
        if self.arrival_time < self.departure_time:
            self.handle_arrival()
        else:
            self.handle_departure_sjf()


    def handle_departure_sjf(self):
        #Proses meninggalkan CPU
        self.process_list.pop(0)
        self.num_in_system-=1
        print("Process has leaved at time {}".format(round(self.clock,2)))
        #Menambah jumlah proses yang keluar
        self.num_processed+=1
        #Kalau masih ada proses lain di dalam sistem
        if self.num_in_system>0 :
            print("There are still {} process(es) in the system.".format(self.num_in_system))
            #Mengurutkan mulai dari yang service time maximum terkecil untuk diproses selanjutnya
            self.process_list.sort(key=maximum_time)
            '''
            for i in range(len(self.process_list)):
                print(self.process_list[i].maximum_service_time)'''
            #Menghitung delay time untuk proeses yang akan dilayani selanjutnya
            waiting_time = self.clock-self.process_list[0].arrival_time
            self.maximum_waiting_time = max(waiting_time, self.maximum_waiting_time)
            if waiting_time >= 5 : 
                self.num_customer_mtf += 1
            print("Ready to serve process {} after delay for {} minutes".format(self.process_list[0].id, round(waiting_time,2)))
            self.total_waiting_time+=waiting_time
            #Menghitung proses yang ada di paling depan
            self.departure_time=self.clock+self.actual_service_time
        #Kalau gaada proses lain, departure time dinyatakan infinity karena tidak ada proses yang perlu dijalankan
        else :
            self.departure_time=float('inf')
            print("CPU is idle")

        

s1 = Simulation(1, 1.1, [0.55, 1.05])
s2 = s1
while s1.num_processed <= 1000 : 
    s1.advance_time_fifo()

print("FIFO")
print("Percentage of delay more than 5 minutes :  {}".format(s1.num_customer_mtf))
print("Average waiting time : {}".format(round(s1.total_waiting_time/s1.num_processed, 2)))
print("Maximum delay : {}".format(round(s1.maximum_waiting_time,2)))

while s2.num_processed <= 1000 :
    s2.advance_time_sjf()

print("SJF")
print("Percentage of delay more than 5 minutes :  {}".format(s2.num_customer_mtf))
print("Average waiting time : {}".format(round(s2.total_waiting_time/s2.num_processed, 2)))
print("Maximum delay : {}".format(round(s2.maximum_waiting_time,2)))