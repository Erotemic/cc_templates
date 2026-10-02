# Python runs these instructions from top to bottom.

print("You wake up in a dark room.")

name = input("What is your name? ")
print("Hello,", name)

print("There is a red door and a blue door.")
door = input("Which door do you open? ")

if door == "red":
    print("You find a sleeping dragon.")
else:
    print("You find a room full of treasure.")

print("The end.")
