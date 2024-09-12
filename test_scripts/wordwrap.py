# def wordwrap(txt, limit):
#     txtlist = txt.split()
#     l = [''] * 10
#     line_length = 0
#     index = 0
#     for x in txtlist:
#         string_to_add = f'{x} '
#         line_length += len(string_to_add)
#         if line_length < limit:
#             print(f'line length less than limit {line_length}<{limit}')
#             l[index] += string_to_add
#         else:
#             print(f'line length greater than limit {line_length}>{limit}')
#             line_length = 0
#             l[index] = l[index][:-1] # takes off trailing space
#             index += 1
#             l[index] += string_to_add
#         print(x, len(string_to_add), line_length, index, l)
#     return l

def wordwrap(txt, line_length_limit, num_of_lines):
    txtlist = txt.split()
    return_list = [''] * num_of_lines # redundant here if self growing, would only need ['']
    
    index = 0
    for word in txtlist:
        spaced_string = f'{word} '
        new_word_length = len(spaced_string)
        current_line_length = len(return_list[index])
        possible_length = current_line_length + new_word_length
        if possible_length < line_length_limit:
            return_list[index] += spaced_string
        else:
            index += 1
            return_list[index] += spaced_string # implement self-growing list here (return_list += [spaced_string])
    return return_list

txt = 'hello world and all      of the people in the world.\nwe love it so much'
l = wordwrap(txt, 20, 10)
print(l)
print('')
for x in l:
    print(x, len(x))