def frange(start, stop, step):
    while start >= stop:
        yield round(start, 3)  # Üç basamağa yuvarladık
        start += step

start = 3.10
end = 2.20
step = -0.02  # Belirtilen adımla azalacak

numbers = list(frange(start, end, step))

for number in numbers:
    print(str(number).replace('.', ','))

