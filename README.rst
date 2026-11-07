CC Templates
============

Small project templates and teaching examples for students learning Python.

Start with the project folder that matches the student's comfort level:

* ``python_basics``: short beginner exercises.
* ``choose_your_own_adventure``: text-based adventure game, several versions
  showing how the same idea grows from a few ``if`` statements into a
  data-driven program.
* ``platformer``: a 2D pygame platformer.
* ``rpg``: a larger pygame RPG with more structure.
* ``peakshift``: Peakshift, an authored-room Celeste-inspired precision platformer
  with dash and wall movement, plus student-coded optional mechanics.
* ``undercode``: UnderCode, a pygame overworld and encounter template with
  separate overworld and encounter engines, Python letter-map stories, guided
  implementation exercises, and independent game-design challenges.
* ``fpx3d``: Prism Vault, a first-person 3D Panda3D treasure hunt with
  guided student missions and independent challenges.
* ``rts``: a real-time strategy game ported from a high school project.
* ``manim``: short animation examples for learning Manim.

Running the games
-----------------

For the projects with a ``pyproject.toml`` (``platformer``, ``rpg``,
``fpx3d``, ``undercode``, ``peakshift``), the simplest way to run them is from inside the
project folder:

.. code-block:: bash

   python main.py

No install step needed. If a Python package is missing, ``main.py`` will
tell you which one and print the exact ``pip install`` command to copy.

Once you are comfortable with Python projects, you can install one in
editable mode instead:

.. code-block:: bash

   pip install -e .

Other folders
-------------

* ``teaching``: instructor materials, handouts, and exercises.


SeeAlso
-------

* https://github.com/Erotemic/ambition_lite
* https://github.com/Erotemic/maryo_lite

Further Reading and Interesting Tutorials
-----------------------------------------

https://github.com/alvinng4/grav_sim/tree/main
