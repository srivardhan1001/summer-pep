def create_paginator(items,pageSize):
    for i in range(0,len(items),pageSize):
        yield items[i:i + pageSize]
items = list(map(int, input("Enter items: ").split()))
pageSize = int(input("Enter page size: "))
for page in create_paginator(items,pageSize):
    print(page)