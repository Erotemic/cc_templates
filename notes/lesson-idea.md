## Your Programming Toolbox

So, you need to make sense of the Python code you seen on screen.
Well, you need to learn what syntax you are looking at first.

This guide shows the main things Python lets you do.

#----

## Chapter 1: Literals & Variables — The smallest things Python can remember

* **Comments — Leave notes**

  * **Syntax patterns:** `# This is a comment`
  * **Usage:** Explain code in a way Python ignores.

* **Strings — Work with text**

  * **Syntax patterns:** `"hello"`, `'Python'`, `f"Hello, {name}"`
  * **Usage:** Create messages, labels, names, and other text.

* **Numbers — Work with numbers**

  * **Syntax patterns:** `10`, `3.14`, `-5`
  * **Usage:** Count, measure, calculate, and compare values.

* **Booleans — Work with true / false**

  * **Syntax patterns:** `True`, `False`
  * **Usage:** Represent yes/no answers.

* **Variables — Store information**

  * **Syntax patterns:** `name = "Ada"`, `age = 12`, `score = 98`
  * **Cares about:** strings, numbers, booleans
  * **Usage:** Save values so you can use them later.

#----

## Chapter 2: Operators — Doing math and asking questions

* **Arithmetic operators — Do math**

  * **Syntax patterns:** `+`, `-`, `*`, `/`, `//`, `%`, `**`
  * **Cares about:** numbers, variables
  * **Usage:** Add, subtract, multiply, divide, floor-divide, find remainders, and use powers.

* **Comparison operators — Compare values**

  * **Syntax patterns:** `==`, `!=`, `<`, `>`, `<=`, `>=`
  * **Cares about:** strings, numbers, variables
  * **Usage:** Check whether values are equal, different, bigger, or smaller. The answer is usually `True` or `False`.

#----

## Chapter 3: Expressions — Combining pieces into answers

Expressions are one of the most important ideas in Python. Once you know about values, variables, and operators, expressions are how you start putting those pieces together. Many later ideas depend on this: `if` statements need expressions, loops often use expressions, functions return expressions, and collections can contain expressions.

* **Expressions — Produce a value**

  * **Syntax patterns:** `age`, `age + 1`, `"Hi " + name`, `score >= 90`
  * **Cares about:** strings, numbers, booleans, variables, operators
  * **Usage:** Write code that Python can evaluate into an answer.

* **Expression composition — Build bigger expressions from smaller ones**

  * **Syntax patterns:** `(age + 1) * 2`, `score >= passing_score`, `"Hi " + name + "!"`
  * **Cares about:** expressions
  * **Usage:** Combine simple pieces of code into more useful answers.

#----

## Chapter 4: Conditionals & Indentation — Choosing what happens next

* **Conditionals — Make decisions**

  * **Syntax patterns:** `if`, `elif`, `else`
  * **Cares about:** booleans, expressions, comparison operators
  * **Usage:** Run different code depending on what is true.

* **Indentation — Organize code blocks**

  * **Syntax patterns:** indented lines after `if`, `for`, `while`, and `def`
  * **Cares about:** conditionals
  * **Usage:** Show which lines belong together.

#----

## Chapter 5: Collections — Keeping many things together

* **Lists — Group values in order**

  * **Syntax patterns:** `[1, 2, 3]`, `items[0]`, `items.append(value)`
  * **Cares about:** strings, numbers, booleans, variables, expressions
  * **Usage:** Store multiple values in order.

* **Dictionaries — Label values**

  * **Syntax patterns:** `{"name": "Ada"}`, `person["name"]`
  * **Cares about:** strings, numbers, booleans, variables, expressions
  * **Usage:** Store values by key so you can look them up by name.

#----

## Chapter 6: Loops & Control Flow — Repeating work with rules

* **Loops — Repeat actions**

  * **Syntax patterns:** `for item in items:`, `while condition:`
  * **Cares about:** variables, expressions, conditionals, indentation, lists, dictionaries
  * **Usage:** Run code again and again.

* **Loop control — Stop or skip in a loop**

  * **Syntax patterns:** `break`, `continue`
  * **Cares about:** loops, conditionals, indentation
  * **Usage:** Stop a loop early or skip to the next round.

#----

## Chapter 7: Functions, Imports & Errors — Building programs from reusable pieces

* **Functions — Group reusable code**

  * **Syntax patterns:** `def greet(name):`, `return value`, `greet("Ada")`
  * **Cares about:** variables, expressions, indentation
  * **Usage:** Make code you can run whenever you need it.

* **Imports — Bring in extra tools**

  * **Syntax patterns:** `import math`, `from random import randint`
  * **Cares about:** variables, functions
  * **Usage:** Use code that other people already wrote.

* **Errors — Understand problems**

  * **Syntax patterns:** `SyntaxError`, `NameError`, `TypeError`, `IndexError`
  * **Cares about:** everything above
  * **Usage:** Read error messages to find what went wrong.


------




## Appendix: Where Did These Names Come From?

Programming words can sound strange at first, but most of them came from ordinary ideas: math, language, lists, tools, and instructions.

* **Comment**

  * Comes from writing notes in the margin.
  * A comment is a note for humans, not an instruction for Python.
  * Historically, comments became important as programs grew longer and programmers needed to explain their thinking to other people.

* **String**

  * Comes from the idea of a “string of characters.”
  * Text is made by stringing letters, numbers, spaces, and symbols together.
  * The phrase “character string” was used in early computer science to describe a sequence of text characters stored in memory.

* **Number**

  * Comes from math.
  * Python uses numbers for counting, measuring, and calculating.
  * Computers were first used heavily for numerical calculation, so numbers are one of the oldest and most central ideas in programming.

* **Boolean**

  * Named after George Boole, a mathematician who studied true/false logic.
  * A Boolean value is either `True` or `False`.
  * George Boole’s work in the 1800s became a foundation for digital logic and modern computing.

* **Variable**

  * Comes from math.
  * A variable is a name whose value can vary or change.
  * Programming borrowed the word from algebra, where letters like `x` and `y` stand for values.

* **Operator**

  * Comes from math.
  * An operator is a symbol that performs an operation, like `+`, `-`, `*`, or `==`.
  * Early programming languages borrowed many operators directly from mathematical notation.

* **Expression**

  * Comes from math and language.
  * An expression is a piece of code that expresses a value Python can figure out.
  * Programming languages inherited this idea from mathematics, where expressions like `3 + x` are built from values, names, and operators.

* **Conditional**

  * Comes from the word “condition.”
  * A conditional runs code only if a condition is true.
  * Conditional branching became one of the basic building blocks of programming because it lets a machine choose between different paths.

* **Indentation**

  * Comes from writing and formatting.
  * Indentation means moving text inward to show structure.
  * Python made indentation part of the language itself, unlike many older languages that used braces like `{}` or keywords like `begin` and `end`.

* **List**

  * Comes from everyday lists.
  * A Python list keeps multiple things in order, like a shopping list.
  * Lists are one of the oldest collection ideas in programming, especially in languages that worked with sequences of data.

* **Dictionary**

  * Comes from real dictionaries.
  * A Python dictionary lets you look something up by a key, like looking up a word to find its meaning.
  * In computer science, this idea is related to “hash tables,” a fast lookup structure developed to find stored values efficiently.

* **Loop**

  * Comes from the idea of going around again.
  * A loop repeats code until it is done.
  * Loops became essential because computers are especially good at doing repetitive work quickly and accurately.

* **Control flow**

  * Comes from the idea that a program has a path.
  * Control flow decides which direction the program goes next.
  * The term became common as programmers studied how execution moves through instructions, branches, loops, and function calls.

* **Function**

  * Comes from math, but in programming it means a reusable action.
  * A function takes input, does work, and may give back output.
  * Programming borrowed the word from mathematics, but expanded it into a way to organize reusable blocks of instructions.

* **Import**

  * Comes from bringing something in.
  * An import brings extra tools into your program.
  * As programs became larger, languages added ways to reuse code from separate files, libraries, and modules instead of rewriting everything.

* **Error**

  * Comes from the ordinary idea of a mistake or problem.
  * An error tells you that Python could not understand or run something.
  * Early computers often failed silently or with cryptic machine messages; modern programming languages try to give more helpful error names and locations.


# ------



## Appendix B: History Lesson — How Did These Ideas Come to Be?

Programming syntax did not appear all at once. Most of these ideas came from a simple problem: **how do we give precise instructions to a machine, while still writing something humans can read?**

#----

## 1. First came instructions

Early computers did not understand friendly words like `if`, `for`, or `print`. Programmers had to work close to the machine: memory locations, numeric instructions, and hardware-specific commands. Programming languages grew out of the need to make those instructions easier for humans to write and understand. Britannica describes early programming languages as being close to the instructions directly executed by hardware. ([Encyclopedia Britannica][1])

That is where the basic idea of a program comes from:

* put values somewhere
* do operations on them
* decide what to do next
* repeat instructions
* organize the result

#----

## 2. Then came numbers, variables, and operators

Computers were first used heavily for math, science, engineering, and military calculations. That is why numbers, variables, formulas, and operators became core programming ideas very early.

FORTRAN, created at IBM in the 1950s, was short for **formula translation**. Its big idea was that scientists and engineers should be able to write formulas in a more natural way instead of spelling out every tiny machine instruction. IBM describes Fortran as created in 1954 and commercially released in 1957, and as one of the most influential early programming languages. ([IBM][2])

That history leads directly to things like:

* `x = 3`
* `y = x + 2`
* `total = price * count`

So when students learn variables and arithmetic operators, they are learning one of the oldest reasons programming languages exist: **make the machine do calculations using human-readable formulas.**

#----

## 3. Then came true / false logic

The idea of `True` and `False` comes from logic, especially the work of George Boole. Boole helped turn logical reasoning into algebraic symbols, which later became important for digital circuits and programming. Britannica notes that Boolean algebra is basic to the design of digital computer circuits. ([Encyclopedia Britannica][3])

That history leads to:

* `True`
* `False`
* `score >= 90`
* `name == "Ada"`

Comparison operators matter because they let a program ask questions. Once a program can ask questions, it can choose what to do.

#----

## 4. Then came expressions

Expressions came from math notation too. A math expression like `3 + x` combines values, names, and operators into something that can be evaluated.

Programming kept that idea, but made it more general. In Python, all of these are expressions:

* `3 + 4`
* `age`
* `age >= 13`
* `"Hi " + name`
* `items[0]`

This is why expressions deserve their own chapter: they are the bridge between “I know the pieces” and “I can compose code.” Without expressions, conditionals, loops, function calls, returns, and collection lookups are much harder to understand.

#----

## 5. Then came decisions and control flow

Once programs could calculate and compare, they needed to choose between paths. That gave us conditionals: `if`, `else`, and related ideas.

ALGOL 60 was especially influential in making programming languages look more like structured, readable algorithms. Britannica notes that ALGOL was widely used for publishing algorithms and contributed important notation for describing programming language structure. ([Encyclopedia Britannica][4])

That history leads to:

```python
if score >= 90:
    print("Great job")
else:
    print("Keep going")
```

The important new idea is not just comparison. It is **branching**: the program can go one way or another.

#----

## 6. Then came blocks and indentation

As programs grew, programmers needed a way to show which instructions belonged together. Many older languages used words like `begin` and `end`, or symbols like `{` and `}`. ALGOL 60 helped popularize block structure; its revised report described blocks as sequences of declarations and statements enclosed between `begin` and `end`. ([softwarepreservation.computerhistory.org][5])

Python chose indentation instead. The official Python Design and History FAQ says Guido van Rossum considered indentation for grouping statements elegant and helpful for clarity, and notes that it avoids disagreement between what the parser sees and what the human reader sees. ([Python documentation][6])

That history leads to:

```python
if ready:
    print("Go")
    print("Now")
```

In Python, indentation is not decoration. It is syntax.

#----

## 7. Then came collections

Once programs handled more than one value at a time, they needed containers.

Lists came from the need to keep values in order:

```python
scores = [90, 85, 100]
```

Dictionaries came from the need to look values up by name or key:

```python
person = {"name": "Ada", "age": 12}
```

The official Python tutorial describes dictionaries as a built-in data type also known in other languages as “associative memories” or “associative arrays.” ([Python documentation][7])

So collections came from a practical problem: real programs do not work with one value at a time. They work with groups of values.

#----

## 8. Then came loops

Computers are useful because they can repeat work quickly and reliably. Loops grew out of that need.

Instead of writing:

```python
print("Hi")
print("Hi")
print("Hi")
```

you can write:

```python
for i in range(3):
    print("Hi")
```

Loops are part of control flow: they control where the program goes next. Instead of moving straight down once, the program can go back and run a block again.

#----

## 9. Then came functions and reusable pieces

As programs got bigger, programmers needed ways to name a chunk of work and reuse it. That gave us functions, procedures, subroutines, and later modules and imports.

ALGOL 60 was important here too; it influenced how later languages described algorithms, blocks, procedures, and syntax. ([Encyclopedia Britannica][4]) Lisp, developed by John McCarthy in the late 1950s, also pushed ideas about functions, recursion, and symbolic computation; McCarthy’s own history of Lisp describes his desire for an algebraic list-processing language for AI work beginning in the 1950s. ([JMC Stanford][8])

That history leads to:

```python
def greet(name):
    return "Hi " + name
```

A function lets a programmer say: “This group of instructions is one idea. Give it a name.”

#----

## 10. Then came imports and libraries

Once people had useful functions, they wanted to share them. Instead of rewriting the same tools in every program, programmers put reusable code into libraries and modules.

That history leads to:

```python
import math
from random import randint
```

Imports are part of a larger historical trend: programming became less about writing everything yourself and more about combining reusable pieces.

#----

## 11. Then came better errors

Early programming was hard partly because mistakes were difficult to understand. As languages became more human-friendly, they also became better at explaining what went wrong.

That history leads to names like:

* `SyntaxError`
* `NameError`
* `TypeError`
* `IndexError`

Errors are not just failures. They are part of the conversation between the programmer and the language.

#----

## Big picture

These ideas came from different historical needs:

* **Numbers, variables, operators:** make formulas readable.
* **Booleans and comparisons:** let programs ask questions.
* **Expressions:** let programmers compose small pieces into answers.
* **Conditionals:** let programs choose a path.
* **Blocks and indentation:** show which instructions belong together.
* **Collections:** manage many values at once.
* **Loops:** repeat work.
* **Functions:** name and reuse a chunk of work.
* **Imports:** reuse work from somewhere else.
* **Errors:** help humans fix what went wrong.

Python did not invent all of these ideas. It inherited many of them from decades of programming language history, then chose a style that emphasizes readability, simple syntax, and clear structure.

[1]: https://www.britannica.com/technology/computer-programming-language?utm_source=chatgpt.com "computer programming language - Encyclopedia Britannica"
[2]: https://www.ibm.com/history/fortran?utm_source=chatgpt.com "Fortran - IBM"
[3]: https://www.britannica.com/biography/George-Boole?utm_source=chatgpt.com "George Boole | Facts, Biography, Death, Education, & Books - Britannica"
[4]: https://www.britannica.com/technology/ALGOL-computer-language?utm_source=chatgpt.com "ALGOL | Programming, Syntax & Compiler | Britannica"
[5]: https://softwarepreservation.computerhistory.org/ALGOL/report/Algol60_revised_report_CACM.pdf?utm_source=chatgpt.com "Revised report on the algorithm language ALGOL 60 - Software Preservation"
[6]: https://docs.python.org/3/faq/design.html?utm_source=chatgpt.com "Design and History FAQ — Python 3.14.5rc1 documentation"
[7]: https://docs.python.org/3/tutorial/datastructures.html?utm_source=chatgpt.com "5. Data Structures — Python 3.14.5rc1 documentation"
[8]: https://jmc.stanford.edu/articles/lisp/lisp.pdf?utm_source=chatgpt.com "History of Lisp - Computer Science"



## Appendix C: Coder Vocabulary — Names You Will Hear Later

Do not worry about mastering these yet. This appendix is just so the words sound less mysterious when you hear them.


< TODO: I need to rerank and curate these >


#----

## Language Mechanics — How Python runs and behaves

* **Interpreter** — A program that reads and runs code, like Python does.
* **Runtime** — The period when a program is actually running.
* **Bytecode** — A lower-level form of code that Python can run more efficiently than raw source code.
* **Compiler** — A program that translates source code into another form before running.
* **Binary** — Machine-readable data or instructions, often not meant to be read by humans.
* **Executable** — A file the computer can run as a program.
* **Interpreted language** — A language usually run by an interpreter instead of directly by the machine.
* **Compiled language** — A language usually translated into machine code before it runs.
* **Main guard** — The `if __name__ == "__main__":` pattern used when running a Python file directly.
* **Entry point** — The place where a program starts running.
* **Shebang** — The first line of a script that says what program should run it.
* **Import path** — The places Python looks when you write `import`.
* **Import side effect** — Something that happens just because a module was imported.
* **Circular import** — When two files try to import each other and cause problems.
* **Virtual environment** — A separate Python setup for one project.
* **Lock file** — A file that records exact dependency versions.
* **Pinning** — Choosing an exact package version, like `numpy==2.0.0`.
* **Dependency hell** — When library versions conflict and are hard to fix.

#----

## Advanced Control Patterns — How programs organize behavior

* **Async** — A style where code can wait for slow tasks without stopping everything.
* **Blocking** — When code waits for something before continuing.
* **Concurrency** — Managing multiple tasks during the same time period.
* **Parallelism** — Actually running multiple tasks at the same time.
* **Race condition** — A bug where timing changes the result.
* **Deadlock** — A situation where tasks are stuck waiting on each other.
* **Generator** — Code that produces values one at a time instead of all at once.
* **Yield** — The keyword a generator uses to produce its next value.
* **Lazy evaluation** — Waiting to compute values until they are actually needed.
* **Eager evaluation** — Computing values immediately.
* **Callback** — A function passed into other code so it can be called later.
* **Handler** — Code that responds to an event, request, or special case.
* **Hook** — A place where you can plug in custom behavior.
* **Wrapper** — Code that surrounds another piece of code to change or extend it.
* **Decorator** — Python syntax for wrapping a function or class with extra behavior.
* **Context manager** — Code used with `with` to set something up and clean it up afterward.

#----

## Code Meaning — Names for what code is made of

* **Object** — A value Python can store, pass around, and work with.
* **Type** — The kind of value something is, like `int`, `str`, `list`, or `dict`.
* **Reference** — A connection from a name to an object in memory.
* **Scope** — The part of a program where a name can be used.
* **Namespace** — A place where Python keeps track of names.
* **Class** — A blueprint for making objects.
* **Instance** — An object made from a class.
* **Method** — A function that belongs to an object.
* **Attribute** — A value that belongs to an object.
* **Mutable** — Able to be changed after it is created.
* **Immutable** — Not able to be changed after it is created.
* **State** — The current remembered information in a program.
* **Stateful** — Code that remembers information between steps.
* **Stateless** — Code that does not remember information between calls.
* **Pure function** — A function that only uses its inputs and has no side effects.
* **Side effect** — Something code changes outside its own result, like printing, saving a file, or modifying a list.
* **Invariant** — A rule that should always stay true.
* **Precondition** — Something that must be true before code runs correctly.
* **Postcondition** — Something that should be true after code finishes.

#----

## Data and Values — How information is represented

* **None** — Python’s special value for “nothing here.”
* **Truthy / Falsy** — Values Python treats like `True` or `False` in a decision.
* **Null / nil** — A general programming word for “nothing”; in Python this is `None`.
* **Iterable** — Something you can loop over.
* **Iterator** — Something that gives one item at a time.
* **Comprehension** — Compact Python syntax for building a list, dict, or set.
* **Sentinel value** — A special value used to mean something unusual, like “not found.”
* **Constant** — A value that is not supposed to change.
* **Global variable** — A variable available across a large part of a program.
* **Local variable** — A variable available only inside a small part of a program.
* **Serialization** — Turning data into a format that can be saved or sent.
* **Parsing** — Reading text or data and turning it into useful structure.
* **Schema** — The structure of data, such as tables, fields, and types.
* **Migration** — A change to a database’s structure.

#----

## Core Reading Vocabulary — Words that describe ordinary code

* **Expression** — A piece of code that produces a value.
* **Statement** — A complete instruction Python can run.
* **Assignment** — Giving a value to a name, like `score = 10`.
* **Literal** — A value written directly in code, like `3`, `"hello"`, or `True`.
* **Identifier** — A name in code, like a variable name or function name.
* **Parameter** — A name listed in a function definition.
* **Argument** — A value given to a function or command.
* **Return value** — The value a function gives back.
* **Call** — Running a function by using parentheses.
* **Module** — A Python file that can contain reusable code.
* **Package** — A group of modules organized together.
* **Library** — Reusable code someone else wrote for you to use.
* **API** — The way one piece of code offers tools for another piece of code to use.
* **Algorithm** — A step-by-step method for solving a problem.
* **Data structure** — A way to organize data, like a list, dictionary, set, or tree.
* **Index** — A position number used to get an item from a sequence.
* **Slice** — A way to take part of a sequence, like `items[1:4]`.
* **I/O** — Input and output, such as reading files, writing files, or using the network.
* **Standard input** — The normal way a program receives text input.
* **Standard output** — The normal way a program prints text output.
* **Process** — A running program on your computer.
* **Exit code / exit status** — A number a program gives back to say whether it succeeded or failed.
* **Environment** — The setup Python is running in, including installed libraries and settings.
* **Dependency** — A library your program needs in order to run.
* **Package manager** — A tool that installs and manages libraries, like `pip`.
* **Requirements file** — A file listing Python packages to install.
* **Source code** — Human-readable code written by a programmer.
* **Script** — A code file meant to be run directly, often for automation.
* **Program** — A set of instructions that a computer can run.
* **REPL** — An interactive Python prompt where you type code and immediately see what it does.
* **Notebook** — A document that mixes code, output, notes, and experiments.
* **Notebook cell** — One runnable block of code or text inside a notebook.
* **Kernel** — The running Python process behind a notebook.
* **Session** — One period of running Python where variables and memory are still available.

#----

## Tools and Project Workflow — How coders work with files and changes

* **Terminal / command line** — A text-based place where you can run commands.
* **Shell** — The program that understands terminal commands.
* **CLI** — A command-line interface; a tool you use by typing commands.
* **Command** — Something you type in the terminal to make the computer do a task.
* **Option / flag** — Extra command settings, like `--help` or `-v`.
* **Flag** — An option that changes how a command or program runs.
* **Filesystem** — The folders and files on your computer.
* **Path** — The address of a file or folder, like `project/data.txt`.
* **Relative path** — A file path starting from your current folder.
* **Absolute path** — A full file path starting from the filesystem root.
* **Working directory** — The folder Python is currently running from.
* **Root directory** — The top-level folder of a filesystem or project.
* **Home directory** — Your personal user folder on a computer.
* **Directory / folder** — A container that holds files and other folders.
* **File extension** — The ending of a filename, like `.py`, `.txt`, `.csv`, or `.json`.
* **Hidden file** — A file usually not shown by default, often starting with `.`.
* **Repository / repo** — A project folder tracked by a version control tool like Git.
* **Version control** — A system for tracking changes to code over time.
* **Git** — A common tool for saving code history and collaborating.
* **Commit** — A saved snapshot of changes.
* **Branch** — A separate line of work in a repo.
* **Merge** — Combining changes from one branch into another.
* **Pull request / PR** — A proposed code change for others to review.
* **Clone** — Make a copy of a repository on your computer.
* **Pull** — Download the latest changes from a remote repo.
* **Push** — Upload your commits to a remote repo.
* **Diff** — A view of what changed between two versions.
* **Conflict** — When two changes disagree and a human must choose what to keep.
* **Remote** — A shared copy of a Git repository, often on GitHub.
* **Origin** — The default name for the main remote repo.
* **Main branch** — The primary branch of a project.
* **Checkout** — Switch to another branch or restore a file.
* **Working tree** — The current files in your Git project folder.
* **Staging area** — The place Git holds changes before a commit.
* **Rebase** — Move commits so they appear on top of newer work.
* **Tag** — A named marker for a specific version, often a release.

#----

## Debugging, Testing, and Code Quality — How coders find and prevent problems

* **Bug** — A mistake or problem in code.
* **Debugging** — Finding and fixing problems in code.
* **Exception** — A problem Python can report and sometimes recover from.
* **Traceback** — The error report that shows where Python ran into trouble.
* **Stack trace** — Another name for the error report showing the path to the problem.
* **Breakpoint** — A place where a debugger pauses the program so you can inspect it.
* **Logging** — Recording messages while a program runs so you can understand what happened.
* **Print debugging** — Using `print()` to check what your code is doing.
* **Reproduce** — Make a bug happen again on purpose.
* **Minimal example** — The smallest code that still shows a problem.
* **Crash** — When a program stops unexpectedly.
* **Hang** — When a program keeps running but stops making progress.
* **Timeout** — When a task is stopped because it took too long.
* **Retry** — Trying an operation again after it fails.
* **Fallback** — A backup plan when the preferred option fails.
* **Edge case** — A weird or uncommon situation your code still needs to handle.
* **Happy path** — The normal case where everything works as expected.
* **Regression** — A bug that appears after something used to work.
* **Off-by-one error** — A common mistake where code is wrong by exactly one step or index.
* **Silent failure** — When something fails without clearly reporting the problem.
* **Test** — Code or steps used to check whether other code works.
* **Unit test** — A test for one small piece of code.
* **Integration test** — A test that checks whether multiple pieces work together.
* **Test suite** — A collection of tests.
* **Assertion** — A check that something must be true.
* **Failing test** — A test showing that something is broken.
* **Flaky test** — A test that sometimes passes and sometimes fails without a clear code change.
* **Fixture** — Test setup data or objects used by tests.
* **Mock** — A fake version of something used during testing.
* **Coverage** — A measure of how much code is exercised by tests.
* **CI / continuous integration** — A system that automatically runs checks when code changes.
* **Linting** — Checking code for style problems or suspicious patterns.
* **Formatting** — Automatically arranging code to follow a consistent style.
* **Code smell** — Code that works but feels suspicious or hard to maintain.
* **Technical debt** — Messy or rushed code that will cost effort later.
* **Refactoring** — Improving how code is organized without changing what it does.
* **Maintainability** — How easy code is to understand, change, and fix.
* **Readability** — How easy code is for humans to read.
* **Robustness** — How well code handles unexpected situations.
* **Verbose** — Giving extra details in output or logs.
* **Log level** — The importance of a log message, like debug, info, warning, or error.

#----

## Design and Maintenance — How coders talk about structure

* **Abstraction** — A simpler idea that hides messy details.
* **Interface** — The part of code other code is expected to use.
* **Implementation** — The hidden details of how something actually works.
* **Boilerplate** — Repetitive code you often have to write before the interesting part.
* **Glue code** — Code that connects other pieces together.
* **Configuration / config** — Settings that change how a program behaves.
* **Environment variable** — A setting stored outside the code, often used for paths, secrets, or modes.
* **Default** — The value used when you do not choose one.
* **Build** — Preparing code so it can run or be shared.
* **Deploy** — Put code somewhere users or systems can run it.
* **Release** — A shared version of software.
* **Version** — A label for a particular release or state of code.
* **Patch** — A small code change, often to fix a bug.
* **Hotfix** — An urgent fix for a problem in released software.
* **Deprecated** — Still available, but no longer recommended.
* **Backward compatible** — A change that does not break old code.
* **Upgrade** — Install a newer version of a package.
* **Downgrade** — Install an older version of a package.
* **Cache** — Stored results used to avoid repeating slow work.
* **Optimization** — Making code faster, smaller, or more efficient.
* **Prototype** — A rough version made to test an idea.
* **MVP** — Minimum viable product; the smallest useful version.
* **Scaffold** — Starter structure for a project.
* **Spike** — A short experiment to learn whether an approach works.
* **Documentation** — Written explanation of how code or tools are meant to be used.
* **README** — The first file people usually read to understand a project.
* **Changelog** — A list of what changed between versions.
* **TODO** — A note about something that still needs to be done.
* **Issue / ticket** — A tracked task, bug, or feature request.
* **Code review** — Having another programmer inspect code before it is accepted.

#----

## Web, Systems, and Data — The world around Python

* **Memory** — The temporary workspace where Python keeps values while a program is running.
* **Server** — A program or computer that provides something to other programs.
* **Client** — A program that asks a server for something.
* **Request** — A message asking for data or action.
* **Response** — The answer sent back after a request.
* **Endpoint** — A specific address where an API can be used.
* **Localhost** — Your own computer, treated like a server.
* **Port** — A numbered doorway where network programs listen.
* **Protocol** — A rule system for how programs communicate.
* **HTTP** — The common protocol used by websites and web APIs.
* **URL** — The address of something on the web.
* **Payload** — The main data sent in a request or response.
* **Status code** — A number that says what happened to a web request, like `200` or `404`.
* **Authentication** — Proving who you are.
* **Authorization** — Deciding what you are allowed to do.
* **Credential** — Information used to prove who you are, like a password or token.
* **Token** — A secret value used to access a service.
* **Secret** — Sensitive value like a password, API key, or token.
* **Permission** — What a user or program is allowed to do.
* **Hash** — A fixed-size fingerprint made from data.
* **Encryption** — Scrambling data so only authorized people can read it.
* **Database** — A system for storing and looking up data.
* **Query** — A request for data from a database.
* **Record** — One stored item in a database.
* **Field** — One named piece of data inside a record.
* **JSON** — A common text format for structured data.
* **CSV** — A simple table format stored as text.
* **YAML** — A human-friendly text format often used for configuration.
* **Frontend** — The part of software users directly see or interact with.
* **Backend** — The part of software that handles data, logic, servers, or storage.
* **Full stack** — Working with both frontend and backend.
* **Service** — A program that provides a useful function to other programs.
* **Daemon** — A background program that keeps running.
* **Container** — A packaged environment for running software consistently.
* **Docker** — A common tool for building and running containers.
* **Image** — A saved template used to create containers.
* **Volume** — A way for a container to access persistent files.
* **Mount** — Connecting a file or folder into another place.
* **Latency** — How long one operation takes to respond.
* **Throughput** — How much work a system can do over time.
* **Bottleneck** — The slow part that limits the whole system.
* **Overhead** — Extra work needed to manage a task, not the task itself.
* **Scalability** — How well software keeps working as size or demand grows.
* **Portability** — How easily code can run in different places.

