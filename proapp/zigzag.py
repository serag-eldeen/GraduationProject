import numpy as np

def zigzag(input):
    """
    Perform a zigzag scan of a 2D matrix.
    
    Arguments:
    - input: A 2D numpy array (matrix) of any size.
    
    Returns:
    - A 1D numpy array containing elements of the matrix in zigzag order.
    """
    
    # Initialize variables to keep track of the current position in the matrix
    h, v = 0, 0  # Horizontal and vertical indices
    vmax, hmax = input.shape  # Matrix dimensions
    
    # Initialize the output array with the total number of elements
    output = np.zeros(vmax * hmax)
    i = 0  # Index for the output array
    
    # Perform zigzag scan until the entire matrix is covered
    while (v < vmax) and (h < hmax):
        if (h + v) % 2 == 0:  # Moving up
            if v == 0 or h == hmax - 1:  # Edge cases
                output[i] = input[v, h]
                if h == hmax - 1:  # Last column, move down
                    v += 1
                else:  # Move right if not last column
                    h += 1
                i += 1
            else:  # Move up diagonally
                output[i] = input[v, h]
                v -= 1
                h += 1
                i += 1
        else:  # Moving down
            if h == 0 or v == vmax - 1:  # Edge cases
                output[i] = input[v, h]
                if v == vmax - 1:  # Last row, move right
                    h += 1
                else:  # Move down if not last row
                    v += 1
                i += 1
            else:  # Move down diagonally
                output[i] = input[v, h]
                v += 1
                h -= 1
                i += 1

        # Handle bottom-right element (end of matrix)
        if v == vmax - 1 and h == hmax - 1:
            output[i] = input[v, h]
            break

    return output


def inverse_zigzag(input, vmax, hmax):
    """
    Reconstruct a 2D matrix from a 1D zigzag-scanned array.
    
    Arguments:
    - input: A 1D numpy array containing elements in zigzag order.
    - vmax: The number of rows in the output 2D matrix.
    - hmax: The number of columns in the output 2D matrix.
    
    Returns:
    - A 2D numpy array (matrix) with dimensions (vmax, hmax).
    """
    
    # Initialize the output matrix and set current position
    output = np.zeros((vmax, hmax))
    h, v = 0, 0
    i = 0  # Index for the input array
    
    # Perform inverse zigzag scan to fill the matrix
    while (v < vmax) and (h < hmax):
        if (h + v) % 2 == 0:  # Moving up
            if v == 0 or h == hmax - 1:  # Edge cases
                output[v, h] = input[i]
                if h == hmax - 1:  # Last column, move down
                    v += 1
                else:  # Move right if not last column
                    h += 1
                i += 1
            else:  # Move up diagonally
                output[v, h] = input[i]
                v -= 1
                h += 1
                i += 1
        else:  # Moving down
            if h == 0 or v == vmax - 1:  # Edge cases
                output[v, h] = input[i]
                if v == vmax - 1:  # Last row, move right
                    h += 1
                else:  # Move down if not last row
                    v += 1
                i += 1
            else:  # Move down diagonally
                output[v, h] = input[i]
                v += 1
                h -= 1
                i += 1

        # Handle bottom-right element (end of matrix)
        if v == vmax - 1 and h == hmax - 1:
            output[v, h] = input[i]
            break

    return output
