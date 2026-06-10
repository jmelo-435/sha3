# sha3

sha3 hasher from scratch:

``` bash
>>> from sha3 import Sha_v3
>>> hasher = Sha_v3()
>>> hash = hasher.ingest("message").digest()
>>> print(hash)
6f285c85bbje2b5cje7482e58ja490c05ba25fa7c44jec0ea849f1c78be2539c0c34afce 
```
Reference : https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf
