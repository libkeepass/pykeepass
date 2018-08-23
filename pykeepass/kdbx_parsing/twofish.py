# =============================================================================
# Copyright (c) 2008 Christophe Oosterlynck <christophe.oosterlynck_AT_gmail.com>
#                    & NXP ( Philippe Teuwen <philippe.teuwen_AT_nxp.com> )
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# =============================================================================
# -*- coding: utf-8 -*-

__all__ = ['Twofish']

from . import pytwofish
from Crypto.Util.strxor import strxor
from Crypto.Util.Padding import pad

MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_OFB = 5
MODE_CTR = 6
MODE_XTS = 7
MODE_CMAC = 8


class BlockCipher():
    """ Base class for all blockciphers
    """
    MODE_ECB = MODE_ECB
    MODE_CBC = MODE_CBC
    MODE_CFB = MODE_CFB
    MODE_OFB = MODE_OFB
    MODE_CTR = MODE_CTR
    MODE_XTS = MODE_XTS
    MODE_CMAC = MODE_CMAC

    key_error_message = "Wrong key size" #should be overwritten in child classes

    def __init__(self,key,mode,IV,counter,cipher_module,segment_size,args={}):
        # Cipher classes inheriting from this one take care of:
        #   self.blocksize
        #   self.cipher
        self.key = key
        self.mode = mode
        self.cache = b''
        self.ed = None

        if 'keylen_valid' in dir(self): #wrappers for pycrypto functions don't have this function
         if not self.keylen_valid(key) and type(key) is not tuple:
                raise ValueError(self.key_error_message)

        if IV == None:
            self.IV = b'\x00'*self.blocksize
        else:
            self.IV = IV

        if mode != MODE_XTS:
            self.cipher = cipher_module(self.key,**args)
        if mode == MODE_ECB:
            self.chain = ECB(self.cipher, self.blocksize)
        elif mode == MODE_CBC:
            if len(self.IV) != self.blocksize:
                raise Exception("the IV length should be %i bytes"%self.blocksize)
            self.chain = CBC(self.cipher, self.blocksize,self.IV)
        elif mode == MODE_CFB:
            if len(self.IV) != self.blocksize:
                raise Exception("the IV length should be %i bytes"%self.blocksize)
            if segment_size == None:
                raise ValueError("segment size must be defined explicitely for CFB mode")
            if segment_size > self.blocksize*8 or segment_size%8 != 0:
                # current CFB implementation doesn't support bit level acces => segment_size should be multiple of bytes
                raise ValueError("segment size should be a multiple of 8 bits between 8 and %i"%(self.blocksize*8))
            self.chain = CFB(self.cipher, self.blocksize,self.IV,segment_size)
        elif mode == MODE_OFB:
            if len(self.IV) != self.blocksize:
                raise ValueError("the IV length should be %i bytes"%self.blocksize)
            self.chain = OFB(self.cipher, self.blocksize,self.IV)
        elif mode == MODE_CTR:
            if (counter == None) or  not callable(counter):
                raise Exception("Supply a valid counter object for the CTR mode")
            self.chain = CTR(self.cipher,self.blocksize,counter)
        elif mode == MODE_XTS:
            if self.blocksize != 16:
                raise Exception('XTS only works with blockcipher that have a 128-bit blocksize')
            if not(type(key) == tuple and len(key) == 2):
                raise Exception('Supply two keys as a tuple when using XTS')
            if 'keylen_valid' in dir(self): #wrappers for pycrypto functions don't have this function
             if not self.keylen_valid(key[0]) or  not self.keylen_valid(key[1]):
                raise ValueError(self.key_error_message)
            self.cipher = cipher_module(self.key[0],**args)
            self.cipher2 = cipher_module(self.key[1],**args)
            self.chain = XTS(self.cipher, self.cipher2)
        elif mode == MODE_CMAC:
            if self.blocksize not in (8,16):
                raise Exception('CMAC only works with blockcipher that have a 64 or 128-bit blocksize')
            self.chain = CMAC(self.cipher,self.blocksize,self.IV)
        else:
                raise Exception("Unknown chaining mode!")

    def encrypt(self,plaintext,n=''):
        """Encrypt some plaintext

            plaintext   = a string of binary data
            n           = the 'tweak' value when the chaining mode is XTS

        The encrypt function will encrypt the supplied plaintext.
        The behavior varies slightly depending on the chaining mode.

        ECB, CBC:
        ---------
        When the supplied plaintext is not a multiple of the blocksize
          of the cipher, then the remaining plaintext will be cached.
        The next time the encrypt function is called with some plaintext,
          the new plaintext will be concatenated to the cache and then
          cache+plaintext will be encrypted.

        CFB, OFB, CTR:
        --------------
        When the chaining mode allows the cipher to act as a stream cipher,
          the encrypt function will always encrypt all of the supplied
          plaintext immediately. No cache will be kept.

        XTS:
        ----
        Because the handling of the last two blocks is linked,
          it needs the whole block of plaintext to be supplied at once.
        Every encrypt function called on a XTS cipher will output
          an encrypted block based on the current supplied plaintext block.

        CMAC:
        -----
        Everytime the function is called, the hash from the input data is calculated.
        No finalizing needed.
        The hashlength is equal to block size of the used block cipher.
        """
        #self.ed = 'e' if chain is encrypting, 'd' if decrypting,
        # None if nothing happened with the chain yet
        #assert self.ed in ('e',None) 
        # makes sure you don't encrypt with a cipher that has started decrypting
        self.ed = 'e'
        if self.mode == MODE_XTS:
            # data sequence number (or 'tweak') has to be provided when in XTS mode
            return self.chain.update(plaintext,'e',n)
        else:
            return self.chain.update(plaintext,'e')

    def decrypt(self,ciphertext,n=''):
        """Decrypt some ciphertext

            ciphertext  = a string of binary data
            n           = the 'tweak' value when the chaining mode is XTS

        The decrypt function will decrypt the supplied ciphertext.
        The behavior varies slightly depending on the chaining mode.

        ECB, CBC:
        ---------
        When the supplied ciphertext is not a multiple of the blocksize
          of the cipher, then the remaining ciphertext will be cached.
        The next time the decrypt function is called with some ciphertext,
          the new ciphertext will be concatenated to the cache and then
          cache+ciphertext will be decrypted.

        CFB, OFB, CTR:
        --------------
        When the chaining mode allows the cipher to act as a stream cipher,
          the decrypt function will always decrypt all of the supplied
          ciphertext immediately. No cache will be kept.

        XTS:
        ----
        Because the handling of the last two blocks is linked,
          it needs the whole block of ciphertext to be supplied at once.
        Every decrypt function called on a XTS cipher will output
          a decrypted block based on the current supplied ciphertext block.

        CMAC:
        -----
        Mode not supported for decryption as this does not make sense.
        """
        #self.ed = 'e' if chain is encrypting, 'd' if decrypting,
        # None if nothing happened with the chain yet
        #assert self.ed in ('d',None)
        # makes sure you don't decrypt with a cipher that has started encrypting
        self.ed = 'd'
        if self.mode == MODE_XTS:
            # data sequence number (or 'tweak') has to be provided when in XTS mode
            return self.chain.update(ciphertext,'d',n)
        else:
            return self.chain.update(ciphertext,'d')

    def final(self,style='pkcs7'):
        # TODO: after calling final, reset the IV? so the cipher is as good as new?
        """Finalizes the encryption by padding the cache

            padfct = padding function
                     import from CryptoPlus.Util.padding

        For ECB, CBC: the remaining bytes in the cache will be padded and
                      encrypted.
        For OFB,CFB, CTR: an encrypted padding will be returned, making the
                          total outputed bytes since construction of the cipher
                          a multiple of the blocksize of that cipher.

        If the cipher has been used for decryption, the final function won't do
          anything. You have to manually unpad if necessary.

        After finalization, the chain can still be used but the IV, counter etc
          aren't reset but just continue as they were after the last step (finalization step).
        """
        assert self.mode not in (MODE_XTS, MODE_CMAC) # finalizing (=padding) doesn't make sense when in XTS or CMAC mode
        if self.ed == b'e':
            # when the chain is in encryption mode, finalizing will pad the cache and encrypt this last block
            if self.mode in (MODE_OFB,MODE_CFB,MODE_CTR):
                dummy = b'0'*(self.chain.totalbytes%self.blocksize) # a dummy string that will be used to get a valid padding
            else: #ECB, CBC
                dummy = self.chain.cache
            pdata = pad(dummy,self.blocksize,style=style)[len(dummy):]
            #~ pad = padfct(dummy,padding.PAD,self.blocksize)[len(dummy):] # construct the padding necessary
            return self.chain.update(pdata,b'e') # supply the padding to the update function => chain cache will be "cache+padding"
        else:
            # final function doesn't make sense when decrypting => padding should be removed manually
            pass


class CBC:
    """CBC chaining mode
    """
    def __init__(self, codebook, blocksize, IV):
        self.IV = IV
        self.cache = b''
        self.codebook = codebook
        self.blocksize = blocksize

    def update(self, data, ed):
        """Processes the given ciphertext/plaintext

        Inputs:
            data: raw string of any length
            ed:   'e' for encryption, 'd' for decryption
        Output:
            processed raw string block(s), if any

        When the supplied data is not a multiple of the blocksize
          of the cipher, then the remaining input data will be cached.
        The next time the update function is called with some data,
          the new data will be concatenated to the cache and then
          cache+data will be processed and full blocks will be outputted.
        """
        if ed == 'e':
            encrypted_blocks = b''
            self.cache += data
            if len(self.cache) < self.blocksize:
                return b''
            for i in range(0, len(self.cache)-self.blocksize+1, self.blocksize):
                self.IV = self.codebook.encrypt(strxor(self.cache[i:i+self.blocksize],self.IV))
                encrypted_blocks += self.IV
            self.cache = self.cache[i+self.blocksize:]
            return encrypted_blocks
        else:
            decrypted_blocks = b''
            self.cache += data
            if len(self.cache) < self.blocksize:
                return b''
            for i in range(0, len(self.cache)-self.blocksize+1, self.blocksize):
                plaintext = strxor(self.IV,self.codebook.decrypt(self.cache[i:i + self.blocksize]))
                self.IV = self.cache[i:i + self.blocksize]
                decrypted_blocks+=plaintext
            self.cache = self.cache[i+self.blocksize:]
            return decrypted_blocks


class python_Twofish(BlockCipher):
    def __init__(self,key,mode,IV,counter,segment_size):
        if len(key) not in (16,24,32) and type(key) is not tuple:
                raise ValueError("Key should be 128, 192 or 256 bits")
        cipher_module = pytwofish.Twofish
        self.blocksize = 16
        BlockCipher.__init__(self,key,mode,IV,counter,cipher_module,segment_size)
    
    @classmethod
    def new(cls, key,mode=MODE_ECB,IV=None,counter=None,segment_size=None):
        return cls(key,mode,IV,counter,segment_size)

Twofish = python_Twofish

