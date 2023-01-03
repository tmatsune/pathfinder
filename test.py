
ROW = 5
COL = 6
grid = []
for i in range(ROW):
    grid.append([])
    for j in range(COL):
        grid[i].append(j+i)
print(grid)
print(grid[2][3])

open_set = []
open_set.append((1, 2, 3))
print(open_set[0][2])
