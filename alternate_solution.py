def next_states(s):
    rule1 = lambda s: [s + 'U'] if s.endswith('I') else []
    rule2 = lambda s: [s[0] + s[1:] * 2] if s.startswith('M') else []
    rule3 = lambda s: [s[:i] + 'U' + s[i + 3:] for i in range(len(s)) if s[i:i + 3] == 'III']
    rule4 = lambda s: [s[:i] + s[i + 2:] for i in range(len(s)) if s[i:i + 2] == 'UU']
    return [*dict.fromkeys(r for rule in (rule1, rule2, rule3, rule4) for r in rule(s))]
