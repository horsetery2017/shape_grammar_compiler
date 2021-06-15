#coding:utf-8
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
v2 = (200,100)
e0 = (v0,v1)
e1 = (v1,v2)
s0 = (v0,e0,e1)
s1 = (e0,e1)
p0 = (s0,s1)
''' 
# This will generate a file named test.svg in the current folder


import ply.lex as lex
import ply.yacc as yacc
import svgwrite
import re
import sys
tokens=( 
    'SHAPE_ID',
    'EDGE_ID',
    'VERTEX_ID',
    'PRODUCTION_ID',
    'LPAREN',
    'RPAREN',
    'EQUAL',
    'NUMBER',
    'COMMA',
    'LABEL_SW',
    'DERIVE',
)
t_VERTEX_ID= r'v\d+'
t_SHAPE_ID = r's\d+'
t_EDGE_ID = r'e\d+'
t_PRODUCTION_ID = r'p\d+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUAL = r'='
t_COMMA = r','
t_DERIVE = r'->'

def t_LABEL_SW(t):
    r'[tf]'
    return t

def t_NUMBER(t):
    r'\d+'
    # print(t)
    t.value = int(t.value)    
    return t
# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
lexer =lex.lex()

#Error rule for syntax errors
def p_error(p):
    print("------error-v------")
    print(p)
    print("Syntax error in input!")    
    print("------error-------")

l = '''v0 = (10,10)
v1 = (110,10)
v2 = (110,110)
v3 = (10,110)

v4 = (60,10)
v5 = (110,60)
v6 = (60,110)
v7 = (10,60)

v8 = (60,10)
v9 = (85,35)

e0 = (v0,v1)
e1 = (v1,v2)
e2 = (v2,v3)
e3 = (v3,v0)

e4 = (v4,v5)
e5 = (v5,v6)
e6 = (v6,v7)
e7 = (v7,v4)

s0 = (v8,e0,e1,e2,e3)
s1 = (v9,e4,e5,e6,e7)
s2 = (e0,e1,e2,e3)

p0 = (s0,s1)
p1 = (s1,s2)'''

vertexes = {}
edges = {}
shapes = {}
productions = {}

dwg = svgwrite.Drawing(sys.argv[2], profile='tiny')
'''
expr : VERTEX_ID EQUAL item
     | EDGE_ID EQUAL item
     | SHAPE_ID EQUAL item
     | PRODUCTION_ID EQUAL item

item : vertex
     | edge
     | shape
     | production

vertex : LPAREN NUMBER COMMA NUMBER RPAREN
edge : LPAREN VERTEX_ID COMMA VERTEX_ID RPAREN
shape : LPAREN edges RPAREN
edges : edges COMMA EDGE_ID
      | EDGE_ID
production : LPAREN SHAPE_ID COMMA SHAPE_ID RPAREN
'''

draw_label_vertexes = []
draw_vertexes = []
draw_edges = []
current_shapes = ['s0']

def p_expr_xid(p):
    '''expr : VERTEX_ID EQUAL item
     | EDGE_ID EQUAL item
     | SHAPE_ID EQUAL item
     | PRODUCTION_ID EQUAL item'''
    if p[1][:1] == 'v':
        vertexes[p[1]] = p[3]
    elif p[1][:1] == 'e':
        edges[p[1]] = p[3]
    elif p[1][:1] == 's':
        shapes[p[1]] = p[3]
    elif p[1][:1] == 'p':
        productions[p[1]] = p[3]
    p[0] = "%s%s%s"%(p[1],p[2],p[3])
    print(vertexes)
    print(edges)
    print(shapes)
    print(productions)

    for s in shapes.items():
        k,v = s
        o=[]
        shapes[k] = tuple(flat_shape(v,o))

    
def apply_production(productions):
    for s in current_shapes:
        for p in productions.items():
            k,v = p
            if s == v[0]:
                if shapes[s][0][:1] == 'v':
                    current_shapes.append(v[1])

def draw_shape_(current_shapes):
    index = -1

    for is_,s in enumerate(current_shapes):
        cl_vertex= (0,0)
        l_vertex = (0,0)
        if is_>0:
            fs = shapes[current_shapes[is_ - 1]][0]
            if fs[:1] == 'v':
                l_vertex = (vertexes[fs][0],vertexes[fs][1])
                dwg.add(dwg.circle(l_vertex,3))
        else:
            l_vertex = (0,0)
            cl_vertex= (0,0)

        if shapes[s][0][:1]=='v' and is_>0:
            cl_vertex = (vertexes[shapes[s][0]][0],vertexes[shapes[s][0]][1])
            # l_pos = (l_vertex[0] + cl_vertex[0],l_vertex[1] + cl_vertex[1])
            dwg.add(dwg.circle(cl_vertex,3))

        for k,v in enumerate(shapes[s]):
            if v[:1] != 'v':
                draw_edges.append(
                    (
                ( vertexes[edges[v][0]][0] ,  vertexes[edges[v][0]][1] ),
                (vertexes[edges[v][1]][0] ,  vertexes[edges[v][1]][1] )
                    )
                )

def draw_edge_with_label(draw_edges):
    for ie,es in enumerate(draw_edges):
        s_vertex = es[0]
        e_vertex = es[1]
        print(s_vertex)
        print(e_vertex)
        dwg.add(dwg.line(s_vertex,e_vertex,stroke=svgwrite.rgb(10, 10, 16, '%')))
    dwg.save()


def flat_shape(s,o):
    '''s:string, o:list
    This function flattens the shape item data'''
    for i in s:
        if type(i) == str:
            o.append(i)
        else:
            flat_shape(i,o)
    return o
def p_item(p):
    '''item : vertex
     | edge
     | shape
     | production'''
    p[0] = p[1]
    print("item:")
    print(p[0])

def p_vertex(p):
    '''vertex : LPAREN NUMBER COMMA NUMBER RPAREN'''
    p[0] = (p[2],p[4])
    print('vertex:')
    print(p[0])

def p_edge(p):
    '''edge : LPAREN VERTEX_ID COMMA VERTEX_ID RPAREN'''
    # p[0] = ( vertexes[p[2]] ,vertexes[p[4]])
    p[0] = (p[2],p[4])
    print("edge:")
    print(p[0])

def p_shape(p):
    '''shape : LPAREN edges RPAREN
             | LPAREN VERTEX_ID COMMA edges RPAREN'''
    if len(p)>4:    
        # p[0] = (vertexes[p[2]],p[4])
        p[0] = (p[2],p[4])
    else:
        p[0] = (p[2])
    print("shape:")
    print(p[0])

def p_edges(p):
    '''edges : edges COMMA EDGE_ID
      | EDGE_ID'''
    if len(p)>3:
        p[0] = (p[1],p[3])
    else:
        p[0] = (p[1])
    print("edges:")
    print(p[0])

def p_production(p):
    '''production : LPAREN SHAPE_ID COMMA SHAPE_ID RPAREN'''
    p[0] =  (p[2] , p[4])
    print("production:")
    print(p[0])


parser = yacc.yacc()
num = 0
f = open(sys.argv[1])
l = "".join(f.readlines())
l = l.split("\n")
while True:
    if num >= len(l):
        dwg.save()
        break
    print(l[num])
    result = yacc.parse(l[num])
    num+=1

def get_s(s,o):
    '''s:string, o:list'''
    for i in s:
        if type(i) == str:
            o.append(i)
        else:
            get_s(i,o)
    return o

while True:
    apply_production(productions)
    print(current_shapes)
    draw_shape_(current_shapes)
    print(draw_edges)
    draw_edge_with_label(draw_edges)
    if shapes[current_shapes[len(current_shapes)-1]][0][:1] != 'v':
        break
