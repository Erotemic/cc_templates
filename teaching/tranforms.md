## **Lesson Plan: Playing with Affine Transformations in Python**

### **1. Learning Objectives**

By the end of this lesson, the student should be able to:

* Understand what an affine transformation is and how it differs from a purely linear transformation.
* Represent affine transformations as matrices.
* Apply affine transformations to 2D points.
* Combine multiple transformations into a single matrix.
* Use Python (NumPy/Matplotlib) to visualize transformations.

---

### **2. Core Concepts**

1. **Affine transformation** = linear transformation + translation.
2. Represented using **homogeneous coordinates**:

   $$
   \begin{bmatrix}
   x' \\
   y' \\
   1
   \end{bmatrix}
   =
   \begin{bmatrix}
   a_{11} & a_{12} & t_x \\
   a_{21} & a_{22} & t_y \\
   0      & 0      & 1
   \end{bmatrix}
   \cdot
   \begin{bmatrix}
   x \\
   y \\
   1
   \end{bmatrix}
   $$
3. Examples: rotation, scaling, shear, reflection, translation.

---

### **3. Teaching Flow**

#### **Step 1 — Intuitive Intro (10 min)**

* Show transformations visually on graph paper: moving points, stretching, rotating.
* Emphasize: *linear part* changes shape/orientation, *translation* moves everything.

#### **Step 2 — Matrix Form (15 min)**

* Introduce 3×3 matrix representation for 2D affine transforms.
* Show how identity matrix leaves points unchanged.
* Explain homogeneous coordinate trick (extra `1`).

#### **Step 3 — Hands-On with NumPy (20 min)**

```python
import numpy as np
import matplotlib.pyplot as plt

# Define some points: a square
square = np.array([
    [0, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 1, 1],
    [0, 0, 1]  # close the loop
])

def transform(points, matrix):
    return points @ matrix.T  # apply transformation

# Example: translate by (2, 1)
translate = np.array([
    [1, 0, 2],
    [0, 1, 1],
    [0, 0, 1]
])

trans_square = transform(square, translate)

plt.plot(square[:,0], square[:,1], label='Original')
plt.plot(trans_square[:,0], trans_square[:,1], label='Translated')
plt.axis('equal'); plt.legend(); plt.show()
```

* Let them run it and see the shape move.

#### **Step 4 — Composition of Transformations (15 min)**

* Multiply transformation matrices to combine them.
* Show that `rotate @ scale @ translate` applies transformations in reverse order of multiplication.
* Challenge them to guess what a combined matrix will do before plotting.

#### **Step 5 — Creative Play (20 min)**

* Rotate shape around origin.
* Scale in only one axis.
* Apply shear.
* Make a "house" shape and transform it into fun variations.

---

### **4. Extension Challenges**

* Write a function that builds a rotation matrix given an angle in degrees.
* Apply multiple random transformations to a set of points and predict the result.
* Use transformations to make a simple animation in Matplotlib.
* Try reversing a transformation by using the matrix inverse.

---

### **5. Key Takeaways**

* Affine transformations are a compact, powerful way to express geometric changes.
* The translation part makes them more general than linear transformations.
* They compose neatly via matrix multiplication.
* Homogeneous coordinates make translations possible in matrix form.

---

### **6. Resources**

* 3Blue1Brown video on linear transformations.
* NumPy documentation on `@` (matrix multiplication).
* Matplotlib for visualization.

