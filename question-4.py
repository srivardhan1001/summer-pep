#4
cel = [20, 30, 40, 50, 60]

fahrenheit = list(map(lambda c: (c * 9/5) + 32, cel))

high_temp = list(filter(lambda f: f > 100, fahrenheit))

print("Fahrenheit Temperatures:")
print(fahrenheit)

print("Temperatures above 100°F:")
print(high_temp)
