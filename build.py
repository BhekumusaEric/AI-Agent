def next_states(s):
    results = []
    seen = set()

    # Rule 1: If string ends with 'I', append 'U'
    if s.endswith("I"):
        new_s = s + "U"
        if new_s not in seen:
            results.append(new_s)
            seen.add(new_s)

    # Rule 2: If string starts with 'M', duplicate everything after 'M'
    if s.startswith("M"):
        suffix = s[1:]
        new_s = "M" + suffix + suffix
        if new_s not in seen:
            results.append(new_s)
            seen.add(new_s)

    # Rule 3: Replace "III" with "U"
    idx = 0
    while "III" in s[idx:]:
        i = s.index("III", idx)
        new_s = s[:i] + "U" + s[i+3:]
        if new_s not in seen:
            results.append(new_s)
            seen.add(new_s)
        idx = i + 1  # Move past this point to find next occurrence

    # Rule 4: Remove "UU"
    idx = 0
    while "UU" in s[idx:]:
        i = s.index("UU", idx)
        new_s = s[:i] + s[i+2:]
        if new_s not in seen:
            results.append(new_s)
            seen.add(new_s)
        idx = i + 1

    return results
