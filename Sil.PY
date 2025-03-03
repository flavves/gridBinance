def frange(start, stop, step):
    while start >= stop:
        yield round(start, 3)  # Üç basamağa yuvarladık
        start += step

start = 2.60
end = 2.40
step = -0.01  # Belirtilen adımla azalacak

numbers = list(frange(start, end, step))

for number in numbers:
    print(str(number).replace('.', ','))

