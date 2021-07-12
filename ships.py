import random
import numpy as np
import time
import copy

class Ship: 
    def __init__(self, id, arrival_time, service_time):
        self.id = id
        self.arrival_time = arrival_time
        self.departure_time = 0
        self.served_time = arrival_time
        self.service_time = service_time

    def set_departure_time(self, departure_time):
        self.departure_time=departure_time

    def set_served_time(self, served_time):
        self.served_time=served_time

    def get_remaining_time(self, clock):
        return self.departure_time-clock
    
    def decrease_departure_time(self, clock):
        self.departure_time=clock+0.5*(self.get_remaining_time(clock))
        print("Departure time is decreased. Now the departure time is {}.".format(round(self.departure_time,2)))


    def increase_departure_time(self, clock):
        self.departure_time = clock+2*(self.get_remaining_time(clock))
        print("Departure time is increased. Now the departure time is {}.".format(round(self.departure_time,2)))



def maximum_time(obj):
    return obj.maximum_service_time


class Simulation:
    def __init__(self, iat, bounds):
        #Clock
        self.clock = 0.0
        #Objek kapal
        self.obj = None
        #Waktu Kedatangan
        self.arrival_time = self.generate_interarrival(iat)
        #Waktu Keberangkatan
        self.departure_time = [float('inf'), float('inf')]
        #Actual Time
        self.service_time = random.uniform(bounds[0], bounds[1])
        #ID Proses
        self.ship_id = 1
        #Jumlah proses di sistem (indeks ke 0 selalu merupakan yang dilayani)
        self.queue = []
        #Check process in system
        self.process_in_system = [False, False]
        #Check processes identity in system
        self.unloading = [None, None]
        #Jumlah kedatangan
        self.num_arrival = 0
        #Jumlah keberangkatan
        self.num_departure = 0
        #Total Waiting Time
        self.total_waiting_time = 0.0
        #Inter Arrival Time
        self.mean_iat = iat
        #Status bergabung
        self.status = False
        #Waiting time
        self.maximum_waiting_time = 0
        #Berth Total Utility time
        self.berth_total_utility_time = [0,0]
        #Crane Idle Time
        self.crane_utility_time = [0,0]
        self.crane_total_utility_time = [0,0]
        #Total time in harbour
        self.total_time_in_harbour = [float('inf'),0,0]


    def generate_interarrival(self,iat):
        return np.random.exponential(1./iat)

    #Kalau dijalankan secara FIFO
    def advance_time(self):
        event = min(self.arrival_time,self.departure_time[0], self.departure_time[1])
        print("---------------------------------------------------------------------")
        print("Last Arrival Time : {}".format(round(self.arrival_time, 2)))
        print("Last Departure Time in Berth 1 : {}".format(round(self.departure_time[0], 2)))
        print("Last Departure Time in Berth 2 : {}".format(round(self.departure_time[1], 2)))
        print("---------------------------------------------------------------------")
        self.clock = event
        if event == self.arrival_time :
            self.handle_arrival()
        elif event==self.departure_time[0]:
            self.handle_departure_one()
        elif event==self.departure_time[1]:
            self.handle_departure_two()
    
    def add_departure_time(self, server):
        self.unloading[server].increase_departure_time(self.clock)
        self.departure_time[server] = self.unloading[server].departure_time

    def sub_departure_time(self, server):
        self.unloading[server].decrease_departure_time(self.clock)
        self.departure_time[server] = self.unloading[server].departure_time
        

    def push_served(self, server, obj, alpha):
        #Mengeluarkan dari daftar antrian
        self.unloading[server]=obj
        self.unloading[server].service_time = alpha*self.unloading[server].service_time
        self.process_in_system[server]=True
        departure_time = self.clock+alpha*self.unloading[server].service_time
        self.unloading[server].set_departure_time(departure_time)
        self.departure_time[server]=departure_time
        

    def handle_arrival(self):
        #Menambah customer ke kedatangan di server A
        self.num_arrival +=1
        #Memasukkan proses ke dalam queue
        self.ship_id = hex(random.getrandbits(8))
        self.obj = Ship(self.ship_id, self.arrival_time, self.service_time)
        #Kalau masih ngantri
        if self.process_in_system[0] and self.process_in_system[1]:
            print("Queue is busy, please wait")
            self.queue.append(self.obj)
        #Kalau salah satu server yang keisi
        elif self.process_in_system[0] ^ self.process_in_system[1]:
            #Kalau di 0 yang kosong
            if self.process_in_system[0]==False : 
                print("Queue is empty, serving process {} in server {}".format(self.ship_id, 1))
                self.push_served(0,self.obj, 1)
                self.add_departure_time(1)
            #Kalau di 1 yang kosong
            elif self.process_in_system[1]==False :
                print("Queue is empty, serving process {} in server {}".format(self.ship_id, 2))
                self.push_served(1, self.obj, 1)
                self.add_departure_time(0)
        #Kalau masih kosong (idle)
        elif not (self.process_in_system[0] or self.process_in_system[1]) :
            print("Queue is empty, serving process {}".format(self.ship_id))
            self.crane_utility_time[0]=self.crane_utility_time[1]=self.clock
            self.push_served(0,self.obj, 0.5)
        self.arrival_time = self.clock+self.generate_interarrival(self.mean_iat)


    #Mengatur kedatangan dari server 1
    def handle_departure_one(self):
        #Kapal meninggalkan pelabuhan
        print("Ship has leaved at time {}".format(round(self.clock,2)))
        time_in_harbour = self.unloading[0].departure_time-self.unloading[0].arrival_time
        self.total_time_in_harbour[0] = min(self.total_time_in_harbour[0], time_in_harbour)
        self.total_time_in_harbour[1] = max(self.total_time_in_harbour[1], time_in_harbour)
        self.total_time_in_harbour[2] += time_in_harbour
        self.berth_total_utility_time[0] += (self.unloading[0].departure_time-self.unloading[0].served_time)
        #print(round(self.clock,2), round(self.unloading[0].departure_time,2))
        self.unloading[0]=None
        self.process_in_system[0]=False
        
        #Menambah jumlah proses yang keluar
        self.num_departure+=1
        #Kalau masih ada proses lain di dalam sistem
        if len(self.queue)>0 :
            print("There are still {} ship(s) in the system.".format(len(self.queue)))
            #Menghitung delay time untuk proeses yang akan dilayani selanjutnya
            waiting_time = self.clock-self.queue[0].arrival_time
            print("Ready to unload ship {} after delay for {} minutes".format(self.queue[0].id, round(waiting_time,2)))
            self.queue[0].set_served_time(self.clock)
            self.total_waiting_time+=waiting_time
            #Kalau misalnya yang 1 juga kosong
            if self.process_in_system[1]==False:
                self.push_served(0,self.queue[0], 0.5)
                self.crane_utility_time[0]=self.crane_utility_time[1]=self.clock
            #Kalau misalnya yang 1 masih isi
            else :
                self.push_served(0, self.queue[0], 1)
                self.add_departure_time(0)
            self.queue.pop(0)    
        #Kalau gaada proses lain, departure time dinyatakan infinity karena tidak ada proses yang perlu dijalankan
        else :
            #Kalau masih ada proses yang dijalankan di server sebelah
            if self.process_in_system[1]==True:
                self.sub_departure_time(1)
                print("---------------------------------------------------------------------")
            else : 
                self.crane_total_utility_time[0] = self.clock-self.crane_utility_time[0]
                self.crane_total_utility_time[1]=self.clock-self.crane_utility_time[1]
            self.departure_time[0]=float('inf')
            print("Berth 1 is idle")

    def handle_departure_two(self):
        #Kapal meninggalkan pelabuhan
        print("Ship has leaved at time {}".format(round(self.clock,2)))
        time_in_harbour = self.unloading[1].departure_time-self.unloading[1].arrival_time
        self.total_time_in_harbour[0] = min(self.total_time_in_harbour[0], time_in_harbour)
        self.total_time_in_harbour[1] = max(self.total_time_in_harbour[1], time_in_harbour)
        self.total_time_in_harbour[2] += time_in_harbour
        self.berth_total_utility_time[1] += (self.unloading[1].departure_time-self.unloading[1].served_time)
        self.unloading[1]=None
        self.process_in_system[1]=False
        
        #Menambah jumlah proses yang keluar
        self.num_departure+=1
        #Kalau masih ada proses lain di dalam sistem
        if len(self.queue)>0 :
            print("There are still {} process(es) in the system.".format(len(self.queue)))
            #Menghitung delay time untuk proeses yang akan dilayani selanjutnya
            waiting_time = self.clock-self.queue[0].arrival_time
            print("Ready to unload ship {} after delay for {} days".format(self.queue[0].id, round(waiting_time,2)))
            self.queue[0].set_served_time(self.clock)
            self.total_waiting_time+=waiting_time
            #Kalau berth 1 kosong
            if self.process_in_system[0]==False :
                self.push_served(0,self.queue[0], 0.5)
                self.crane_utility_time[0]=self.crane_utility_time[1]=self.clock
            #Kalau semisal di berth 1 ada isinya
            else : 
                self.push_served(1, self.queue[0], 1)
                self.add_departure_time(0)
            self.queue.pop(0)    
        #Kalau gaada proses lain, departure time dinyatakan infinity karena tidak ada proses yang perlu dijalankan
        else :
            #Kalau masih ada proses yang dijalankan di server sebelah
            if self.process_in_system[0]==True:
                self.sub_departure_time(0)
            else :
                self.crane_total_utility_time[0] += self.clock-self.crane_utility_time[0]
                self.crane_total_utility_time[1] += self.clock-self.crane_utility_time[1]
            self.departure_time[1]=float('inf')
            #Mencatat idle time pada server
            print("Berth 2 is idle")

    def stop(self) :
        for i in range(len(self.berth_total_utility_time)):
            if self.process_in_system[i]==True:
                self.berth_total_utility_time[i]+=self.clock-self.unloading[i].served_time
        for i in range(len(self.crane_total_utility_time)):
            if self.process_in_system[i]==True:
                self.crane_total_utility_time[i] += self.clock-self.crane_utility_time[i]
            
        self.total_time_in_harbour[2] = self.total_time_in_harbour[2]/self.num_departure


        

s = Simulation(1.25, [0.5, 1.5])
while s.clock < 90 : 
    s.advance_time()
s.stop()
for i in range(2):
    print("Total utility time in Berth {}: {} day".format(i+1, round(s.berth_total_utility_time[i],2)))

for i in range(2):
    print("Total utility time in Crane {} : {} day".format(i+1, round(s.crane_total_utility_time[i],2)))

print("Minimum time in harbour is {} day".format(round(s.total_time_in_harbour[0],2)))
print("Maximum time in harbour is {} day".format(round(s.total_time_in_harbour[1],2)))
print("Average time in harbour is {} day".format(round(s.total_time_in_harbour[2],2)))

