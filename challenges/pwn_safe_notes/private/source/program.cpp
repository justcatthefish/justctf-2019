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

// Errors

class incorrect_password_error : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class no_note_error : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class unsuported_character_error : public std::invalid_argument {
public:
    using std::invalid_argument::invalid_argument;
};

// Memory

class memory_page_t {
    static size_t const page_size;

    char *allocate();
    size_t  readable_memory;
    std::shared_ptr<char[]> address_ptr;
public:   

    memory_page_t(size_t const readable_memory) : readable_memory(readable_memory),
        address_ptr(allocate(), [=](auto const ptr){
            munmap(ptr, page_size * (1 + readable_memory/page_size));
        }) {};
    char &operator[](size_t const i){return address_ptr[i];}
    char operator[](size_t const i) const {return address_ptr[i];}

    void lock();
    char *address(){return &address_ptr[0];}
    size_t size() const {return readable_memory;}
};

size_t const memory_page_t::page_size = sysconf(_SC_PAGESIZE);

// Hash

memory_page_t generate_hash(std::string const s) {
    unsigned char hash[SHA512_DIGEST_LENGTH];
    memory_page_t ret(4);

    SHA512_CTX sha512;
    SHA512_Init(&sha512);
    SHA512_Update(&sha512, s.c_str(), s.size());
    SHA512_Final(hash, &sha512);

    for(size_t i = 0; i < 4; ++i) {
        ret[i] = hash[i];
    }

    return ret;
}



//  Messages
volatile char _xxxxxxxxx[] = "PUBLIC:1\nPRIVATE:2\n";
enum note_t : size_t {
    PUBLIC=1,
    PRIVATE=2,
    NONE=0
};

note_t note_type = note_t::NONE;

// Operations

enum class op_t : unsigned char {
    ADD_PRIVATE,
    ADD_PUBLIC,
    LOAD_NOTE,
    SHOW_NOTE,
    CANCEL,
    BIG_TEST,
    ERROR
};

op_t get_operation_id() {
    std::cout << "Operation id: " << std::flush;
    uint32_t choice;
    std::cin >> choice;

    switch(choice) {
        case 1  : return op_t::ADD_PRIVATE;
        case 2  : return op_t::ADD_PUBLIC;
        case 3  : return op_t::LOAD_NOTE;
        case 4  : return op_t::SHOW_NOTE;
        case 5  : return op_t::CANCEL;
        case 6  : return op_t::BIG_TEST;
        default : return op_t::ERROR;
    }
}

// System

class {
    std::vector<memory_page_t> actual;
    std::map<std::string, std::vector<memory_page_t>> dict;

public:
    void actual_clear() {actual.clear();};
    size_t actual_size() {return actual.size();}
    void push_actual(memory_page_t mem){actual.push_back(mem);}
    void save() {
        std::string name;

        std::cout << "Note name: " << std::flush;
        std::cin >> name;

        dict[name] = actual;
        actual_clear();
    }
    std::vector<memory_page_t> get(std::string const &name){return dict[name];}

} note_system;

void get_password(char *data[2]);
void get_note(char *data[2]);
std::tuple<char *, char *> load_note(char *data[2]);
void show_note(char const *const data[]);
void unload_note(char *data[2]);
void big_test_foo();

size_t position = 0;

void __attribute__ ((noinline)) hacker_check() {
    static size_t counter = 0;

    counter += 1;
    if(counter > 128 ) {
             throw std::runtime_error("You used limit operations for free user, BUY PREMIUM!");       
    }
}

void __attribute__ ((noinline)) main_loop() {
    char *data[2 + 6];
    data[0] = data[1] = nullptr;

    while(true) {
        #ifdef PRINTROP
        std::cerr << "position = " << position << std::endl;
        #endif //PRINTROP

        hacker_check();

        try {
            switch(get_operation_id()) {
                case op_t::ADD_PRIVATE : get_password(data);                        // OK -- actual pass
                [[fallthrough]];
                case op_t::ADD_PUBLIC  : get_note(data); note_system.save();        // OK -- actual note + save
                break;
                case op_t::LOAD_NOTE   : std::tie(data[0], data[1]) = load_note(data);  // OK -- position += 1
                break;
                case op_t::SHOW_NOTE   : show_note(data); unload_note(data);        // OK -- unused
                break;
                case op_t::CANCEL      : unload_note(data);                         // OK -- set 0 at end
                break;
                case op_t::BIG_TEST    : return;                                    // OK
                default: throw std::invalid_argument("Operation unknown!");         // OK
            }
        }
        catch(incorrect_password_error const &e) {
            std::cout << e.what() << std::endl;
        }
        catch(unsuported_character_error const &e) {
            std::cout << e.what() << std::endl;
            for(size_t i = 0; i < note_system.actual_size(); ++i) {
                data[position-1] = nullptr;
                position -= 1;
            }

            note_system.actual_clear();
        }
        catch(no_note_error const &e) {
            std::cout << e.what() << std::endl;
        }
    }
}

int main() {
    std::cout << "Create PRIVATE note : 1" << std::endl;
    std::cout << "Create PUBLIC  note : 2" << std::endl;
    std::cout << "Load note           : 3" << std::endl;
    std::cout << "Show loaded note    : 4" << std::endl;
    std::cout << "Unload note         : 5" << std::endl;
    std::cout << "Exit                : 6" << std::endl;
    std::cout << std::endl;
    try {
        main_loop();
    }
    catch(std::bad_alloc const &e) {
        std::cout << e.what() << std::endl << "E:" << errno << std::endl << "You may want to mail the administrator."<< std::endl;

        return 3;
    }
    catch(std::exception const &e) {
        std::cout << e.what() << std::endl;
        return 2;
    }
}

// Functions basic

void get_password(char *data[2]) {
    std::cout << "Give password: " << std::flush;
    std::string password;
    std::cin >> password;

    auto hash = generate_hash(password);

    #ifdef PRINTROP
    for(size_t i = 0; i < 4; ++i) {
        std::cerr << std::hex <<
        static_cast<unsigned>(static_cast<unsigned char>(hash[i])) << ' ';
    }
    std::cerr << std::endl;
    #endif

    note_system.push_actual(hash);
    data[position] = hash.address();

    position += 1;
}

void __attribute__ ((noinline)) get_note(char *data[2]) {
    std::string note;
    std::cout << "Note: " << std::flush;
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(),'\n');
    std::getline(std::cin, note);

    memory_page_t note_memory(note.size());
    for(size_t i = 0; i < note.size(); ++i) {
        note_memory[i] = note[i];
    }

    note_memory.lock();

    note_system.push_actual(note_memory);

    static std::string const not_allowed = "!@#$%^&*()_+-=[]{};'<>|";
    for(char const forbidden : not_allowed) {
        if(std::count(std::begin(note), std::end(note), forbidden) > 0) {
            throw unsuported_character_error(
                std::string("Invalid character: ") + forbidden + std::string(" It's for your security!")
            );
        }
    }

    for(char const c : note) {
        if(!std::isprint(c)) {
            throw std::runtime_error("Internal HACKER error.");
        }
    }

    data[position] = note_memory.address();
    position += 1;
}

std::tuple<char *, char *> load_note(char *data[2]) {
    if(data[1] != nullptr) {
        unload_note(data);
    }

    position += 1;
    std::cout << "Note name: " << std::flush;

    std::string name;
    std::cin >> name;

    auto note = note_system.get(name);
    if(note.size() == note_t::NONE) {
        std::cout << "No note with name: " << name << std::endl;
        return std::make_tuple(nullptr, nullptr);
    }

    if(note.size() == note_t::PUBLIC) {
        return std::make_tuple(note[0].address(), nullptr);
    }
    position += 1;
    return std::make_tuple(note[0].address(), note[1].address()); 
}

bool check_password(char const *const pass_hash) {
    std::cout << "Give password: " << std::flush;

    std::string password;
    std::cin >> password;

    auto const hash = generate_hash(password);

    for(size_t i = 0; i < hash.size(); ++i) {
        if(hash[i] != pass_hash[i]) {
            return false;
        }
    }

    return true;
}

void show_note(char const *const data[]) {
    if(position == note_t::PRIVATE) {
        if( !check_password(data[position-2]) ) {
            throw incorrect_password_error("Given password is incorrect.");
        }
    }

    if(position == note_t::PUBLIC || position == note_t::PRIVATE) {
        std::cout << data[position-1] << std::endl;
    } else if(position == note_t::NONE){
        std::cout << "No note loaded." << std::endl;
    } else {
        throw std::logic_error("Internal note error.");
    }
}

void unload_note(char *data[2]) {
    while(position > 0) {
        data[position] = nullptr;
        position -= 1;
    }

    data[0] = nullptr;
    position = note_t::NONE;
}

void big_test_foo() {
    size_t size;
    std::cin >> size;

    volatile memory_page_t tab(size);
}

// Functions memory_page_t

char *memory_page_t::allocate() {
    if(readable_memory == 0) {
        return nullptr;
    }

    size_t const needed_size = page_size * (1 + readable_memory/page_size);

    char *const ret = reinterpret_cast<char *>(mmap(nullptr, needed_size,
        PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0));

    if(ret == reinterpret_cast<char *>(-1)) {
        throw std::bad_alloc();
    }

    if(reinterpret_cast<size_t>(ret)%page_size != 0) {
        auto const tmp = allocate();
        munmap(ret, needed_size);

        return tmp;
    }

    return ret;
}

void memory_page_t::lock() {
    size_t const full_size = page_size * (1 + readable_memory/page_size);

    mprotect(address(), full_size, PROT_READ);
}
