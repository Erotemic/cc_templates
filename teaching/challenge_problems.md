Challenge Problem:
* Given an array of numbers `arr` and a target number `target`, determine if there exist any two numbers in the array that can sum to `target`.



The challenge is to write a program can solve this problem. 
In other words, decide if for a specific instance of `arr` and `target` if the
proposition is true or false.

Write a function in Python or Javascript that takes takes `arr` and `target` as
inputs, and returns true if there exist two items in `arr` that sum to `target`
and false otherwise.

Try to do this in 
it in javascript or Python, then try to write it efficiently.

Extra Learning:

Mathematically:

Assume A = (a[1], a[2], ..., a[n]) is an array of integers and target = T is another integer.
The question is:
“Does there exist i, j ∈ {0,...,n-1} such that A[i] + A[j] = T?”


This can be phrased formally in lean:


```lean4
/--
Proposition form (the “math statement”):
There exist indices i and j (valid for the list)
such that xs[i] + xs[j] = target.
-/
def TwoSumProp (xs : List Int) (target : Int) : Prop :=
  ∃ i j : Fin xs.length, xs.get i + xs.get j = target
```

The above reads:

* There is a proposition TwoSumProp that takes two arguments
* the first argument is called "xs" and it has a type, which is a List Int (i.e. a list of integers).
* The second argument is called "target" and has a type of Int (i.e. an integer)
* The next line says there exist, two index variables i and j, such that:
    * both of them are from a finite indexing set the same length as the "xs" list
    * and the sum of the i-th element of xs and the j-th element of xs equals total 


In Lean, we can compute and prove things about this propositions:
```lean4
/--
This tells Lean that the proposition `TwoSumProp xs target` is decidable.

A value of type `Decidable P` is a procedure that can decide whether `P` is true or false.
Here we let Lean construct that procedure automatically.

`infer_instance` is a tactic that asks Lean’s typeclass system to build the instance from
existing ones. It works here because:
- `Fin xs.length` is a finite index type, so ∃ over it is decidable
- equalities on `Fin xs.length` and `Int` are decidable
- the logical connectives `∧` preserve decidability when the parts are decidable
-/
instance (xs : List Int) (target : Int) : Decidable (TwoSumProp xs target) := by
  unfold TwoSumProp
  infer_instance

-- You can *compute* it as a Bool:
#eval decide (TwoSumProp [1, 2, 3, 9] 8)    -- false
#eval decide (TwoSumProp [1, 2, 4, 4] 8)    -- true
#eval decide (TwoSumProp [5] 10)            -- true

-- You can also *prove* it using `by decide` (Lean finds witnesses):
example : TwoSumProp [1, 2, 4, 4] 8 := by
  decide

-- Or prove the negation:
example : ¬ TwoSumProp [1, 2, 3, 9] 8 := by
  decide
```

