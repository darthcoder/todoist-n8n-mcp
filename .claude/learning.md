sensei-halp: Permutations — Session Notes
Concept: All permutations of a set
Idiom: Recursion (beginner weight)
Languages: Pseudocode → Python → Haskell

Phase 1 — Pseudocode
Started with the table analogy: you, me, and a third person, three chairs. How many ways?

Student worked it out from first principles — first chair has 3 choices, second has 2, last has whoever's left.

Key moment: "it feels like mathematical induction" — student connected permutations to recursion without being told. The algorithm emerged:

Pick each element. Put it first. Do the same thing with the rest. Base case: empty set has one permutation — the empty arrangement [[]].

Phase 2 — Python (permutations.py)
Student wrote it without a template. Key discoveries along the way:

Chekhov's gun: popped current_item out of the list then didn't use it — spotted the error themselves
Mutation: pop mutates the list, saving one variable while changing another — student flagged this as "unidiomatic"
Naming is the hardest problem: scoping bugs came from operating on the wrong list at the wrong time — student diagnosed this themselves
.copy() before .pop(): Python's pass-by-reference forced the defensive copy that Haskell would later make unnecessary
Final result:


def permutations(set_of_items):
    list_of_perms = []
    if set_of_items == []:
        return [[]]
    else:
        for song in set_of_items:
            playlist = set_of_items.copy()
            curr = playlist.pop(playlist.index(song))
            sub_perms = permutations(playlist)
            temp = []
            for item in sub_perms:
                temp.append([curr] + item)
            list_of_perms.extend(temp)
        return list_of_perms
Output: [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]

Phase 3 — Haskell (permutations.hs)
Key concepts introduced — only what was needed:

:: for type signatures
Pattern matching: permute [] = ... and permute (x:xs) = ...
: as cons (prepend), same operator for splitting and building
<- as for-each ("drawn from")
Eq a => constraint — elements must support equality for delete to work
delete from Data.List — returns a new list, no mutation, no .copy() needed
The mutation point landed: "there's nothing to protect against" — immutability removed the entire class of bugs from Phase 2.

Final result:


import Data.List (delete)

permute :: Eq a => [a] -> [[a]]
permute [] = [[]]
permute xs = [x : rest | x <- xs, rest <- permute (delete x xs)]

countPermutations xs = length (permute xs)
Verified: countPermutations [1,23,4,456,789,1234,34135,78] → 40320 = 8!

Next weight: Combinations. Same three phases.