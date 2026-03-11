#include "cobs.h"

__attribute__((weak)) size_t COBS_encode(
    const uint8_t *decodedMessage, // pointer to the buffer where the data to encode is
    size_t length,                 // number of elements in the message to encode
    uint8_t *codedMessage          // pointer to the buffer where the encoded data will be stored
)
{
    return 0U;
}

__attribute__((weak)) size_t COBS_decode(
    const uint8_t *codedMessage, // pointer to the buffer where the data to decode is
    size_t length,               // number of elements in the message to decode
    uint8_t *decodedMessage      // pointer to the buffer where the decoded data will be stored
)
{
    return 0U;
}