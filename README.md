# worldline-poc
A small proof of concept to see if we can use Wordline to pay supplier invoice payments for Open Poen.

### main.py
I managed to "approve" a payment. Then the status becomes "CAPTURE_REQUESTED". According to "rickvanthof" in [this issue](https://github.com/Ingenico-ePayments/connect-sdk-php/issues/3), the sandbox should change it to "PAID" automatically to simulate real payments. That hasn't happened to me so far...
