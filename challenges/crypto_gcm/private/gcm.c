/* clang -lcrypto -O2 gcm.c -o gcm */
#include <assert.h>
#include <openssl/aes.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

const char *FLAG = "justCTF{0ld_bug_but_r3m3mber_sh0rt_is_b4d}";

const bool DEBUG = false;

const int MAX_TEXT_SIZE = 262144;
const int MAX_OPERATIONS = 1337;
const int IV_LEN = 12;
const int IV_COUNTER_LEN = 4;
const int TAG_SIZE = 2;
const int KEY_SIZE = 16;
const int BLOCK_SIZE = 16;

void handleErrors(char *x) {
  if (DEBUG) {
    fprintf(stderr, "%s error\n", x);
    ERR_print_errors_fp(stderr);
  }
  exit(1);
}

int ecb_encrypt(unsigned char *plaintext, int plaintext_len, unsigned char *key,
                unsigned char *ciphertext) {
  EVP_CIPHER_CTX *ctx;
  int len;
  int ciphertext_len;

  if (!(ctx = EVP_CIPHER_CTX_new()))
    handleErrors("EVP_CIPHER_CTX_new");

  if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_ecb(), NULL, key, NULL))
    handleErrors("EVP_CIPHER_CTX_set_padding");

  if (1 != EVP_CIPHER_CTX_set_padding(ctx, false))
    handleErrors("EVP_CIPHER_CTX_set_padding");

  if (1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len))
    handleErrors("EVP_EncryptUpdate");
  ciphertext_len = len;

  if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len))
    handleErrors("EVP_EncryptFinal_ex");
  ciphertext_len += len;

  EVP_CIPHER_CTX_free(ctx);

  return ciphertext_len;
}

int gcm_encrypt(unsigned char *plaintext, int plaintext_len, unsigned char *key,
                unsigned char *iv, int iv_len, unsigned char *ciphertext,
                unsigned char *tag) {
  EVP_CIPHER_CTX *ctx;
  int len;
  int ciphertext_len;

  /* Create and initialise the context */
  if (!(ctx = EVP_CIPHER_CTX_new()))
    handleErrors("EVP_CIPHER_CTX_new");

  /* Initialise the encryption operation. */
  if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL))
    handleErrors("EVP_aes_256_gcm");

  /*
   * Set IV length if default 12 bytes (96 bits) is not appropriate
   */
  if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, iv_len, NULL))
    handleErrors("EVP_CTRL_GCM_SET_IVLEN");

  /* Initialise key and IV */
  if (1 != EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv))
    handleErrors("EVP_EncryptInit_ex key iv");

  /*
   * Provide the message to be encrypted, and obtain the encrypted output.
   * EVP_EncryptUpdate can be called multiple times if necessary
   */
  if (1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len))
    handleErrors("EVP_EncryptUpdate");
  ciphertext_len = len;

  /*
   * Finalise the encryption. Normally ciphertext bytes may be written at
   * this stage, but this does not occur in GCM mode
   */
  if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len))
    handleErrors("EVP_EncryptFinal_ex");
  ciphertext_len += len;

  /* Get the tag */
  if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, TAG_SIZE, tag))
    handleErrors("EVP_CIPHER_CTX_ctrl");

  /* Clean up */
  EVP_CIPHER_CTX_free(ctx);

  return ciphertext_len;
}

int gcm_decrypt(unsigned char *ciphertext, int ciphertext_len,
                unsigned char *tag, unsigned char *key, unsigned char *iv,
                int iv_len, unsigned char *plaintext) {
  EVP_CIPHER_CTX *ctx;
  int len;
  int plaintext_len;
  int ret;

  /* Create and initialise the context */
  if (!(ctx = EVP_CIPHER_CTX_new()))
    handleErrors("EVP_CIPHER_CTX_new");

  /* Initialise the decryption operation. */
  if (!EVP_DecryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL))
    handleErrors("EVP_aes_256_gcm");

  /* Set IV length. Not necessary if this is 12 bytes (96 bits) */
  if (!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, iv_len, NULL))
    handleErrors("EVP_CTRL_GCM_SET_IVLEN");

  /* Initialise key and IV */
  if (!EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv))
    handleErrors("EVP_DecryptInit_ex key iv");

  /*
   * Provide the message to be decrypted, and obtain the plaintext output.
   * EVP_DecryptUpdate can be called multiple times if necessary
   */
  if (!EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len))
    handleErrors("EVP_DecryptUpdate");
  plaintext_len = len;

  /* Set expected tag value. Works in OpenSSL 1.0.1d and later */
  if (!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, TAG_SIZE, tag))
    handleErrors("EVP_CTRL_GCM_SET_TAG");

  /*
   * Finalise the decryption. A positive return value indicates success,
   * anything else is a failure - the plaintext is not trustworthy.
   */
  ret = EVP_DecryptFinal_ex(ctx, plaintext + len, &len);

  /* Clean up */
  EVP_CIPHER_CTX_free(ctx);

  if (ret > 0) {
    /* Success */
    plaintext_len += len;
    return plaintext_len;
  } else {
    /* Verify failed */
    return -1;
  }
}

void encrypt(unsigned char *plaintext, unsigned char *ciphertext,
             unsigned char *key) {
  int plaintext_len = 0;
  printf("plaintext size: ");
  if (scanf("%d", &plaintext_len) == EOF)
    handleErrors("plaintext size");

  if (plaintext_len <= 0 || plaintext_len > MAX_TEXT_SIZE)
    handleErrors("plaintext size");

  printf("plaintext: ");
  int plaintext_readed = 0;
  while (plaintext_readed < plaintext_len) {
    plaintext_readed +=
        read(STDIN_FILENO, plaintext + plaintext_readed, plaintext_len - plaintext_readed);
    if (plaintext_readed <= 0)
      break;
  }
  if (plaintext_readed != plaintext_len)
    handleErrors("plaintext read");
  getc(stdin);

  unsigned char iv[IV_LEN] = {};
  RAND_bytes(iv, IV_LEN);

  unsigned char tag[16];
  int ciphertext_len =
      gcm_encrypt(plaintext, plaintext_len, key, iv, IV_LEN, ciphertext, tag);

  write(STDOUT_FILENO, iv, IV_LEN);
  write(STDOUT_FILENO, tag, TAG_SIZE);
  write(STDOUT_FILENO, ciphertext, ciphertext_len);

  memset(plaintext, 0, plaintext_len);
  memset(ciphertext, 0, ciphertext_len);
}

void verify(unsigned char *plaintext, unsigned char *ciphertext,
            unsigned char *key) {
  int ciphertext_len = 0;
  printf("ciphertext size: ");
  if (scanf("%d", &ciphertext_len) == EOF)
    handleErrors("ciphertext size");

  if (ciphertext_len <= 0 || ciphertext_len > MAX_TEXT_SIZE)
    handleErrors("ciphertext size");

  printf("ciphertext: ");
  int ciphertext_readed = 0;
  while (ciphertext_readed < ciphertext_len) {
    ciphertext_readed +=
        read(STDIN_FILENO, ciphertext+ciphertext_readed, ciphertext_len - ciphertext_readed);
    if (ciphertext_readed <= 0)
      break;
  }
  if (ciphertext_readed != ciphertext_len)
    handleErrors("ciphertext read");
  getc(stdin);

  printf("tag: ");
  unsigned char tag[TAG_SIZE] = {};
  int tag_len = read(STDOUT_FILENO, tag, TAG_SIZE);
  if (tag_len != TAG_SIZE)
    handleErrors("tag len");

  printf("iv: ");
  unsigned char iv[IV_LEN] = {};
  int iv_len = read(STDOUT_FILENO, iv, IV_LEN);
  if (iv_len != IV_LEN)
    handleErrors("iv len");

  int result =
      gcm_decrypt(ciphertext, ciphertext_len, tag, key, iv, iv_len, plaintext);

  if (result != -1){
    puts("OK");
  } else {
    puts("FAIL");
  }

  memset(plaintext, 0, ciphertext_len);
  memset(ciphertext, 0, ciphertext_len);
}

int main() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);

  unsigned char key[KEY_SIZE] = {};
  RAND_bytes(key, KEY_SIZE);

  unsigned char *plaintext = malloc(MAX_TEXT_SIZE);
  unsigned char *ciphertext = malloc(MAX_TEXT_SIZE);
  if (plaintext == NULL || ciphertext == NULL)
    handleErrors("malloc texts");

  int encrypt_counter = 0;
  int verify_counter = 0;
  bool we_are_done = false;

  while (!we_are_done && encrypt_counter + verify_counter < MAX_OPERATIONS) {
    printf("operation: ");
    int choice = getc(stdin);
    switch (choice) {
    case 'e':
    case 'E':
      encrypt_counter += 1;
      encrypt(plaintext, ciphertext, key);
      break;
    case 'v':
    case 'V':
      verify_counter += 1;
      verify(plaintext, ciphertext, key);
      break;
    case 'q':
    case 'Q':
      we_are_done = true;
      break;
    default:
      if (DEBUG)
        fprintf(stderr, "%c\n", choice);
      handleErrors("Bad choice");
    }
  }

  memset(plaintext, 0, BLOCK_SIZE);
  int h_true_len = ecb_encrypt(plaintext, BLOCK_SIZE, key, ciphertext);
  if (h_true_len != BLOCK_SIZE)
    handleErrors("h_true_len");

  unsigned char h_true[h_true_len];
  memcpy(h_true, ciphertext, h_true_len);

  unsigned char h[BLOCK_SIZE] = {};
  printf("authentication key: ");
  if (read(STDIN_FILENO, h, h_true_len) == h_true_len) {
    if (memcmp(h, h_true, h_true_len) == 0) {
      printf("%s\n", FLAG);
    } else {
      printf("Nope, true auth key is: ");
      write(STDOUT_FILENO, h_true, h_true_len);
    }
  } else {
    handleErrors("auth key");
  }

  free(plaintext);
  free(ciphertext);

  return 0;
}
