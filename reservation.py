#Yanin Niramai
#260983558
import doctest, datetime, random, room
from room import Room, MONTHS, DAYS_PER_MONTH

class Reservation:
    booking_numbers = []
    def __init__(self, name, room_reserved, check_in, check_out, booking_number = None):
        #raise error if room isn't available
        if room_reserved.is_available(check_in, check_out) == False:
            raise AssertionError("This room isn't available at the specified dates")
        self.name = name
        self.room_reserved = room_reserved
        self.check_in = check_in
        self.check_out = check_out
        #check if the booking number is valid if provided
        if booking_number != None:
            if booking_number in Reservation.booking_numbers:
                raise AssertionError("Please enter a valid room number")
            if len(str(booking_number)) != 13 or str(booking_number)[:1] == 0:
                raise AssertionError("Please enter a valid room number")
        #If the booking number not provided, generate a new random 13 digit number
        else:
            range_start = 10**(13-1)
            range_end = (10**13)-1
            ran_num = random.randint(range_start, range_end)
            if str(ran_num)[:1] != 0 and ran_num not in Reservation.booking_numbers:
                booking_number = ran_num
        self.booking_number = int(booking_number)
        #update the booking_numbers list
        Reservation.booking_numbers.append(int(booking_number))
        #reserve the room for all nights including check-in night and excluding check_out night
        delta = datetime.timedelta(days=1)
        check_in1 = check_in
        while check_in1 <= check_out:
            room_reserved.reserve_room(check_in1)
            check_in1 += delta
        #exclude the check_out night
        availability_list = room_reserved.availability.get((check_out.year, check_out.month))
        #replace False with True
        availability_list[check_out.day] = True
        
    def __str__(self):
        #returns a str containing the booking number, name, room reserved and check-in&out dates
        booking_num = "Booking number: " + str(self.booking_number)
        name = "Name: " + self.name
        room1 = "Room reserved: " + self.room_reserved.__str__()
        checkin = "Check-in date: " + str(self.check_in)
        checkout = "Check-out date: " + str(self.check_out)
        return booking_num + "\n" + name + "\n" + room1 + "\n" + checkin + "\n" + checkout
    def to_short_string(self):
        #returns a str containing the booking number and name separated by two hyphens
        return str(self.booking_number)+'--'+self.name
    @classmethod
    def from_short_string(cls, short_str, check_in, check_out, room_reserved):
        #creates and returns an object of type Reservation for a stay in the specified room
        return Reservation(short_str[15:],room_reserved, check_in, check_out, short_str[0:13])
    @staticmethod
    def get_reservations_from_row(room_reserved, tup_list):
        #dict in which key is a booking number and each value is the reservation object for that booking number
        reserve_dict = {}
        #all unique booking_number
        unique_num = []
        #all days in booking_number
        days = []
        short_str = ''
        #iterate through each tup
        for tup in tup_list:
            #if fourth element is an empty str, there was no reservation on that day for the given room
            if tup[3] == '':
                continue
            #find the booking_number
            booking_number = (tup[3])[0:13]
            #add all days to days and unique booking number to unique_num
            if booking_number not in unique_num:
                day = (tup[0], room.MONTHS.index(tup[1])+1, tup[2])
                days.append(day)
                unique_num.append(booking_number)
                #unique short string
                short_str += tup[3]
            else:
                day = (tup[0], room.MONTHS.index(tup[1])+1, tup[2])
                days.append(day)
        #find the checkin and checkout date
        date1 = datetime.date(min(days)[0],min(days)[1],min(days)[2])
        date2 = datetime.date(max(days)[0],max(days)[1],max(days)[2]+1)
        #turn all info into Reservation objects
        info = Reservation.from_short_string(short_str, date1, date2, room_reserved)
        #iterate through all booking numbers in Reservation.booking_numbers
        for num in Reservation.booking_numbers:
            #set num as key and turn all info into a str using __str__
            reserve_dict[int(num)] = info.__str__()
        return reserve_dict

