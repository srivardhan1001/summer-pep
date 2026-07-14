""" x = [4,2,3,8,6,5]
def is_even(num):
    if num %2 == 0:
        return True
    else:
        return False
out = list(filter(is_even,x))
print(out)"""
"""l = [2,8,9,3]
il=iter(l)
print(il)
print(type(il))
next
print(next(il))
print("Hi")
print(next(il))
print("Bye")"""
def gen_alphabets(start, end, step=1):
    print(f"step is",(step))
    start_ascii = ord(start)
    end_ascii = ord(end)
    while start_ascii <= end_ascii:
        yield chr(start_ascii)
        start_ascii += step