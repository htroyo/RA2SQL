# coding=utf-8
import re
#lexer
#Heyner Troyo
#David Hine
#tabla de simbolos
simbolos = {}
#forma de cada entrada:
#nombre : [tipo, valor]
#declaracion de palabras reservadas, todas los nombres de las operaciones
error = 0
expresion = ""
reserved = {'select' : 'SELECT', 'project' : 'PROJECT', 'thetajoin' : 'TJOIN',
		'naturaljoin' : 'NJOIN', 'leftjoin' : 'LJOIN', 'rightjoin' : 'RJOIN', 'fulljoin' : 'FJOIN',
		'union' : 'UNION', 'intersect' : 'INTERSECT', 'except' : 'EXCEPT'}
tokens = ['PUNTO','NUM','STRING','OP_COMPARACION','OP_LOGICO','OP_NOT','PAREN', 'RPARAM', 'OP_ARITMETICO', 'PARENC', 'RPARAMC', 'IGUAL','COMA', 'ID']+list(reserved.values())

t_PUNTO = r'\.'
t_NUM = r'-?[0-9]+(\.[0-9]+)?' #No se convierte a tipo numero, las operaciones solo se transcriben al sql
t_OP_COMPARACION = r'\<\=|>\=|\!\=|\<|>|\<>'
t_OP_LOGICO =      r'\||\&'
t_OP_NOT = '\!'
t_PAREN    =      r'\('
t_RPARAM    =      r'\)'
t_OP_ARITMETICO =  r'\+|-|\*|/|%'
t_PARENC         =  r'\['
t_RPARAMC         =  r'\]'
t_IGUAL           =  r'\='
t_COMA            =  r','
def t_ID(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	#regla para asignar el tipo de palabra reservada si es necesario
	t.type = reserved.get(t.value.lower(),'ID')
	return t
t_STRING         =  r"'([^'])*((?<!\\)(\\\\)+|[^\\]?)'" #definicion de una string, ademas evita que escapen la comilla y la hilera quede invalida            

def t_error(t):
	global error
	error = 1
	print ("EEROR LEXICO")
	t.lexer.skip(1)

t_ignore = " \t"
	
def t_newline(t):
    r'\n'
    t.lexer.lineno += t.value.count("\n")

precedence = (
		('left', 'OP_ARITMETICO'),
        ('left', 'OP_COMPARACION'),
        ('left', 'OP_LOGICO'),
)

import ply.lex as lex
lex.lex()

str_token = re.compile(t_STRING)
	
def p_e1(p):
	'''exp : unexp
		| biexp'''
	global expresion
	global error
	p[0] = p[1]
	expresion = p[1][1]
	
def p_e2(p):
	'''exp : asign'''
	global expresion
	global error
	p[0] = p[1]
	expresion = "--asignacion: "+p[1]
	
def p_a1(p):
	'''asign : ID IGUAL unexp
		| ID IGUAL biexp'''
	global simbolos
	#caso similar al de exp, si es un id igual no hay que hacer nada
	#solo pasarlo a p[0]
	#cada consulta puede redefinir una variable
	#si una variable no es encontrada (o no coincide con el tipo de argumento esperado) no pasa nada
	#solo se escribe el nombre
	if error == 0:
		simbolos[p[1]] = ["exp",p[3][1]]
	p[0] = p[1]+" = "+p[3][1]
	
def p_a2(p):
	'''asign : ID IGUAL campos'''
	global simbolos
	#dos casos:
	#si len(p[3][1]) es 1 se guarda como un id
	#si es mayor a 1 se guarda como lista
	if len(p[3][1]) == 1:
		if error == 0:
			simbolos[p[1]] = ["id",p[3][1][0]]
		p[0] = p[1]+" = "+p[3][1][0]
	else:
		campos = p[3][1][0]
		for x in range(1,len(p[3][1])):
			campos = campos+","+p[3][1][x]
		if error == 0:
			simbolos[p[1]] = ["lista",campos]
		p[0] = p[1]+" = "+campos
		
def p_u1(p):
	'''unexp : op_select PAREN arg RPARAM'''
	#para el select
	if p[3][0] == "id":
		if p[3][1] in list(simbolos.keys()):
			if simbolos[p[3][1]][0] == "exp":
				arg = "("+simbolos[p[3][1]][1]+")"
			elif simbolos[p[3][1]][0] == "id":
				arg = simbolos[p[3][1]][1]
			else:
				arg = p[3][1]
		else:
			arg = p[3][1]
		exp = "SELECT * FROM "+arg
	else:
		exp = p[3][1]
	if p[1]:
		exp = exp + p[1]
	p[0] = ["unexp",exp]
	
def p_u2(p):
	'''unexp : PROJECT PARENC campos RPARAMC PAREN arg RPARAM'''
	#para el project
	total = len(p[3][1])
	if total == 1:
		if p[3][1][0] in list(simbolos.keys()) and simbolos[p[3][1][0]][0] in ["id","lista"]:
			campos = simbolos[p[3][1][0]][1]
		else:
			campos = p[3][1][0]
	else:
		campos = p[3][1][0]
		for i in range(1,total):
			campos = campos+", "+p[3][1][i]
	if p[6][0] == "id":
		if p[6][1] in list(simbolos.keys()):
			if simbolos[p[6][1]][0] == "exp":
				arg = "("+simbolos[p[6][1]][1]+")"
			elif simbolos[p[6][1]][0] == "exp":
				arg = simbolos[p[6][1]][1]
			else:
				arg = p[6][1]
		else:
			arg = p[6][1]
	else:
		arg = "("+p[6][1]+")"
	exp = "SELECT "+campos+" FROM "+arg
	p[0] = ["unexp",exp]
	
def p_c1(p):
	'''campos : ID COMA campos'''
	#lista de campos, para un project por ejemplo
	p[0] = ["campos",[p[1]]]
	p[0][1].extend(p[3][1])
	
def p_c2(p):
	'''campos : ID'''
	#un solo campo
	p[0] = ["campos",[p[1]]]
	
def p_ar1(p):
	'''arg : ID'''
	p[0] = ["id",p[1]]
	
def p_ar2(p):
	'''arg : unexp 
		| biexp'''
	#pasar a la raiz
	p[0] = ["exp",p[1][1]]
	
def p_sl(p):
	'''op_select : SELECT op_select_opc'''
	#declaracion del select, con un parametro opcional, la condicion
	p[0] = p[2]
	
def p_sl_opc(p):
	'''op_select_opc : PARENC condicion RPARAMC
		| '''
	#si len(p) es 1 significa que se usara select sin condicion
	#se puede checkear sin crear otra funcion para la regla
	if len(p) == 1:
		p[0] = ""
	else:
		p[0] = " WHERE "+p[2]
	
def p_cond1(p):
	'''condicion : PAREN condicion RPARAM'''
	#condiciones para select o join
	#reconocimiento de parentesis
	p[0] = "("+p[2]+")"

def p_cond2(p):
	'''condicion : condicion OP_LOGICO condicion'''
	#operaciones logicas and, or, etc
	p[0] = p[1]+p[2]+p[3]
	
def p_cond3(p):
	'''condicion : op_condicion'''
	#operando de la condicion
	p[0] = p[1]
	
def p_cond4(p):
	'''condicion : OP_NOT PAREN condicion RPARAM'''
	#negacion
	p[0] = "!("+p[3]+")"
	
def p_oc(p):
	'''op_condicion : cond_exp OP_COMPARACION cond_exp
		| cond_exp IGUAL cond_exp'''
	#el igual fue separado por ser un token usado tambien en la asignacion
	#pero la regla es la misma
	if (str_token.search(p[1]) or str_token.search(p[3])) and p[2] != "=":
		p_error(p)
	p[0] = p[1]+p[2]+p[3]
	
def p_ce1(p):
	'''cond_exp : PAREN cond_exp RPARAM'''
	#parentesis en las condiciones
	p[0] = "("+p[2]+")"
	
def p_ce2(p):
	'''cond_exp : cond_exp OP_ARITMETICO cond_exp'''
	#operaciones aritmeticas
	#no es necesario checkear la precedencia, las operaciones son devueltas a como vienen escritas
	#el DBMS es el encargado de evaluarlas
	if str_token.search(p[1]) or str_token.search(p[3]):
		p_error(p)
	p[0] = p[1]+p[2]+p[3]
	
def p_ce3(p):
	'''cond_exp : ID
		| NUM
		| STRING'''
	#devolver el token a la raiz
	p[0] = p[1]
	
def p_ce4(p):
	'''cond_exp : ID PUNTO ID'''
	#para operandos del tipo <tabla>.<campo>
	p[0] = p[1]+"."+p[3]
	
def p_b(p):
	'''biexp : op_binario PAREN arg COMA arg RPARAM'''
	#operaciones binarias
	arg1 = p[3][1]
	arg2 = p[5][1]
	if p[1][0] == "op_join_arg":
		if p[3][0] == "exp":
			arg1 = "("+arg1+")"
		else:
			if p[3][1] in list(simbolos.keys()):
				if simbolos[p[3][1]][0] == "exp":
					arg1 = "("+simbolos[p[3][1]][1]+")"
				elif simbolos[p[3][1]][0] == "id":
					arg1 = simbolos[p[3][1]][1]
		if p[5][0] == "exp":
			arg2 = "("+arg2+")"
		else:
			if p[5][1] in list(simbolos.keys()):
				if simbolos[p[5][1]][0] == "exp":
					arg2 = "("+simbolos[p[5][1]][1]+")"
				elif simbolos[p[5][1]][0] == "id":
					arg2 = simbolos[p[5][1]][1]
		exp = "SELECT * FROM "+arg1+" "+p[1][1]+" "+arg2+" ON "+p[1][2]
	else:
		if p[3][0] == "id":
			if p[3][1] in list(simbolos.keys()):
				if simbolos[p[3][1]][0] == "exp":
					arg1 = simbolos[p[3][1]][1]
				elif simbolos[p[3][1]][0] == "id":
					arg1 = "SELECT * FROM "+simbolos[p[3][1]][1]
			else:
				arg1 = "SELECT * FROM "+arg1
		else:
			if p[3][1] in list(simbolos.keys()):
				if simbolos[p[3][1]][0] == "exp":
					arg1 = simbolos[p[3][1]][1]
				elif simbolos[p[3][1]][0] == "id":
					arg1 = "SELECT * FROM "+simbolos[p[3][1]][1]
		if p[5][0] == "id":
			if p[5][1] in list(simbolos.keys()):
				if simbolos[p[5][1]][0] == "exp":
					arg2 = simbolos[p[5][1]][1]
				elif simbolos[p[5][1]][0] == "id":
					arg2 = "SELECT * FROM "+simbolos[p[5][1]][1]
			else:
				arg2 = "SELECT * FROM "+arg2
		else:
			if p[5][1] in list(simbolos.keys()):
				if simbolos[p[5][1]][0] == "exp":
					arg2 = simbolos[p[5][1]][1]
				elif simbolos[p[5][1]][0] == "id":
					arg2 = "SELECT * FROM "+simbolos[p[5][1]][1]
		exp = arg1+" "+p[1][1]+" "+arg2
	p[0] = ["biexp",exp]
	
def p_ob(p):
	'''op_binario : op_join_arg
		| binario'''
	#op_join_arg son los join que reciben condiciones
	#binario corresponde a los que solo reciben los operandos, como union o intersect
	p[0] = p[1]
	
def p_ob_arg(p):
	'''op_join_arg : join_func PARENC condicion RPARAMC'''
	#condicion del join
	p[0] = ["op_join_arg",p[1], p[3]]
	
def p_jf1(p):
	'''join_func : TJOIN'''
	p[0] = "INNER JOIN"
	
def p_jf2(p):
	'''join_func : LJOIN'''
	p[0] = "LEFT JOIN"
	
def p_jf3(p):
	'''join_func : RJOIN'''
	p[0] = "RIGHT JOIN"
	
def p_jf4(p):
	'''join_func : FJOIN'''
	p[0] = "FULL JOIN"
	
def p_bin1(p):
	'''binario : NJOIN'''
	p[0] = ["binario","NATURAL JOIN"]
	
def p_bin2(p):
	'''binario : UNION'''
	p[0] = ["binario","UNION"]
	
def p_bin3(p):
	'''binario : INTERSECT'''
	p[0] = ["binario","INTERSECT"]
	
def p_bin4(p):
	'''binario : EXCEPT'''
	p[0] = ["binario","EXCEPT"]

def p_error(p):
	global error
	print("ERROR SINTACTICO")
	error = 1
	
import ply.yacc as yacc
yacc.yacc()

import sys
import os.path
print("Relational algebra to SQL compiler (RA2SQL)")
print("v1.0.2")
resultado = ""
if len(sys.argv) < 2:
	while True:
		l = raw_input("Expresion: ")
		exp = l.strip()
		if exp:
			yacc.parse(exp)
			if error == 0:
				resultado = resultado+expresion+"\n"
			else:
				error = 0
		else:
			break
	print(resultado)
else:
	try:
		f = open(sys.argv[1],'rU')
	except:
		print("No se pudo abrir el archivo")
		exit()
	print('Leyendo archivo "'+sys.argv[1]+'"')
	for linea in f:
		l = linea.strip()
		if l:
			yacc.parse(l)
			if error == 0:
				resultado = resultado+expresion+"\n"
			else:
				error = 0
		else:
			pass
	f.close()
	if len(sys.argv) >= 3:
		salida = sys.argv[2]
	else:
		salida = os.path.splitext(os.path.basename(sys.argv[1]))[0]+".sql"
	if resultado:
		try:
			print("Guardando: "+salida)
			archivo = open(salida,"w")
			archivo.write(resultado)
			archivo.close()
			print("Archivo: "+salida+" guardado con exito")
		except:
			print("No se pudo escribir el archivo con el resultado")