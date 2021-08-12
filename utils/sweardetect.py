def preprocessing(substring):
    """This function does the preprocessing for the KMP algorithm.
       It checks the previous occurence of each letter and maps it to a pi_table variable that contains a tuple for each letter
       Args:
            substring: A string that represents the needle that we will be looking for
       Return:
            pi_table: A list in which we mapped each letter in the substring and if it occured we give it its previous occurence otherwise it takes a 0 value"""
    pi_table = [('', 0)]#the first value is 0 to facilitate the kmp process
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
    """This function checks whether a word is a substring of the other through the KMP string matching algorithm
        This algorithm is faster than most string matching algorithm which allows the bot to be faster when checking for the swear word
        Args:
            haystack: The big string that we will be searching
            needle: The target that we will be seeking
        Return:
            A boolean to confirm whether a word is in the string or not"""
    if len(needle) > len(haystack):
        return False
    reference = preprocessing(needle)
    i = 0
    j = 0
    while i < len(haystack):
        while j != 0 and j<len(needle):
            letter_pair = reference[j + 1]
            if letter_pair[0] == haystack[i]:
                j += 1
                if j == len(needle):
                    #if we get to the end of the string
                    return True
                break
            else:
                #returns j to the value in which the letter previously occured
                j = reference[j][1]
        if j == 0 and reference[1][0] == haystack[i]:
            j += 1
        i += 1
    if j == len(needle):
        return True
    return False
