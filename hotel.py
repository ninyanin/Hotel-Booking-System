#Yanin Niramai
#260983558
import doctest, datetime, random, copy, os, room, reservation
from room import Room, MONTHS, DAYS_PER_MONTH
from reservation import Reservation

class Hotel:
    def __init__(self, name, rooms = [], reservations = {}):
        self.name = name
        self.rooms = copy.deepcopy(rooms)
        self.reservations = copy.deepcopy(reservations)
        
    def make_reservation(self, name, room_type, check_in, check_out):
        #raise error if no room is available
        if Room.find_available_room(self.rooms, room_type, check_in, check_out) == None:
            raise AssertionError("no room of the given type is available for the dates indicated")
        #find the available room
        room_reserved = Room.find_available_room(self.rooms, room_type, check_in, check_out)
        #turn all inputs to reservation objects
        rsv_obj = Reservation(name, room_reserved, check_in, check_out)
        #ubdate the reservations dict
        self.reservations[rsv_obj.booking_number] = rsv_obj.__str__()
        return rsv_obj.booking_number
    
    def get_receipt(self, booking_numbers):
        #a list contain all price
        all_price = []
        for booking_number in booking_numbers:
            #if booking_number isn't for this hotel, return 0.0
            if booking_number not in self.reservations:
                return 0.0
            booking_info = self.reservations.get(booking_number)
            index1 = booking_info.find('Room reserved: ')
            index2 = booking_info.find('Check-in date: ')
            index3 = booking_info.find('Check-out date: ')
            #find checkin and checkout date
            check_in = booking_info[index2+15:index3-1]
            check_out = booking_info[index3+16:]
            #turn into datetime object
            out_date = (datetime.date(int(check_out[:4]), int(check_out[5:7]),int(check_out[8:])))
            in_date = (datetime.date(int(check_in[:4]), int(check_in[5:7]),int(check_in[8:])))
            #find room info
            room_info = booking_info[index1+15: index2-1]
            #append all price
            all_price.append(float((room_info.split(',')[2]))*(out_date-in_date).days)
        return sum(all_price)
    
    def get_reservation_for_booking_number(self, booking_number):
        #returns None if such a reservation cannot be found.
        if booking_number not in self.reservations:
            return None
        #returns the reservation object with the given number
        return self.reservations.get(booking_number)
    
    def cancel_reservation(self, booking_number):
        #If the booking number doesn't refer to a reservation at the hotel, the method does do nothing
        if booking_number not in self.reservations:
            pass
        booking_info = self.reservations.get(booking_number)
        index1 = booking_info.find('Room reserved: ')
        index2 = booking_info.find('Check-in date: ')
        index3 = booking_info.find('Check-out date: ')
        check_in = booking_info[index2+15:index3-1]
        check_out = booking_info[index3+16:]
        out_date = (datetime.date(int(check_out[:4]), int(check_out[5:7]),int(check_out[8:])))
        in_date = (datetime.date(int(check_in[:4]), int(check_in[5:7]),int(check_in[8:])))
        #iterate through all room in rooms list
        for room in self.rooms:
            #if room info = room reserved by this booking number, cancel reservation
            if room.__str__() == booking_info[index1+15: index2-1]:
                delta = datetime.timedelta(days=1)
                while in_date <= out_date:
                    room.make_available(in_date)
                    in_date += delta
        #remove this booking number from reservations dict
        self.reservations.pop(booking_number)
        
    def get_available_room_types(self):
        available_type = []
        for r in self.rooms:
            #find room_type using Room 
            if r.room_type not in available_type:
                available_type.append(r.room_type)
        return available_type
    
    @staticmethod
    def load_hotel_info_file(filename):
        room_list =[]
        #open the file in read mode
        fobj = open(filename, 'r')
        #the first line is the hotel name
        for line in fobj:
            hotel_name = line[:-1]
            break
        #append all room info
        for line in fobj:
            room_list.append(line[:-1])
        return (hotel_name, room_list)
        fobj.close()
    
    def save_hotel_info_file(self):
        '''
        >>> r1 = Room("Double", 101, 99.99)
        >>> r1.set_up_room_availability(['Oct', 'Nov', 'Dec'], 2021)
        >>> h = Hotel("Queen Elizabeth Hotel", [r1], {})
        >>> h.save_hotel_info_file()
        >>> fobj = open('hotels/queen_elizabeth_hotel/hotel_info.txt', 'r')
        >>> fobj.read()
        'Queen Elizabeth Hotel\\nRoom 101,Double,99.99\\n'
        >>> fobj.close()
        '''
        name = self.name.replace(' ', '_')
        fobj = open('hotels/'+name.lower()+"/"+'hotel_info.txt', 'w')
        fobj.write(self.name)
        #write info of each room in Room._str__ formate
        for r in self.rooms:
            fobj.write('\n'+r.__str__()+'\n')

        fobj.close()
    
    @staticmethod
    def load_reservation_strings_for_month(folder, month, year):
        rsv_dict = {}
        #a list of tuples
        list_info = []
        #open csv file of the given month/year
        date_file = open('hotels/'+folder+"/"+str(year)+'_'+month+'.csv', 'r')
        #iterate through each line in file
        for line in date_file:
            #turn into a list
            line = line.split(',')
            if '\n' in line:
                line.remove('\n')
            #days of the month
            days = room.DAYS_PER_MONTH[room.MONTHS.index(month)]
            #iterate through j in range(days)
            for j in range(days):
                if j == days-1:
                    element = line[1:][j-1]
                else:
                    element = line[1:][j]
                #append tuple of each day
                list_info.append((year, month, j+1, element))
            #save room_number as key and a list of tuples as value
            rsv_dict[int(line[0])] = list_info
            list_info = []
        date_file.close()
        return rsv_dict
    
    def save_reservations_for_month(self, month, year):
        '''
        >>> random.seed(987)
        >>> r1 = Room("Double", 237, 99.99)
        >>> r1.set_up_room_availability(['Oct', 'Nov', 'Dec'], 2021)
        >>> Reservation.booking_numbers = []
        >>> h = Hotel("Queen Elizabeth Hotel", [r1], {})
        >>> date1 = datetime.date(2021, 10, 30)
        >>> date2 = datetime.date(2021, 12, 23)
        >>> num = h.make_reservation("Jack", "Double", date1, date2)
        >>> h.save_reservations_for_month('Oct', 2021)
        >>> fobj = open('hotels/queen_elizabeth_hotel/2021_Oct.csv', 'r')
        >>> fobj.read()
        '237,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,1953400675629--Jack,1953400675629--Jack\\n'
        >>> fobj.close()

        '''
        folder = self.name.replace(' ', '_')
        date_file = open('hotels/'+folder.lower()+"/"+str(year)+'_'+month+'.csv', 'w')
        #list to store reservations
        str_list = ''
        for key in self.reservations:
            #find Name, booking number, checkin, checkout date, room number
            booking_info = self.reservations.get(key)
            index1 = booking_info.find('Room reserved: ')
            index2 = booking_info.find('Check-in date: ')
            index3 = booking_info.find('Check-out date: ')
            index4 = booking_info[index1+20: index2].find(',')
            index5 = booking_info.find(':')
            index6 = booking_info.find('Name')
            name = booking_info[index6+6:index1-1]
            booking_num = booking_info[index5+2:index5+15]
            room_num = booking_info[index1+20: index2][:3]
            check_in = booking_info[index2+15:index3-1]
            check_out = booking_info[index3+16:]
            out_date = (datetime.date(int(check_out[:4]), int(check_out[5:7]),int(check_out[8:])))
            in_date = (datetime.date(int(check_in[:4]), int(check_in[5:7]),int(check_in[8:])))
            #add room number to the str
            str_list += room_num
            days = room.DAYS_PER_MONTH[room.MONTHS.index(month)]
            #days reserved
            days_booked = days - in_date.day +1
            days_left = days - out_date.day +1
            dif_yr = out_date.year-in_date.year
            if in_date.year == year and out_date.year == year:
                if in_date.month == room.MONTHS.index(month)+1 and out_date.month == room.MONTHS.index(month)+1:
                    for i in range(days-days_booked+1):
                        str_list += ','
                    #add reservation str
                    for i in range(out_date.day-in_date.day+1):
                        str_list += booking_num+'--'+name
                        str_list += ','
                    for i in range(days_booked-days_left):
                        str_list += ','
                    
                else:
                    if in_date.month == room.MONTHS.index(month)+1:
                        for i in range(days-days_booked+1):
                            str_list += ','
                        #add reservation str
                        for i in range(days_booked):
                            str_list += booking_num+'--'+name
                            str_list += ','
                    elif out_date.month > room.MONTHS.index(month)+1:
                        for i in range(days):
                            str_list += ','
                            str_list += booking_num+'--'+name
                    else:
                        for i in range(days - days_left+1):
                            str_list += ','
                            str_list += booking_num+'--'+name
                        for i in range(days_left):
                            str_list += ','
                        
            elif in_date.year < year and out_date.year > year:
                for i in range(days):
                    str_list += ','
                    str_list += booking_num+'--'+name
                    
            elif in_date.year == year and out_date.year > year:
                if in_date.month == room.MONTHS.index(month)+1:
                    for i in range(days-days_booked+1):
                        str_list += ','
                    #add reservation str
                    for i in range(days_booked):
                        str_list += booking_num+'--'+name
                        str_list += ','
                elif in_date.month < room.MONTHS.index(month)+1:
                    for i in range(days):
                        str_list += ','
                        str_list += booking_num+'--'+name
                        
            else:
                if out_date.month == room.MONTHS.index(month)+1:
                    for i in range(days - days_left+1):
                        str_list += ','
                        str_list += booking_num+'--'+name
                    for i in range(days_left):
                        str_list += ','
                else:
                    for i in range(days):
                        str_list += ','
                        str_list += booking_num+'--'+name
                    
            if str_list.count(',') != days:
                str_list = str_list[:-1]
            #write into the file
            date_file.write(str_list+'\n')
            str_list = ''
        date_file.close()
    
    def save_hotel(self):
        '''
        >>> random.seed(987)
        >>> Reservation.booking_numbers = []
        >>> r1 = Room("Double", 237, 99.99)
        >>> r1.set_up_room_availability(['Oct', 'Nov', 'Dec'], 2021)
        >>> h = Hotel("Queen Elizabeth Hotel", [r1], {})
        >>> date1 = datetime.date(2021, 10, 30)
        >>> date2 = datetime.date(2021, 12, 23)
        >>> h.make_reservation("Jack", "Double", date1, date2)
        1953400675629
        >>> h.save_hotel()
        >>> fobj = open('hotels/queen_elizabeth_hotel/hotel_info.txt', 'r')
        >>> fobj.read()
        'Queen Elizabeth Hotel\\nRoom 237,Double,99.99\\n'
        >>> fobj.close()
        '''
        if self.rooms == []:
            pass
        if os.path.exists(self.name) == False:
            os.makedirs(self.name)
        for key in self.reservations:
            #find Name, booking number, checkin, checkout date, room number
            booking_info = self.reservations.get(key)
            index1 = booking_info.find('Room reserved: ')
            index2 = booking_info.find('Check-in date: ')
            index3 = booking_info.find('Check-out date: ')
            index4 = booking_info[index1+20: index2].find(',')
            index5 = booking_info.find(':')
            index6 = booking_info.find('Name')
            name = booking_info[index6+6:index1-1]
            booking_num = booking_info[index5+2:index5+15]
            room_num = booking_info[index1+20: index2][:3]
            check_in = booking_info[index2+15:index3-1]
            check_out = booking_info[index3+16:]
            out_date = (datetime.date(int(check_out[:4]), int(check_out[5:7]),int(check_out[8:])))
            in_date = (datetime.date(int(check_in[:4]), int(check_in[5:7]),int(check_in[8:])))
            dif_yr = out_date.year-in_date.year
            #a list of all years
            yr_list = []
            for i in range(dif_yr+1):
                yr_list.append(in_date.year+i)
            if in_date.year == out_date.year:
                for i in range(in_date.month-1, out_date.month-1):
                    Hotel.save_reservations_for_month(self, room.MONTHS[i], in_date.year)
            else:
                #iterate through checkin month to the end of the year
                for i in range(in_date.month-1, 11):
                    Hotel.save_reservations_for_month(self, room.MONTHS[i], in_date.year)
                for year in yr_list:
                    #iterate through the years in between
                    if year != in_date.year and year != out_date.year:
                        #iterate through all 12 months
                        for i in range(0, 11):
                            Hotel.save_reservations_for_month(self, room.MONTHS[i], year)
                for i in range(0, out_date.month-11):
                    Hotel.save_reservations_for_month(self, room.MONTHS[i], out_date.year)
            Hotel.save_hotel_info_file(self)
            
    @classmethod
    def load_hotel(cls, folder):
        file_list = os.listdir('hotels/'+folder)
        find_txt = file_list.index('hotel_info.txt')
        hotel_info = open('hotels/'+folder+"/"+file_list[find_txt], 'r')
        csv_file = []
        for file in file_list:
            if 'csv' in file:
                csv_file.append(file)
        reserved_day = []
        for file in csv_file:
            year = file[:4]
            month = file[5:8]
            #set up room availability
            for line in hotel_info:
                if 'Room' not in line:
                    continue
                room_num = line[line.find(' ')+1:line.find(',')]
                from_comma = line[line.find(',')+1:]
                index1 = from_comma.find(',')
                room_type = from_comma[:index1]
                price = from_comma[index1+1:-1]
                room_obj = Room(room_type, int(room_num), float(price))
                room_obj.set_up_room_availability([month], int(year))
            hotel_dict = Hotel.load_reservation_strings_for_month(folder, month, year)
            room_dict = {}
            for key in hotel_dict:
                tups = hotel_dict.get(key)
                for tup in tups:
                    if tup[3] != '':
                        index2 = tup[3].find('-')
                        name = tup[3][index2+2:]
                        r = key
                        date_reserved = datetime.date(int(tup[0]),room.MONTHS.index(tup[1])+1,tup[2])
                        reserved_day.append(date_reserved)
                        break
        room_dict[r] = reserved_day
        check_in = min(reserved_day)
        check_out = max(reserved_day)
        Reservation(name, r, check_in, check_out)
