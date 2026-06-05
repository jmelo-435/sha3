#   
#
#Scrambling

class Scrambler():

    def __init__(self,state_array):
        self.state_array = state_array

#
#     The Five Step Mappings(Need to be executed in the order theta - rho - pi - chi - iota)
#     
#       - Theta
#            - XOR each bit in the state with the parities of two columns in the array
#                - for a bit with coordinate [x`,y`,z`] in the Sate Array, the x coordinate of one of the columns is (x`-1) % 5, 
#            with the same z, and the x coordinate of the second column is (x` + 1) % 5 , with z equals (z` - 1) % 64. - FIPS PUB 202, pag. 12.
#
    def theta(self):
        
        def return_column(x_coordinate,z_coordinate):
            column = []
            slice = self.state_array[z_coordinate]
            
            for row in slice:
                column.append(row[x_coordinate])

            return column 

        
        z = 0
        for slice in self.state_array:
            for row in slice:
                x = 0
                for bit in row:
                    result = 0
                    one_column = return_column((x-1)%5 , z)
                    for one_bit in one_column:
                        result ^= one_bit
                    
                    other_column = return_column((x+1)%5 , (z-1)%64)
                    for other_bit in other_column:
                        result ^= other_bit
                    
                    result ^= bit
                    row[x] = result                   
                    x+=1
            z+= 1

        return self



#       - Rho
#           - The effect of ρ is to rotate the bits of each lane by a length, called the offset, 
#       which depends on the fixed x and y coordinates of the lane. - FIPS PUB 202, pag. 12. 
#       The offset can be calculated on execution time or recovered from a pre-calculated 
#       table for the 1600 bits state array case. 


    def rho(self):
        
        ROTATION_OFFSETS = [
            [0, 36, 3, 41, 18],
            [1, 44, 10, 45, 2],
            [62, 6, 43, 15, 61],
            [28, 55, 25, 21, 56],
            [27, 20, 39, 8, 14]
        ]
        array = self.state_array
        
        def rotate(list, offset):
            return list[offset:] + list[:offset]
        
        x = 0
        lane = []
        while x < 5:
            y=0
            while y < 5:
                for slice in array:
                    lane.append(slice[x][y])
                
                rotated_lane = rotate(lane, ROTATION_OFFSETS[x][y])
                
                z=0
                for slice in array:
                    self.state_array[z][x][y] = rotated_lane[z]
                    z+=1
                
                lane = []
                y+=1
            x+=1
        
        return self
        
#       
#       - Pi
#           - "Rotate" the bits on each lane, by applying a function on its x and y coordinates:
#       A′[x, y, z]= A[(x + 3y)% 5, x, z]. - FIPS PUB 202, pag. 14.
    def pi(self):
        rows, columns, lanes = 5,5,64
        buffer = [[[0 for _ in range(rows)] for _ in range(columns)] for _ in range(lanes)]
        
        x = 0
        while x < 5:
            y=0
            while y < 5:
                z=0
                while z < 64 :
                    buffer[z][x][y] = self.state_array[z][(x + (3 * y)) % 5][x]
                    z+=1
                y+=1
            x+=1

        self.state_array = buffer

        return self


#
#       - Chi
#           - Chi is the only non-linear step. It operates on each row independently combining bits using
#       AND, NOT, and XOR operations. 
#       A′ [x, y, z] = A[x, y, z] ⊕ ((A[(x+1) mod 5, y, z] ⊕ 1) ⋅ A[(x+2) mod 5, y, z]).  - FIPS PUB 202, pag. 15.

#               -  inverts the bits of the neighbouring lane breaking linear expectations.
#               -  creates (^row[(x+1)%5] & row[(x+2)%5]) conditional dependency
#       on two neighbours. A bit is returned only if both conditions are met.    
#               -  XOR with the original lane (⊕ row[x]) injects this conditional mask
#       to back into the state but output cannot be recomputed as a linear function
#       of the inputs.

    def chi(self):
        
        rows, columns, lanes = 5,5,64
        buffer = [[[0 for _ in range(rows)] for _ in range(columns)] for _ in range(lanes)]
        
        x = 0
        while x < 5:
            y=0
            while y < 5:
                z=0
                while z < 64 :
                    buffer[z][x][y] = self.state_array[z][x][y] ^ ((self.state_array[z][(x + 1) % 5][y] ^ 1) & (self.state_array[z][(x+2) % 5][y])) 
                    z+=1
                y+=1
            x+=1

        self.state_array = buffer

        return self

#       
#       -  Iota - FIPS PUB 202, pag. 15.
#           - Injects a round constant to prevent linear evolution or cycles on the 24 rounds.
#               - Again , this constants can be calculated on execution time or recovered from a pre-
#           calculated list. The constant is XOErd on the (0,0) lane each round.
    def iota(self,round):
        ROUND_CONSTANTS = [
                0x0000000000000001,
                0x0000000000008082,
                0x800000000000808A,
                0x8000000080008000,
                0x000000000000808B,
                0x0000000080000001,
                0x8000000080008081,
                0x8000000000008009,
                0x000000000000008A,
                0x0000000000000088,
                0x0000000080008009,
                0x000000008000000A,
                0x000000008000808B,
                0x800000000000008B,
                0x8000000000008089,
                0x8000000000008003,
                0x8000000000008002,
                0x8000000000000080,
                0x000000000000800A,
                0x800000008000000A,
                0x8000000080008081,
                0x8000000000008080,
                0x0000000080000001,
                0x8000000080008008
            ]
        
        lane_zeroZero = []

        def to_bitArray(value):
            bit_string = format(value, '064b')
            return [int(bit) for bit in bit_string]
        
        for slice in self.state_array:
            lane_zeroZero.append(slice[0][0])
        
        result = [a ^ b for a, b in zip(lane_zeroZero, to_bitArray(ROUND_CONSTANTS[round]))]

        z= 0

        for slice in self.state_array :
            slice[0][0] = result[z]
            z+=1

        return self
