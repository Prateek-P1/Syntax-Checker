# main_prog.py
from parser_rules import parser, lexer, interpreter

def main():
    print("Enter your code (type 'end' on a new line to finish):")
    code_lines = []
    while True:
        try:
            line = input('> ')
            if line.strip() == 'end':
                break
            code_lines.append(line)
        except EOFError:
            break

    code = '\n'.join(code_lines)
    if code.strip():
        result = parser.parse(code, lexer=lexer)
        if result is not None:
            interpreter.execute(result)
            if not interpreter.had_error:
                print("Parsing successful!")
            else:
                print("Execution completed with errors.")
        else:
            print("Parsing failed.")

if __name__ == "__main__":
    main()