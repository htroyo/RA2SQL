RA2SQL is a small "compiler" developed for a compilers design course, it uses lex and yacc to parse relational algebra expressions and translates them to standard SQL.
The project was written in python 2.7 and uses the PLY package for lexer and parser.

INSTALLATION:
RA2SQL is just a python script so you have to install ply (in 2013 was used the current release for that time, but latest 3.8 release works) and you are ready to use the script

USAGE:
In order to use program you have to call it from a command line interface using the following syntax:
python  ra2sql [file1] [file2]

- if you don't pass any argument, ra2sql reads all input lines from stdin until you leave a blank line and press enter and generates SQL code and displays it in stdout
- if you pass a filename, it attempts to read and parse the file with relational algebra expressions and generates SQL code in a file with the same name and the .sql extension
- if you pass 2 filenames, it reads and parses the first file and attempts to save the result in a file named as the second argument