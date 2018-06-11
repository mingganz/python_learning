class Clock(object):
    def __init__(self, hours = 0, minutes = 0, seconds = 0):
        self.__hours = hours
        self.__minutes = minutes
        self.__seconds = seconds

    def set(self, hours, minutes, seconds):
        self.__hours = hours
        self.__minutes = minutes
        self.__seconds = seconds

    def tick(self): # Advance one second
        if self.__seconds == 59:
            self.__seconds = 0
            if self.__minutes == 59:
                self.__minutes = 0
                self.__hours = 0 if self.__hours == 23 else self.__hours + 1
            else:
                self.__minutes += 1
        else:
            self.__seconds += 1


    def display(self):
        print('{}:{}:{}'.format(self.__hours, self.__minutes, self.__seconds))

    def __str__(self):
        return ('{}:{}:{}'.format(self.__hours, self.__minutes, self.__seconds))

class Calender(object):
    months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__(self, day = 1, month = 1, year = 1900):
        self.__day = day
        self.__month = month
        self.__year = year

    def leapyear(self, y):
        if y % 4:
            return False
        else:
            if y % 100:
                return True
            else:
                if y % 400:
                    return False
                else:
                    return True

    def set(self, day, month, year):
        self.__day = day
        self.__month = month
        self.__year = year

    def advance(self):
        # Adjust max days on February
        Calender.months[1] += self.leapyear(self.__year)
        if self.__day == Calender.months[self.__month - 1]:
            if self.__month == 12:
                self.__year += 1
            else:
                self.__month += 1
        else:
            self.__day += 1

    def __str__(self):
        return ('{}/{}/{}'.format(self.__day, self.__month, self.__year))


class Time(Clock, Calender):
    def __init__(self, day, month, year, hours = 0, minutes = 0, seconds = 0):
        Clock.__init__(self, hours, minutes, seconds)
        Calender.__init__(self, day, month, year)

    def __str__(self):
        return (Clock.__str__(self) + '  ' + Calender.__str__(self))


def main():
    x = Time(24, 12, 2000)
    i = 0
    while i < 3600:
        x.tick()
        x.advance()
        print(x)
        i += 1
    else:
        print('Loop is over...')

if __name__ == '__main__':
    main()