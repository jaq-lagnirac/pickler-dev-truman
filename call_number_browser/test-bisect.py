from bisect import bisect # == bisect_right

test = list(range(0, 50, 2))

value = 25
slice_one_sided = 5
index = bisect(test, value)

print(index)

print(test)
test.insert(index, value)
print(test)
print(test[index])

start_index = index - slice_one_sided
if start_index < 0: # check required to handle bottoming out
    start_index = 0

# no top end check needed, python handles it internally
end_index = index + slice_one_sided + 1 # +1 for half-open indexing [ )

print(test[start_index : end_index])