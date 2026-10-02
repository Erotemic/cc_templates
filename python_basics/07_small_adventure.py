def show_inventory(items):
    print("You are carrying:")
    for item in items:
        print("-", item)


print("THE OLD TOWER")
print("")

name = input("Adventurer, what is your name? ")
print("Welcome,", name)

inventory = []

print("")
print("A forest path splits toward a cave and a pond.")
path = input("Do you visit the cave or the pond? ")

if path == "cave":
    print("Inside the cave you find an old iron key.")
    inventory.append("key")
elif path == "pond":
    print("At the pond you find a smooth blue stone.")
    inventory.append("blue stone")
else:
    print("You wander for a while and find nothing.")

print("")
show_inventory(inventory)

print("")
print("At sunset you reach an old tower with a locked door.")

if "key" in inventory:
    print("Your key fits the lock. The tower door opens!")
else:
    print("The door is locked. You will need to return another day.")

print("The end.")
