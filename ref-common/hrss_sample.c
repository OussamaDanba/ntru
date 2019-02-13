#include "sample.h"
#include "fips202.h"

void sample_xof(unsigned char *output, const size_t sizeof_output, const unsigned char seed[NTRU_SEEDBYTES], const unsigned char domain[NTRU_DOMAINBYTES])
{
  unsigned char input[NTRU_SEEDBYTES+NTRU_DOMAINBYTES];
  int i;

  for(i=0;i<NTRU_SEEDBYTES;i++)
    input[i] = seed[i];
  for(i=0;i<8;i++)
    input[NTRU_SEEDBYTES+i] = domain[i];

  shake128(output, sizeof_output, input, sizeof(input));
}

void sample_iid(poly *r, const unsigned char uniformbytes[NTRU_S3_IID_BYTES])
{
  int i;
  /* {0,1,...,255} -> {0,1,2}; Pr[0] = 86/256, Pr[1] = Pr[-1] = 85/256 */
  for(i=0; i<NTRU_N-1; i++)
    r->coeffs[i] = mod3(uniformbytes[i]);

  r->coeffs[NTRU_N-1] = 0;
}

void sample_iid_plus(poly *r, const unsigned char uniformbytes[NTRU_S3_IID_BYTES])
{
  /* Sample r using sample_iid then conditionally flip    */
  /* signs of even index coefficients so that <x*r, r> >= 0.      */

  int i;
  uint16_t s = 0;

  sample_iid(r, uniformbytes);

  /* Map {0,1,2} -> {0, 1, 2^16 - 1} */
  for(i=0; i<NTRU_N-1; i++)
    r->coeffs[i] = r->coeffs[i] | (-(r->coeffs[i]>>1));

  /* s = <x*r, r>.  (r[n-1] = 0) */
  for(i=0; i<NTRU_N-1; i++)
    s += r->coeffs[i+1] * r->coeffs[i];

  /* Extract sign of s (sign(0) = 1) */
  s = 1 | (-(s>>15));

  for(i=0; i<NTRU_N; i+=2)
    r->coeffs[i] = s * r->coeffs[i];

  /* Map {0,1,2^16-1} -> {0, 1, 2} */
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = 3 & (r->coeffs[i] ^ (r->coeffs[i]>>15));
}

