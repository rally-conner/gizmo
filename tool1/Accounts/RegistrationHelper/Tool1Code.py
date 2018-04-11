import math

def getPhoneNumber(num, n):
    return num // 10 ** (int(math.log(num, 10)) - n + 1)

number = 4151234567
print(getPhoneNumber(number, 3))
