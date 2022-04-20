#Checks whether g is a generator for the cyclic group Zp*

def is_generator(p,g): #p = prime, g = generator
	z = set()
	for i in range(1,p):
		z.add(i)

	first = (g**2) % p

	for i in range(1,p):
		e = (first*g)%p
		if e in z:
			z.remove(e)
		first = e
		
	if len(z) == 0:
		return True
	else:
		return False

#Finds n generators for the cyclic group Zp*. If the number of generators is less than n, then returns them anyway without sending errors.

def find_group_generators(p,n): #p = prime, n = number of generators
	generators = []
	for i in range(1,p):
		if is_generator(p,i):
			if len(generators) < n:
				generators.append(i)
			else:
				return generators
		if i==(p-1):
			return generators
	



