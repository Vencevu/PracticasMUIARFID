module Queue2 (Queue, empty, enqueue, dequeue, first, isEmpty, size) where
data Queue a = EmptyQueue | Item a (Queue a)
empty = EmptyQueue
enqueue x EmptyQueue = Item x EmptyQueue
enqueue x (Item a q) = Item a (enqueue x q)
dequeue (Item _ q) = q
first (Item a _) = a
isEmpty EmptyQueue = True
isEmpty _ = False
size EmptyQueue = 0
size (Item _ q) = 1 + size q

instance (Eq a) => Eq (Queue a) where
 EmptyQueue == EmptyQueue  = True
 (Item b x) == (Item c y) = (b == c) && ((dequeue (Item b x)) == (dequeue (Item c y)))
 _ == _ = False
