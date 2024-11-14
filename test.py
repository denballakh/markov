from markov import (
    Rule,
    run,
    run_interactive,
    TooLongStringError,
    TooManyStepsError,
    parse_algo,
)


def test_algo(rules: list[Rule], *, inp: str, out: str, **kw: object) -> None:
    e = None
    out2 = None
    try:
        out2 = run(inp, rules)
    except (TooLongStringError, TooManyStepsError) as exc:
        e = exc
    if e is not None or out2 != out:
        info = ' '.join(f'{k}={v!r}' for k, v in kw.items())
        msg = ''
        msg += '!' * 40 + '\n'
        if info:
            msg += f'info: {info}\n'
        msg += f'input:    {inp}\n'
        msg += f'expected: {out}\n'
        if e is None:
            msg += f'got:      {out2}\n'
        else:
            msg += f'got:      {e!r}\n'
        print(msg)
        run_interactive(inp, rules)


binary2unary = parse_algo(
    '''
     1 -> 0|
    |0 -> 0|||
     0 ->
       ->.
    '''
)
for n in range(0, 100):
    test_algo(
        binary2unary,
        inp=bin(n)[2:],
        out='|' * n,
        name='2->1',
        n=n,
    )

unary2binary = parse_algo(
    '''
    0| ->  1
    1| -> |0
     | ->  0|
     0 ->. 0
     1 ->. 1
       ->. 0
    '''
)

for n in range(0, 100):
    test_algo(
        unary2binary,
        inp='|' * n,
        out=bin(n)[2:],
        name='1->2',
        n=n,
    )

print('ok!')
