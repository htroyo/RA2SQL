SELECT * FROM tabla
SELECT id, nombre, telefono FROM contacto
SELECT carnet, nombre FROM (SELECT * FROM estudiante WHERE nota>90)
--asignacion: a = SELECT * FROM emp WHERE salario>500000&departamento=5|departamento=2
--asignacion: b = SELECT * FROM dept
SELECT * FROM emp WHERE salario>500000&departamento=5|departamento=2 NATURAL JOIN SELECT * FROM dept
SELECT * FROM (SELECT * FROM emp WHERE salario>500000&departamento=5|departamento=2) INNER JOIN (SELECT * FROM dept) ON id=num
--asignacion: tabla_3 = SELECT * FROM (SELECT * FROM emp WHERE salario>500000&departamento=5|departamento=2) LEFT JOIN (SELECT * FROM dept) ON a.salario<b.salario
--asignacion: campos = salario,nombre,apellido,departamento
SELECT salario,nombre,apellido,departamento FROM (SELECT * FROM emp WHERE salario>500000&departamento=5|departamento=2 EXCEPT SELECT * FROM (SELECT * FROM emp WHERE salario>500000&departamento=5|departamento=2) LEFT JOIN (SELECT * FROM dept) ON a.salario<b.salario)
SELECT * FROM tabla3 WHERE campo='string con \r\ncaracteres especiales\\' INTERSECT SELECT * FROM notas
