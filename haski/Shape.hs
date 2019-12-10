type Side    = Float
type Apothem = Float
type Radius  = Float
type Height = Float
type Volume = Float

data Pentagon = Pentagon Side Apothem
data Circle   = Circle Radius

class Shape a where
 perimeter :: a -> Float
 area :: a -> Float
 volumePrism :: (Shape a) => a -> Height -> Volume
 surfacePrism :: (Shape a) => a -> Height -> Float

instance Shape Pentagon where
 perimeter (Pentagon s a) = 5 * s
 area (Pentagon s a) = 5*((s/2)*a)
 volumePrism (Pentagon s a) height = (area (Pentagon s a)) * height
 surfacePrism (Pentagon s a) height = 12 * (area (Pentagon s a))

instance Shape Circle where
 perimeter (Circle r) = 2 * pi * r
 area (Circle r) = pi*r*r
 volumePrism (Circle r) height = (area (Circle r)) * height
 surfacePrism (Circle r) height = (2*(area(Circle r)))+((perimeter(Circle r))*height)
