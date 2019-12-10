import Data.Char

fact :: Int -> Int
fact 0 = 1
fact n = n * fact(n-1)

max' :: Int -> Int -> Int
max' a b = if a<b then b else a

remainder :: Int -> Int -> Int
remainder a b = if a < b then a else remainder (a-b) b

numCbetw2 :: Char -> Char -> Int
numCbetw2 a b =if a==b then 0 else abs((ord a)-(ord b))-1

addRange :: Int -> Int -> Int
addRange a b = if a==b then a else b + addRange a (b-1)

leapyear :: Int -> Bool
leapyear a = if (((remainder a 4)==0 && (remainder a 100)/=0)||(remainder a 400)==0) then True else False

daysAmonth :: Int -> Int -> Int
daysAmonth a b
 | a==2 && (leapyear b == True) = 28
 | a==2 = 29
 |(odd a)==True && a < 9 = 31
 |(odd a)==False && a > 2 && a < 8 = 30
 |(odd a)==True = 30
 |(odd a)==False = 31

sumFacts :: Int -> Int
sumFacts n = if n==1 then 1 else (fact n) + sumFacts (n-1)

