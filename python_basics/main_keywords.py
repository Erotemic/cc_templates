# This is a comment

# These are Python imports
import datetime as datetime_mod
import time


# This is a variable
flag = True


# This is a loop.
while flag:

    # The "try:" keyword means we might run code that causes an error
    try:

        # This is a "function call"
        now_time = datetime_mod.datetime.now()

        # This is "attribute lookup"
        current_minute = now_time.minute

        # This an "if-else statement"
        if current_minute < 5:
            # Anything in quotes is a "string"
            print('We are at the start of the hour')
        if current_minute < 10:
            print('It hasnt been too long')
        if current_minute < 30:
            print('Still a lot of time left')
        elif current_minute < 50:
            print('Wow, the time flys')
        else:
            print('We are nearing the end, imma stop')
            flag = False

        print('The time is ' + str(now_time))
        print('')
        print('Sleeping for 2 seconds')
        print('')
        time.sleep(2)

    except KeyboardInterrupt:
        # The "try" keyword is always followed by an "except" that says
        # what to do if there is an error.
        # The triple quotes is a multi-line string
        print('''
              We caught a Python Exception. The program will now use the
              special "break" keyword to break out of the loop.
              ''')

        # There is a builtin Python module that tells you what all the keywords
        # are.
        import keyword
        keyword_list = keyword.kwlist
        print('Python has ' + str(len(keyword_list)) + ' keywords')
        # Note:
        # The first keywords you should learn are:
        # 1. Constants: 'False', 'None', 'True',
        # 2. Logic: 'not', 'or', 'and',
        # 3. Conditional: 'if', 'elif', 'else',
        # 4. Loops: 'while', 'for', 'break', 'continue', 'pass',
        # 5. Comparison: 'in', 'is',
        # 7. Functions and Classes: 'def', 'class' 'return',
        # 6. Imports: 'import', 'from', 'as',
        # 8. Errors: 'raise', 'try', 'except',
        print('The keywords are: ' + str(keyword_list))

        # The "break" keyword will break us out of the loop.
        break


# This is a function definition
def goodbye_message():
    print('The program will end, but first some MATH!')
    numbers = [1, 2, 3, 4, 5]
    squared_numbers = []
    for number in numbers:
        squared_numbers.append(number * number)
    print(f"Squared numbers: {squared_numbers}")

    # Demonstrating the use of 'is' and 'in'
    print("Is flag True? ", flag is True)
    print("Is 5 in squared numbers? ", 5 in squared_numbers)
    print('That was, butn, but the program actually ends now')

# Function call
goodbye_message()
