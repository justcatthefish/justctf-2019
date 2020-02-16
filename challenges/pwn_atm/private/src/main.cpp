//
// g++ -fno-stack-protector -fstack-protector-explicit -Wall -Wextra -Wpedantic -fPIE -z noexecstack -Wl,-z,relro,-z,now main.cpp -o atm
//
// Bugs:
// - alloc big buffer on heap which is located not far from glabal canary value
// - overwrite global canary value by writing to offset parsed via atoi(input)
// - the request send by the client has 'atm-ip:' field which must be a valid ip
// - the "valid ip" is checked with inet_aton to which u can put garbage
// - and make a buffer overflow on the stack
// also:
// - leak values via pin overwrites, but those values were already modified, so be careful
// - but this should allow to leak some pointers!
#include <cstdio>
#include <cstring>
#include <iostream>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

using namespace std;

#pragma pack(1)
struct Request {
    bool masked;
    std::string send_to_ip;
    uint8_t* buf;
    size_t len;
    uint32_t pin;
};

// global state
int sendfd = -1;
struct Request req = {};
bool has_req = false;
int counter = 0;
#define MAX_PARSES 4

#ifdef LOGME
#define LOG(...) printf("[LOG] " __VA_ARGS__)
void log_mem() {
    return;
    LOG("-- logging /bin/cat /proc/getpid()/maps --\n");
    char buf[32] = {0};
    sprintf(buf, "/bin/cat /proc/%d/maps", getpid());
    LOG("buf=%s\n", buf);
    system(buf);
    LOG("-------------------------------------\n");
}
#else
#define LOG(...) 
#define log_mem() 
#endif

void __attribute__((stack_protect)) bp() {
    __asm__("int3");
}

bool __attribute__((stack_protect)) read_exact(int fd, uint8_t* buf, size_t len) {
    size_t read_bytes = 0;

    while (read_bytes != len) {
        ssize_t n = read(fd, buf+read_bytes, len-read_bytes);
        if (n == -1) {
            LOG("Failed on read_exact");
            return false;
        }
        read_bytes += n;
    }
    return true;
}

uint8_t* __attribute__((stack_protect)) alloc_buf(size_t len) {
    uint8_t* buf = (uint8_t*)malloc(len);
    LOG("Buf (len=%lu) = %p\n", (size_t)len, buf);
    return buf;
}

size_t __attribute__((stack_protect)) get_len(uint32_t min, uint32_t max) {
    std::cout << "Length: ";
    uint32_t length = 0;
    std::cin >> length;

    LOG("Length = %u\n", length);

    if (length >= min && length <= max) {
        return length;
    }

    std::cout << "Wrong request length! (min: " << min << ", max: " << max << ")" << std::endl;
    return 0;
}

/*
Request:
BANK-REQ/1.0\n
atm-ip: <ip>\n
mask-pin-at: <offset>\n
<<data>>
 */

size_t __attribute__((stack_protect)) idx_after_nl(uint8_t* from, size_t len) {
    uint8_t* p = from;
    while (p < from+len) {
        if (*p == '\n')
            return (p-from)+1;
        p++;
    }
    std::cerr << "Nl not found!" << std::endl;
    return 0;
}

const char* HEADER_MAGIC = "ATM-REQ/1.0\n";
const char* ATM_IP = "atm-ip: ";
const char* MASK_PIN_AT = "mask-pin-at: ";

void parse_req() {
    // required
    size_t nl_idx = 0;
    int32_t pin_idx = -1;
    uint8_t* p = nullptr;
    uint8_t* buf = nullptr;
    /////////////////////////

    auto len = get_len(0x20000, 0x30000);
    if (!len)
        goto fail_nofree;

    buf = alloc_buf(len);
    if (!buf)
        goto fail_nofree;

    std::cout << "Please provide request data: " << std::endl;

    if (!read_exact(STDIN_FILENO, buf, len))
        goto fail;

    std::cout << "Received request! " << std::endl;

    buf[len-1] = 0;
    req.buf = buf;
    req.len = len;

    if (memcmp(buf, HEADER_MAGIC, strlen(HEADER_MAGIC)) != 0) {
        std::cerr << "Invalid request magic value" << std::endl;
        goto fail;
    }

    p = buf + strlen(HEADER_MAGIC);

    if (memcmp(p, ATM_IP, strlen(ATM_IP)) != 0) {
        LOG("p=%30s\n", p);
        std::cerr << "Missing atm-ip header" << std::endl;
        goto fail;
    }
    p += strlen(ATM_IP);

    nl_idx = idx_after_nl(p, buf+len-p);
    if (!nl_idx)
        goto fail;

    req.send_to_ip = std::string(p, p+nl_idx-1);
    LOG("send_to_ip = '%s'\n", req.send_to_ip.c_str());

    p += nl_idx;

    req.masked = memcmp(p, MASK_PIN_AT, strlen(MASK_PIN_AT)) == 0? true : false;

    if (!req.masked) {
        LOG("Request not masked; p=%.*s\n", 30, p);
        goto parsed;
    }
    else {
        p += strlen(MASK_PIN_AT);

        LOG("Reading pin_idx from p=%p (buf=%p)\n", p, buf);
        pin_idx = atoi((char*)p);
        LOG("Pin_idx = %d\n", pin_idx);

        if (pin_idx == -1) {
            std::cerr << "Wrong pin idx" << std::endl;
            goto fail;
        }
        else {
            uint8_t* pinat = buf+pin_idx;
            LOG("Reading pin from %p\n", pinat);
            log_mem();
            req.pin = *(uint32_t*)pinat;
            LOG("Overwriting (buf=%p) pin at %p (pinat=%d) pin=%u\n", buf, pinat, pin_idx, req.pin);
            for(int i=0; i<4; ++i)
                pinat[i] = '*';
            std::cout << "Pin masked!" << std::endl;
        }
    }

parsed:
    std::cout << "Request parsed! " << std::endl;
    has_req = true;
    return;

fail:
    free(buf);
fail_nofree:
    std::cout << "Failed to parse request! " << std::endl;
    has_req = false;
}

void __attribute__((stack_protect)) print_req() {
    if (!has_req) {
        std::cerr << "No saved request." << std::endl;
        return;
    }
    
    std::cout << "#~~~~# Request details #~~~~#" << std::endl;
    std::cout << "## atm-ip: " << req.send_to_ip << std::endl;
    std::cout << "## Length: " << req.len << std::endl;
    if (!req.masked) {
        std::cout << "## PIN: " << hex << req.pin << std::endl;
    }
    std::cout << "#~~~~###################~~~~#" << std::endl;
}

void __attribute__ ((stack_protect)) send_req() {
    if (!has_req) {
        std::cout << "No request saved." <<std::endl;
        return;
    }

    struct in_addr s = {0};
    if (inet_aton(req.send_to_ip.c_str(), &s) == 1) {
        char ipbuf[0x32] = {0};
        memcpy(ipbuf, req.send_to_ip.c_str(), req.send_to_ip.size());

        const char* special = "send-special-request/hoaxx/1.0\n";
        write(sendfd, special, strlen(special));
        write(sendfd, ipbuf, sizeof(ipbuf));
        write(sendfd, req.buf, req.len);
        return;
    }
    else {
        std::cerr << "Error: bad atm-ip value" << std::endl;
    }

    free(req.buf);
    req.buf = 0;
    has_req = false;
}

void __attribute__ ((constructor)) premain() {
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stdin, 0, 2, 0);
    sendfd = open("/dev/null", O_WRONLY);
    if (sendfd == -1) {
        puts("Could not open target fd, fatal error, please contact admin!");
        exit(-1);
    }
}

void __attribute__ ((stack_protect)) admin() {
    std::cout << "Triggered admin console..." << std::endl;
    std::cout << "Well, nothing here, but you can debug it!" << std::endl;
    bp();
}

int __attribute__((stack_protect)) main() {
    std::cout << "Welcome to SendYourAtmTx service!" << std::endl;
    std::cout << "Our API is still heavily WIP, so it might have some rough edges. You have been warned!" << std::endl;

    while (1) {
        uint8_t cmd = 0;
        std::cout << "Menu: save request (1), send saved request (2), print saved request (3)" << std::endl;
        std::cin >> cmd;
        LOG("cmd = %hhu\n", cmd);
        switch (cmd) {
            case '1':
                if (counter > MAX_PARSES) {
                    std::cerr << "Parse limit exceeded!" << std::endl;
                    continue;
                }
                parse_req();
                counter += 1;
                break;
            case '2':
                send_req();
                break;
            case '3':
                print_req();
                break;
            case 'a':
                admin();
                break;
            default:
                return -1;
        }
    }
}
