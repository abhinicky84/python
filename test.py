from datetime import datetime, timedelta

def greet(name):
    print(f"Hello, {name}!")

def add_numbers(a, b):
    return a + b

fn = "abhishek"
ln = "singhal"
na = "asdss"
days = 28
d1 = '5'
d2 = '3'

#name = input("Enter your name: ")
#greet(name.capitalize())
result = add_numbers(5, 3)
print(f"The sum is: {result}")
mystr = "The sum is: {0} {2}".format(fn, ln, na)

print(float(d1) + float(d2))

current_time = datetime.now()
one_day = timedelta(days=1)
print("current date " + str(current_time))
print(current_time - one_day)
#bday = input("Enter your birthdate in format dd/mm/yyyy: ")
#bdate = datetime.strptime(bday, "%d/%m/%Y")
#   print(f"Your birthdate is: {bdate}")