def frange(start, stop, step):
    while start >= stop:
        yield round(start, 3)  # Üç basamağa yuvarladık
        start += step

start = 0.28
end = 0.15
step = -0.005  # Belirtilen adımla azalacak

numbers = list(frange(start, end, step))

for number in numbers:
    print(str(number).replace('.', ','))

