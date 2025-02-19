start = 0.6
end = 0.1
step = -0.01

def frange(start, stop, step):
    while start >= stop:
        yield start
        start += step

numbers = [round(x, 2) for x in frange(start, end, step)]

for number in numbers:
    print(number)