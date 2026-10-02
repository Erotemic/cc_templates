# A list keeps several values together in order.
backpack = ["rope", "apple", "key"]

print("Backpack:", backpack)
print("First item:", backpack[0])

# append adds one value to the end of a list.
backpack.append("flashlight")

print("After finding a flashlight:")
for item in backpack:
    print("-", item)

print("Number of items:", len(backpack))

# Try changing the starting list or appending a different item.
