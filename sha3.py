from .scrambler import Scrambler

# Keccak [c]
# https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf

class Sha_v3():
    
    #https://crypto.stackexchange.com/questions/47831/sha-3-block-sizes-bitrate-calculation
    size = 1600
    rate = 576
    capacity = size - rate
    rows, columns, lanes = 5,5,64
    number_of_rounds = 24
    seed = "0" * rate
    input_blocks =[]
    state = [0] * size
    state_array = []
    bit_string = None
#Ingestion
#   
#   Convertion to bits
#       
    def __init__(self):
        self.state_array = [[[0 for _ in range(self.rows)] for _ in range(self.columns)] for _ in range(self.lanes)]

    def __to_bits(self,string):
        if string == None:
            raise Exception("Can not convert null.")
        bit_string = "".join(format(ord(x), '08b') for x in string)
        self.bit_string = bit_string
        return self
#
#
#   Padding
#
#       - "... the “0” bit is either omitted or repeated as
#   necessary in order to produce an output string of the 
#   desired length." - FIPS PUB 202, pag. 19.
#   

    def __pad(self):
        if self.bit_string == None:
            raise Exception("Can not pad null.")
        if len(self.bit_string) % self.rate == 0:
            return self.bit_string
        
        return self.bit_string + self.seed[len(self.bit_string) % self.rate:]

#   
# 
#     - Divide the input in chunks of (rate) bits.
#   SHA3-512(M)=KECCAK[576,1024] with bitrate=576
#   "When restricted to the case b = 1600, the KECCAK 
#   family is denoted by KECCAK[c]" - FIPS PUB 202, pag. 20.
#   
    def __chunk(self,string):
        if len(string) <= self.rate :
            return [string]
        return [string[:self.rate]] + self.__chunk(string[self.rate:])
    
    def __to_bitChunks(self,string):
        if string == None:
            raise Exception("Can not convert null.")
        return self.__chunk (self.__to_bits(string).__pad())
    
#
#
#
#    Converting the String to a State Array
#       - Fill a  5x5x64 matrix with all the 1600 bits of a block. The function to do so is represented as 
#    A[x, y, z] = S [w(5y + x) + z]. - FIPS PUB 202, pag. 9.
#     
    def __bits_to_stateArray(self,bit_array):

        if len(bit_array) != self.size :
            raise Exception("Can only convert bit arrays of size: " + str(self.size))
        rows, columns, lanes = 5,5,64
        state_array = [[[0 for _ in range(rows)] for _ in range(columns)] for _ in range(lanes)]

        x,y,z, i = 0,0,0,0
        while x < rows:
            y=0
            while y < columns:
                z=0
                while z < lanes:
                    state_array[z][x][y] = int(bit_array[i])
                    z+=1
                    i+=1
                y+=1
            x+=1
        
        return state_array
    
    def __stateArray_to_state(self):
        rows, columns, lanes = 5,5,64
        x,y,z, i = 0,0,0,0
        while x < rows:
            y=0
            while y < columns:
                z=0
                while z < lanes:
                    self.state[i] = self.state_array[z][x][y] 
                    z+=1
                    i+=1
                y+=1
            x+=1

    def __ingest_input_block(self):
        i =0
        block = self.input_blocks.pop()
        
        while i < len(block):
            self.state[i] ^= int(block[i])
            i+=1


    def ingest(self, string):
        self.input_blocks = self.__to_bitChunks(string)
        while len(self.input_blocks):
            self.__ingest_input_block()
            self.state_array = self.__bits_to_stateArray(self.state)
            i = 0
            scrambler = Scrambler(self.state_array)
            while i < self.number_of_rounds:
                scrambler.theta().rho().pi().chi().iota(i)
                i+=1
            self.state_array = scrambler.state_array
            self.__stateArray_to_state()
        
        return self
    
    def __clean_up(self):
        self.seed = "0" * self.rate
        self.input_blocks =[]
        self.state = [0] * self.size
        self.state_array = []
        self.bit_string = None
    
    def __state_to_hash_string(self):
        hash_bits = self.state[:self.rate]
        bytes = [hash_bits[i:i + 8] for i in range(0, len(hash_bits), 8)]
        hash_string = ""
        def convert_to_char(int):
            arr = list("0123456789abcjef")
            return arr[int%16]
        
        for byte in bytes:
            byte_string = "".join(str(bit) for bit in byte)
            hash_string = hash_string + convert_to_char(int(byte_string,2))

        self.__clean_up()

        return hash_string

    def digest(self):
       return self.__state_to_hash_string()
     