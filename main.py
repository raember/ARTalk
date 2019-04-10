from artalk.parser import Parser

if __name__ == '__main__':
    with open('in.txt', 'r') as codefile:
        content = codefile.read()
    for code in Parser().parse(content):
        print()
        print(f"[{code.title}]")
        for block in code.blocks:
            print(f"{block.first} {block.second}: {block.to_human_readable()}")
