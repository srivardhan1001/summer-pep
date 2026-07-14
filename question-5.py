#5
def fibonacci(n):
    a = 0
    b = 1

    for i in range(n):
        yield a
        a, b = b, a + b

gen = fibonacci(10)

print("Using next():")
print(next(gen))
print(next(gen))
print(next(gen))
print(next(gen))

print("Using for loop:")
for num in gen:
    print(num)