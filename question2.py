arr = list(map(int,input("enter array:").split()))
n = int(input("no of operations: "))
for _ in range(n):
    left,right = map(int,input("enter left and right: ").split())
    arr[left:right+1] = arr[left:right+1][::-1]
    print(arr) 