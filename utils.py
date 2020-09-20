def preprocessing(substring):
    pi_table = [0]
    first_occurrence = {}
    for i in range(len(substring)):
        letter = substring[i]
        if letter not in first_occurrence:
            first_occurrence[letter] = i + 1
            pi_table.append((letter, 0))
        else:
            pi_table.append((letter, first_occurrence[letter]))
    return pi_table


def is_substring(haystack, needle):
    if len(needle) > len(haystack):
        return False
    reference = preprocessing(needle)
    i = 0
    j = 0
    while i < len(haystack):
        while j != 0:
            letter_pair = reference[j + 1]
            if letter_pair[0] == haystack[i]:
                j += 1
                if j == len(needle):
                    return True
                break
            else:
                j = reference[j][1]
        if j == 0 and reference[1][0] == haystack[i]:
            j += 1
        i += 1
    if j == len(needle):
        return True
    return False
