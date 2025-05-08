"""
MIU System Module

This module implements the MIU formal system as described in Douglas Hofstadter's
'Gödel, Escher, Bach: An Eternal Golden Braid'.

The MIU system consists of strings of M, I, and U characters, with transformation rules
that allow generating new strings from existing ones.
"""

def next_states(s):
    """
    Generate all possible next states from the current state by applying MIU system rules.
    
    Rules:
    1. If a string ends in "I," you may append a "U" at the end: x I → x IU
    2. If a string starts with "M," you can duplicate everything after "M": M x → M x x
    3. If the string contains "III," you can replace it with a "U": x III y → x U y
    4. If the string contains "UU," you can remove it entirely: x UU y → x y
    
    Args:
        s (str): The current state (a string of M, I, and U characters)
        
    Returns:
        list: A list of all possible next states, with duplicates removed
    """
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

def is_valid_miu_string(s):
    """
    Check if a string is a valid MIU string.
    
    Args:
        s (str): The string to check
        
    Returns:
        bool: True if the string contains only M, I, and U characters and starts with M
    """
    if not s:
        return False
    if not s.startswith('M'):
        return False
    return all(c in 'MIU' for c in s)

def apply_rule(s, rule_num, occurrence=0):
    """
    Apply a specific MIU rule to a string.
    
    Args:
        s (str): The string to transform
        rule_num (int): The rule number (1-4)
        occurrence (int): Which occurrence of the pattern to transform (0-indexed)
        
    Returns:
        str: The transformed string, or None if the rule cannot be applied
    """
    if rule_num == 1:
        if s.endswith("I"):
            return s + "U"
    elif rule_num == 2:
        if s.startswith("M"):
            suffix = s[1:]
            return "M" + suffix + suffix
    elif rule_num == 3:
        occurrences = []
        idx = 0
        while "III" in s[idx:]:
            i = s.index("III", idx)
            occurrences.append(i)
            idx = i + 1
        
        if occurrence < len(occurrences):
            i = occurrences[occurrence]
            return s[:i] + "U" + s[i+3:]
    elif rule_num == 4:
        occurrences = []
        idx = 0
        while "UU" in s[idx:]:
            i = s.index("UU", idx)
            occurrences.append(i)
            idx = i + 1
        
        if occurrence < len(occurrences):
            i = occurrences[occurrence]
            return s[:i] + s[i+2:]
    
    return None  # Rule cannot be applied
