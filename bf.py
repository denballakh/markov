import markov


markov.MAX_LENGTH = 10_000
markov.MAX_STEPS = 0

def make_bf_program(code: str, input: str = '') -> str:
    allowed_chars = '+-<>[].,'
    code = ''.join(c for c in code if c in allowed_chars)
    input = ''.join(f'{bin(ord(c))[2:].zfill(8)}|' for c in input)
    return f'[input]{input}[/input][code][ip]{code}[/code][memory][mp][/memory][output][printed/sep][/output]'


def extract_output(s: str) -> str:
    assert '[output]' in s, s
    assert '[/output]' in s, s

    _, _, s = s.partition('[output]')
    s, _, _ = s.partition('[/output]')
    return bytes(int(x, 2) for x in s.replace('|', ' ').split()).decode()


bf_rules = markov.parse_algo(open('./bf.mv', 'rt', encoding='utf-8').read(), extensions=True)


def test_bf(code: str, inp: str, out: str) -> None:
    print(code)
    s = make_bf_program(code, inp)
    res = markov.run(s, bf_rules)
    res = extract_output(res)
    assert res == out, (res, out)

# These programs are taken from https://esolangs.org/wiki/Brainfuck:

test_bf(
    '''
        Calculate the value 256 and test if it's zero
        If the interpreter errors on overflow this is where it'll happen
        ++++++++[>++++++++<-]>[<++++>-]
        +<[>-<
            Not zero so multiply by 256 again to get 65536
            [>++++<-]>[<++++++++>-]<[>++++++++<-]
            +>[>
                # Print "32"
                ++++++++++[>+++++<-]>+.-.[-]<
            <[-]<->] <[>>
                # Print "16"
                +++++++[>+++++++<-]>.+++++.[-]<
        <<-]] >[>
            # Print "8"
            ++++++++[>+++++++<-]>.[-]<
        <-]<
        # Print " bit cells\\n"
        +++++++++++[>+++>+++++++++>+++++++++>+<<<<-]>-.>-.+++++++.+++++++++++.<.
        >>.++.+++++++..<-.>>-.
        Clean up used cells
        [[-]<]
    ''',
    '',
    '8 bit cells\n',
)
test_bf(
    '''
    ++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>
    >.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>
    +.>++.
    ''',
    '',
    'Hello World!\n',
)

test_bf(
    '''
    +++++++++++[>++++++>+++++++++>++++++++>++++>+++>+<
    <<<<<-]>++++++.>++.+++++++..+++.>>.>-.<<-.<.+++.--
    ----.--------.>>>+.>-.
    ''',
    '',
    'Hello, World!\n',
)

test_bf(
    '''
    >++++++++[-<+++++++++>]<.>>+>-[+]++>++>+++[>[->+++
    <<+++>]<<]>-----.>->+++..+++.>-.<<+[>[+>+]>>]<----
    ----------.>>.+++.------.--------.>+.>+.
    ''',
    '',
    'Hello World!\n',
)

# this one
test_bf(
    '''
    --<-<<+[+[<+>--->->->-<<<]>]<<--.<++++++.<<-..<<.<
    +.>>.>>.<<<.+++.>>.>>-.<<<+.
    ''',
    '',
    'Hello, World!\n',
)

# around 1 minute to complete
test_bf(
    '''
    +[-->-[>>+>-----<<]<--<---]>-.>>>+.>>..+++[.>]<<<<
    .+++.------.<<-.>>>>+.
    ''',
    '',
    'Hello, World!',
)
