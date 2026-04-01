import Data.List (delete)

permute :: Eq a => [a] -> [[a]] 
permute [] = [[]]
permute xs = [x : rest | x <- xs, rest <- permute (delete x xs)]

countPermutations xs = length (permute xs)