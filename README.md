# shape_grammar_compiler
# As a principle verification of the shape grammar,
# this program roughly realizes the text definition 
# and rule derivation of shape. 
# Both shape and labels adopt absolute coordinates, 
# without coordinate transformation, and follow-up implementation.
# author  :   Chen Guojun진국군
# Email   :   horsetery@gmail.com
# usage   :   python shape_grammar_compiler_v2.2.py test.sg test.svg
# test.sg
# Is a custom shape grammar language file
# Convention:
# v is the vertex, e is the edge, s is the shape, and p is the production
# Here is a simple example:
''' 
v0 = (0,0)
v1 = (100,0)
e0 = (v0,v1)
s0 = (v0,e0)
s1 = (e0)
p0 = (s0,s1)
''' 
# This will generate a file named test.svg in the current folder
