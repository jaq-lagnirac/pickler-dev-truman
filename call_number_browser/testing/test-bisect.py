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

# scope resolution, default case
start_out_of_bounds = False
end_out_of_bounds = False

start_index = index - slice_one_sided
if start_index < 0: # check required to handle bottoming out
    start_index = 0
    start_out_of_bounds = True

# no top end check/reassignment needed, python handles it internally
end_index = index + slice_one_sided + 1 # +1 for half-open indexing [ )
if end_index > (len(test) - 1):
    end_out_of_bounds = True

print(test[start_index : end_index])