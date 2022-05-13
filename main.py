def length_of_longest_substring(s:str):
    lenght = len(s)
    steps_from_start = 0
    current_index = {}
    max_steps = 0
    for j in range(lenght):
        if s[j] in current_index:
            steps_from_start = max(current_index[s[j]], steps_from_start)
        max_steps = max(max_steps, j - steps_from_start + 1)
        current_index[s[j]] = j + 1
    return max_steps

string = 'abcabcd'

print(f"Length of longest substring without repetitions in string {string} is {length_of_longest_substring(string)}")




