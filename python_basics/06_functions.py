# A function gives a useful piece of work a name.
def greet(name):
    print("Hello,", name)


def double(number):
    answer = number * 2
    return answer


greet("Ada")
greet("Grace")

score = 7
new_score = double(score)
print("Original score:", score)
print("Doubled score:", new_score)

# Try writing a function named triple(number) that returns number * 3.
