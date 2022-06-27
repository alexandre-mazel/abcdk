# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Patterns tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Aldebaran Behavior Complementary Development Kit: patterns."""
print( "importing abcdk.patterns" );

class Singleton(type):
    """The singleton pattern is a design pattern used to implement the mathematical concept of a singleton, by restricting the instantiation of a class to one object."""
    """This is useful when exactly one object is needed to coordinate actions across the system."""
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None
 
    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance
        
class Permutation():
    "A class to generate all permutation possible of a vector"
    "[0,1,2], [0,2,1], ..."
    def __init__(self, pnVectorSize):
        self.combi = list();
        self.nVectorSize = pnVectorSize;
    # __init__ - end
    
    def getNbrElement( self ):
        return self.nVectorSize;
    # getNbrElement - end
    
    def first( self ):
        for i in range( self.nVectorSize ):
            self.combi.append( i );
        return self.combi;
    # first - end
    
    def next( self ):
        "Generates the next permutations of the vector v of length n."
        "@return [], if there are no more permutations to be generated"
        "@return the list, otherwise"
        # /* P2 */
        n = self.getNbrElement();
        # /* Find the largest i */
        i = n - 2;
        while(i >= 0) and (self.combi[i] > self.combi[i + 1]):
            i -= 1;

        # /* If i is smaller than 0, then there are no more permutations. */
        if( i < 0 ):
            return [];

        # /* Find the largest element after vi but not larger than vi */
        k = n - 1;
        while self.combi[i] > self.combi[k]:
            k -= 1;
        val = self.combi[i];
        self.combi[i] = self.combi[k];
        self.combi[k] = val;

        # /* Swap the last n - i elements. */
        k = 0;
        for j  in range( i + 1, (n + i) / 2 + 1 ):
            val = self.combi[j];
            self.combi[j] = self.combi[n - k - 1];
            self.combi[n - k - 1] = val;
            k += 1;
            
        return self.combi;
    # next - end
# class Permutation - ned

class Combination():
    "A class to generate all combinations (order doesn't import) possible of a vector"
    "example: choose 4 element in 5 elements"
    def __init__(self, pnSubsetSize, pnOriginalSize ):
        self.combi = list();
        self.nOriginalSize = pnOriginalSize;
        self.nSubsetSize = pnSubsetSize;
    # __init__ - end
    
    def first( self ):
        for i in range( self.nSubsetSize ):
            self.combi.append( i );
        return self.combi;
    # first - end
    
    def next( self ):
        "Generates the next combination of the vector v of length n."
        "@return [], if there are no more permutations to be generated"
        "@return the list, otherwise"
        i = self.nSubsetSize - 1;
        self.combi[i] += 1;
        while (i >= 0) and (self.combi[i] >= self.nOriginalSize - self.nSubsetSize + 1 + i):
            i -= 1;
            self.combi[i] += 1;

        if (self.combi[0] > self.nOriginalSize - self.nSubsetSize): # /* Combination (n-k, n-k+1, ..., n) reached */
            return []; # /* No more combinations can be generated */

        # /* comb now looks like (..., x, n, n, n, ..., n).
        # Turn it into (..., x, x + 1, x + 2, ...) */
        for j  in range( i+1, self.nSubsetSize ):
            self.combi[j] = self.combi[j - 1] + 1;
        return self.combi;
    # next - end
# class Combination - ned


def testPermutation():
    print( "testPermutation:" );
    permut = Permutation( 4 );
    instance = permut.first();
    while instance != []:
        print( instance );
        instance = permut.next();
# testPermutation - end

def testCombination():
    print( "testCombination:" );
    combi = Combination( 3, 5 );
    instance = combi.first();
    while instance != []:
        print( instance );
        instance = combi.next();
# testCombination - end


#testPermutation();
#testCombination();
