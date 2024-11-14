from __future__ import annotations
import typing as t

import dataclasses

# some safeguards:
MAX_LENGTH: int = 1_000  # 0 means no limit
MAX_STEPS: int = 10_000  # 0 means no limit

#
TERMINATED_NO_MATCHING_RULE: int = -1
TERMINATED_TOO_LONG_STRING: int = -2
TERMINATED_TOO_MANY_STEPS: int = -3

termination_reasons = {
    TERMINATED_NO_MATCHING_RULE: 'no matching rule',
    TERMINATED_TOO_LONG_STRING: 'too long string',
    TERMINATED_TOO_MANY_STEPS: 'too many steps',
}


class TooLongStringError(Exception): ...


class TooManyStepsError(Exception): ...


@dataclasses.dataclass(slots=True)
class Rule:
    before: str
    after: str
    terminating: bool = False

    def __str__(self) -> str:
        return f'{self.before} ->{"." if self.terminating else ""} {self.after}'

    @classmethod
    def from_line(cls, line: str) -> Rule:
        if '->.' in line:
            before, _, after = line.partition('->.')
            return Rule(before.strip(), after.strip(), terminating=True)
        elif '->' in line:
            before, _, after = line.partition('->')
            return Rule(before.strip(), after.strip())
        else:
            raise Exception(f'invalid rule: {line!r}')


@dataclasses.dataclass
class State:
    string: str
    rules: list[Rule]
    steps: int = 0

    def step(self) -> int:
        """
        returns:
            >=0 - applied rule index
            <0 - some other termination reason
        """
        if MAX_LENGTH and len(self.string) > MAX_LENGTH:
            return TERMINATED_TOO_LONG_STRING
        if MAX_STEPS and self.steps >= MAX_STEPS:
            return TERMINATED_TOO_MANY_STEPS
        for idx, rule in enumerate(self.rules):
            if rule.before in self.string:
                self.string = self.string.replace(rule.before, rule.after, 1)
                self.steps += 1
                return idx
        else:
            # no rule matched
            return TERMINATED_NO_MATCHING_RULE

    def run(self) -> None:
        while True:
            idx = self.step()
            if idx < 0:
                if idx == TERMINATED_NO_MATCHING_RULE:
                    break  # legit ending condition
                if idx == TERMINATED_TOO_LONG_STRING:
                    raise TooLongStringError(self.string)
                if idx == TERMINATED_TOO_MANY_STEPS:
                    raise TooManyStepsError(self.steps)
                raise Exception(f'unknown termination result: {idx}')
            elif self.rules[idx].terminating:
                break  # legit ending condition
            else:
                pass  # keep going


def run(
    start: str,
    rules: list[Rule],
) -> str:
    s = State(
        string=start,
        rules=rules,
    )
    s.run()
    return s.string


def run_interactive(start: str, rules: list[Rule]) -> str:
    import colorama as col

    col.init()
    fg = col.Fore
    bg = col.Back
    reset = fg.RESET + bg.RESET

    visited_states = set()

    def fmt_rule(rule: Rule) -> str:
        s = ''
        s += bg.RED + fg.BLACK
        s += rule.before
        s += reset
        s += ' ->'
        if rule.terminating:
            s += fg.LIGHTRED_EX
            s += '.'
            s += reset
        s += ' '
        s += bg.GREEN + fg.BLACK
        s += rule.after
        s += reset
        return s

    print('Rules:')
    for idx, rule in enumerate(rules):
        print(f'{idx:3}: {fmt_rule(rule)}')
    print()
    s = State(
        string=start,
        rules=rules,
    )
    while True:
        if s.string in visited_states:
            print(f'already were in this state. Aborting...')
            1/0
        visited_states.add(s.string)

        before = s.string
        idx = s.step()
        if idx < 0:
            print(f'terminated: {termination_reasons[idx]}')
            if idx == TERMINATED_NO_MATCHING_RULE:
                break
            if idx == TERMINATED_TOO_LONG_STRING:
                raise TooLongStringError
            if idx == TERMINATED_TOO_MANY_STEPS:
                raise TooManyStepsError
            raise Exception(f'unknown termination result: {idx}')
        else:
            rule = s.rules[idx]
            after = s.string

            def fmt_string(x: str, y: str, z: str, col: str) -> str:
                try:
                    highlight = _h # some function that takes a string and returns the same string with ANSI codes
                except NameError:
                    highlight = lambda s: s

                n = len(x) + len(y) + len(z)
                s = ''
                s += '['
                s += fg.CYAN
                s += f'{n}'
                s += reset
                s += ']'
                s += ' '
                s += fg.LIGHTBLUE_EX
                s += '>'
                s += reset
                s += highlight(x)
                s += col
                s += y
                s += reset
                s += highlight(z)
                s += fg.LIGHTBLUE_EX
                s += '<'
                s += reset
                return s

            i = before.index(rule.before)
            x, y, z = before.partition(rule.before)
            print(f'before: {fmt_string(x, y, z, fg.BLACK + bg.RED)}')

            x, y, z = after[:i], after[i : i + len(rule.after)], after[i + len(rule.after) :]
            print(f'after:  {fmt_string(x, y, z, fg.BLACK + bg.GREEN)}')
            # print(f'after:  [{fg.CYAN}{len(after):3}{reset}] {x}{bg.GREEN}{fg.BLACK}{y}{reset}{z}')

            print(f'rule: {idx:3}: {fmt_rule(rule)}')
            if s.rules[idx].terminating:
                print('rule is terminating...')
                break
        input()
    input()
    return s.string


def parse_algo(s: str, extensions: bool = False) -> list[Rule]:
    res: list[Rule] = []
    dollar_items: list[str] = []
    for idx, line in enumerate(s.splitlines(), start=1):
        line, _, _ = line.partition('#')
        line = line.strip()
        if not line:
            continue
        if extensions:
            if line.startswith('$$'):
                dollar_items = line.lstrip('$').split()
            elif '$' in line:
                for dollar_item in dollar_items:
                    res.append(Rule.from_line(line.replace('$', dollar_item)))
            else:
                res.append(Rule.from_line(line))
        else:
            res.append(Rule.from_line(line))
    return res

