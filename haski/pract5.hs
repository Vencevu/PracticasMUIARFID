module DecBin where

data Tree a = Leaf a | Branch (Tree a) (Tree a) deriving Show
data BinTreeInt = Void | Node Int BinTreeInt BinTreeInt deriving Show
type Person = String
type Book = String
type Database = [(Person, Book)]

decBin :: Int -> [Int]
decBin x = if x <2 then [x]
else (mod x 2) : decBin (div x 2)

binDec :: [Int] -> Int
binDec (x:[]) = x
binDec (x:xs) = x + binDec xs * 2

divisors :: Int -> [Int]
divisors 1 = [1]
divisors x = divisores x 1

divisores :: Int -> Int -> [Int]
divisores x y
 |mod x y == 0 = y:divisores x (y+1)
 |y > x = []
 |otherwise = divisores x (y+1)

member :: Int -> [Int] -> Bool
member x y = memberi x y 0

memberi :: Int -> [Int] -> Int -> Bool
memberi x y z
 |z >= length y = False
 |(y !! z) == x = True
 |otherwise = memberi x y (z+1)

isPrime :: Int -> Bool
isPrime x
 |length (divisors x) <= 2 = True
 |otherwise = False

primes :: Int -> [Int]
primes n = primesx n 1

primesx :: Int -> Int -> [Int]
primesx n x
 |n == 0 = []
 |isPrime x == True = x : primesx (n-1) (x+1)
 |otherwise = primesx n (x+1)

selectEven :: [Int] -> [Int]
selectEven i = selectEvenx i 0

selectEvenx :: [Int] -> Int -> [Int]
selectEvenx x i
 |i >= length x = []
 |even (x !! i) = (x!!i):selectEvenx x (i+1)
 |otherwise = selectEvenx x (i+1)

selectEvenPos :: [Int] -> [Int]
selectEvenPos x = selectY x 0

selectY :: [Int] -> Int -> [Int]
selectY x i
 |i >= length x = []
 |even i = (x!!i):selectY x (i+1)
 |otherwise = selectY x (i+1)

ins :: Int -> [Int] -> [Int]
ins n [] = [n]
ins n (x:xs) 
 |n <= x = (n:x:xs)
 |otherwise = x : (ins n xs)

iSort :: [Int] -> [Int]
iSort [] = []
iSort (x:xs) = ins x (iSort xs)

doubleAll :: [Int]->[Int]
doubleAll x = map (*2) x

map' :: (Int->Int)->[Int]->[Int]
map' f x = [f i|i<-x]

filter' :: (Int -> Bool) -> [Int] -> [Int]
filter' f x = [i|i<-x,f i]

obtain :: Database -> Person -> [Book]
obtain dBase thisPerson = [book | (person,book) <- dBase, person == thisPerson]

borrow :: Database -> Book -> Person -> Database
borrow b l p
 |estaLibro b l = b
 |otherwise = ((p,l):b)

estaLibro :: Database -> Book -> Bool
estaLibro [] l = False
estaLibro ((x,y):xs) l
 |y == l = True
 |otherwise =  estaLibro xs l

return' :: Database -> (Person,Book) -> Database
return' [] (p,l) = []
return' (x:xs) (p,l)
 |estaLibro (x:xs) l == False = (x:xs)
 |x == (p,l) = xs
 |otherwise = (x: (return' xs (p,l)))

simetrico :: Tree x -> Tree x
simetrico (Leaf x) = (Leaf x)
simetrico (Branch x y) = (Branch (simetrico y) (simetrico x))

listToTree::[a]->Tree a
listToTree [x] = (Leaf x)
listToTree (x:xs) = (Branch (Leaf x) (listToTree xs))

treeToList :: Tree a -> [a]
treeToList (Leaf x) = [x]
treeToList (Branch x y) = (treeToList x)++(treeToList y)

insTree :: Int -> BinTreeInt -> BinTreeInt
insTree x Void = (Node x Void Void)
insTree x (Node y z a)
 |x <= y = (Node y (insTree x z) a)
 |otherwise = (Node y z (insTree x a))

creaTree :: [Int] -> BinTreeInt
creaTree [] = Void
creaTree [x] = (Node x Void Void)
creaTree (x:y:xs)
 | x > y = (Node x (Node y Void Void) (creaTree xs))
 |otherwise = (Node x (creaTree xs) (Node y Void Void))

treeElem :: Int -> BinTreeInt -> Bool
treeElem x Void = False
treeElem x (Node y z a)
 |x == y = True
 |x > y = treeElem x a
 |otherwise = treeElem x z

numleaves :: Tree a -> Int
numleaves (Leaf x) = 1
numleaves (Branch a b) = numleaves a + numleaves b

dupElem :: Tree a -> Tree a
dupElem a = listToTree (map' (*2) (treeToList a))
