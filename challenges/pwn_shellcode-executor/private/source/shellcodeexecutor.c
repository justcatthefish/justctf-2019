#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>
#include<string.h>
#include<sys/mman.h>
#include<seccomp.h>

#define SHELLCODE_LENGTH 1024
#define MAX_URL_LENGTH 1024

bool restricted = false;
unsigned const char demo_shellcode[] = {
    0x48, 0x31, 0xff, 0x48, 0x8d, 0x35, 0x0d, 0x00, 0x00, 0x00, 0xba, 0x59,
    0x00, 0x00, 0x00, 0xb8, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05, 0xc3, 0x54,
    0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20, 0x61, 0x20, 0x64, 0x65, 0x6d,
    0x6f, 0x20, 0x73, 0x68, 0x65, 0x6c, 0x6c, 0x63, 0x6f, 0x64, 0x65, 0x20,
    0x2d, 0x20, 0x74, 0x6f, 0x20, 0x75, 0x73, 0x65, 0x20, 0x79, 0x6f, 0x75,
    0x72, 0x20, 0x6f, 0x77, 0x6e, 0x2c, 0x20, 0x70, 0x6c, 0x65, 0x61, 0x73,
    0x65, 0x20, 0x62, 0x75, 0x79, 0x20, 0x74, 0x68, 0x65, 0x20, 0x66, 0x75,
    0x6c, 0x6c, 0x20, 0x76, 0x65, 0x72, 0x73, 0x69, 0x6f, 0x6e, 0x20, 0x6f,
    0x66, 0x20, 0x6f, 0x75, 0x72, 0x20, 0x73, 0x6f, 0x66, 0x74, 0x77, 0x61,
    0x72, 0x65, 0x0a, 0x00
};
const char flag[] = "justCTF{f0r_4_b3tt3r_fl4g_purch4s3_th3_full_v3rsi0n_0f_0ur_pr0duct}";

typedef struct {
    bool deleted;
    char *origin;
    void *code;
} shellcode;

void setup() {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

void printMenu() {
    printf("0 - Quit\n"
           "1 - Download shellcode from url\n"
           "2 - Delete shellcode\n"
           "3 - Execute shellcode\n"
           "> ");
}

bool verifyUrl(const char *url) {
    for(int i=0; url[i]; i++) {
        if(url[i] < 0x0a || url[i] > 0x7f ) {
            return false;
        }
    }
    return true;
}

int getInt() {
    char input[32];
    fgets(input, 32, stdin);
    return atoi(input);
}

void downloadShellcode(shellcode *sc) {
    char *url = malloc(MAX_URL_LENGTH);
    printf("Enter url: ");
    fgets(url, MAX_URL_LENGTH, stdin);
    if(!verifyUrl(url)) {
        puts("Your url contains incorrect characters, this incident will be reported");
        exit(-1);
    }
    puts("For this feature you need to purchase the full version of our product");
}

void deleteShellcode(shellcode *sc) {
    if(sc->deleted) {
        puts("This shellcode has already been deleted");
        return;
    }
    sc->deleted = true;
    free(sc->origin);
    free(sc->code);
}

void restrictAccess() {
    puts("Your access to syscalls has been restricted. To get more syscalls purchase the full version of our product");
    restricted = true;
    scmp_filter_ctx ctx;
    ctx = seccomp_init(SCMP_ACT_KILL);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigreturn), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mmap), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(munmap), 0);
    seccomp_load(ctx);
}

void executeShellcode(shellcode *sc) {
    printf("Executing shellcode from %s\n", sc->origin);
    void *mem = mmap(NULL, SHELLCODE_LENGTH, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    memcpy(mem, sc->code, SHELLCODE_LENGTH);
    if(!restricted) {
        restrictAccess();
    }
    puts("====================================");
    ((void (*)()) mem)();
    puts("====================================");
    munmap(mem, SHELLCODE_LENGTH);
}

shellcode createShellcode(const char *origin, const void *code) {
    shellcode sc;
    sc.deleted = false;
    sc.code = malloc(SHELLCODE_LENGTH);
    memcpy(sc.code, code, SHELLCODE_LENGTH);
    sc.origin = malloc(strlen(origin));
    strcpy(sc.origin, origin);
    return sc;
}

int main() {
    setup();
    puts("Shellcode Executor PRO");
    shellcode sc = createShellcode("Shellcode Executor PRO Demo Base", demo_shellcode);
    for (;;) {
        printMenu();
        int choice = getInt();
        switch(choice) {
        case 0:
            return 0;
            break;
        case 1:
            downloadShellcode(&sc);
            break;
        case 2:
            deleteShellcode(&sc);
            break;
        case 3:
            executeShellcode(&sc);
            break;
        default:
            puts("Invalid choice");
            break;
        }
    }
    return 0;
}
