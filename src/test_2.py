from util.simplify import Data

file = 'W_1'
aaa=3
bbbb=4
locals()[file] = 5487
# locals()[file] = Data(123, file)

print(locals())
print(W_1)

# print(W_1.img)
# print(W_1.name)