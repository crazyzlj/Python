import numpy



DIR_PAIRS = [(0, 1),
             (-1, 1),
             (-1, 0),
             (-1, -1),
             (0, -1),
             (1, -1),
             (1, 0),
             (1, 1)]


def recursive_continuous_cells(numpyarray, row, col, idx):
    nrows, ncols = numpyarray.shape
    for r, c in DIR_PAIRS:
        new_row = row + r
        new_col = col + c
        if 0 <= new_row < nrows and 0 <= new_col < ncols:
            if numpyarray[new_row][new_col] == numpyarray[row][col]:
                if not [new_row, new_col] in idx:
                    idx.append([new_row, new_col])
                    recursive_continuous_cells(numpyarray, new_row, new_col, idx)


def get_continuous_count_cells_recursive(orgarray, orgv = 1):
    '''
        Counting the number of continuous cells of a single raster layer
        Recursive version
    :param orgarray:
    :param orgv:
    :return:
    '''
    newarray = numpy.copy(orgarray)
    rows, cols = numpy.shape(newarray)
    for i in range(rows):
        for j in range(cols):
            if newarray[i][j] == orgv:
                tempIdx = [[i, j]]
                recursive_continuous_cells(newarray, i, j, tempIdx)
                count = len(tempIdx)
                # print count
                for tmpR, tmpC in tempIdx:
                    newarray[tmpR][tmpC] = count
    return newarray


# def get_continuous_count_cells_iterative(orgarray, orgv = 1):
#     '''
#         Counting the number of continuous cells of a single raster layer
#         Iterative version
#     :param orgarray:
#     :param orgv:
#     :return:
#     '''


if __name__ == "__main__":
    org = [[1, 0, 0, 0, 0, 0],
           [0, 1, 0, 0, 1, 1],
           [0, 0, 1, 0, 1, 0],
           [0, 0, 0, 0, 1, 0],
           [0, 0, 0, 1, 0, 0]]

    print (get_continuous_count_cells_recursive(org))
