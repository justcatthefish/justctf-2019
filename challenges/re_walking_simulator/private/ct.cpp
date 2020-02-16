#include <array>
#include <iostream>
#include <functional>
#include <stdexcept>

#ifdef SECRETVALUE
constexpr uint64_t SECRET = SECRETVALUE;
#else
#error NO_SECRETVALUE_DEFINED
#endif


#ifdef WINLEN
constexpr uint64_t WINING_PATH = WINLEN;
#else
#error NO_WINLEN_DEFINED
#endif

struct ct_random {
    uint64_t const A, B, C, D;

    constexpr uint64_t value(uint64_t const i) const {
        if (i==0) {
            return (
                    (11 + A * 137 + A*C + SECRET) % 95232751 +
                    (B * 997) % 199988773 +
                    (C * 15551) % 115600447 +
                    (D + C) % 1000456003 +
                    (A + B + C + D + SECRET)
            ) % 1000000007ULL;
        } else {
            return (value(i-1) * 1103515245 + 12345) % 1000456003;
        }
    }

    constexpr uint64_t value_ab(uint64_t const i, uint64_t const a, uint64_t const b) const {
        return a + (this->value(i) % (b-a+1));
    }

    constexpr ct_random next(uint64_t const N = 0) const {
        return ct_random{
            (D+7 + 11 * N) % 1000000007,
            (value(173)+1) % 1000456003,
            (value(11) + 4) % 1000477133,
            (A*B*C+137 + SECRET) % 1000000009
        };
    }
};

template<ct_random R, uint64_t N, uint64_t A, uint64_t B>
constexpr auto gen_random_set() {
    static_assert(N <= (B-A+1), "xxx");
    std::array<uint32_t, N> ret{};
    uint64_t counter = 0;
    for(uint64_t i = 0; i < N; ++counter) {
        bool in = false;
        ret[i] = R.value_ab(counter, A, B);
        for(uint64_t j = 0; j < i; ++j) {
            in = in || (ret[i] == ret[j]);
        }

        if(!in) {
            i += 1;
        }
    }

    return ret;
}

template<ct_random R, uint64_t N, uint64_t A, uint64_t B>
constexpr auto get_cycle() {
    static_assert(N <= (B-A+1), "xxx2");
    constexpr auto tab = gen_random_set<R.next(N), N, A, B>();
    return [tab](uint64_t const x) -> uint32_t {
        for(uint64_t i = 0; i < N; ++i) {
            if(tab[i] == x) return tab[(i+1) % N];
        }
        return x;
    };
}

constexpr auto compose(auto foo, auto bar) {
    return [foo, bar](auto x){ return foo(bar(x)); };
}


template<ct_random R, uint64_t D, uint64_t N, uint64_t M>
constexpr auto get_permutation() {
    static_assert(M >= 2, "Incorrect M");

    if constexpr(D == 0) {
        return [](uint32_t const x) {
            if(x >= N) throw std::invalid_argument("Incorrect permutation input." + std::to_string(x));
            return x;
        };
    } else {
        return compose(
                get_cycle<R.next(D), R.value_ab(1, 2, M), 0, N-1>(),
                get_permutation<R.next(N+D), D-1, N, M>()
        );
    }
}

template<uint64_t D>
constexpr auto inverse_permutation(auto permutation) {
    return [permutation](auto const x) {
        if(permutation(D-1) == x) {
            return D-1;
        } else {
            if constexpr(D == 1) {
                throw std::invalid_argument("Incorrect permutation output.");
            } else {
                return inverse_permutation<D-1>(permutation)(x);
            }
        }
    };
}

// Create graph
template<typename T>
constexpr auto gepo2(T const x) {
    T ret = 1;
    while(ret < x) {
        ret *= 2;
    }

    return ret;
}

constexpr uint64_t GRAPH_SIZE = WINING_PATH*WINING_PATH;
constexpr uint64_t TREE_SIZE  = gepo2(GRAPH_SIZE);

constexpr auto graph_id_permutation = get_permutation<ct_random{1,3,3,7}.next(11),
          128, GRAPH_SIZE, GRAPH_SIZE/4>();

constexpr auto graph_id_inv_permutation = inverse_permutation<GRAPH_SIZE>(graph_id_permutation);

template<uint64_t N>
constexpr auto get_node_permutation_impl() {
    if constexpr(N == 0) {
        return [](uint32_t const x) {
            if(!(x < GRAPH_SIZE)) {
                throw std::invalid_argument("Incorrect node id.");
            }
            return x;
        };
    } else {
        return compose(
            get_permutation<ct_random{N, 13, N*N, 17*N+1}.next(1), N==1? 128 : 32, GRAPH_SIZE, GRAPH_SIZE/3>(),
            get_node_permutation_impl<N/2>()
        );
    }
}

template<uint64_t N>
constexpr auto get_node_permutation() {
    static_assert(N < GRAPH_SIZE, "Node id outside.");

    return get_node_permutation_impl<TREE_SIZE + N>();
}

bool in_game = true;

constexpr bool is_in(auto const tab, auto const v) {
    for(auto const x : tab) {
        if(x == v) {
            return true;
        }
    }

    return false;
}

template<ct_random R>
constexpr auto fix_correct_tab(auto tab, auto const v) {
    if(is_in(tab, v)) {
        return tab;
    }

    tab[R.value_ab(v, 0, tab.size()-1)] = v;

    return tab;
}

constexpr uint64_t FLAG_PERMUTATION_SIZE = 37;
std::array<uint32_t, FLAG_PERMUTATION_SIZE> flag_permutation;


void __attribute__((noinline)) victory() {
    std::cout << "Good job!\n";
    for(auto const x : flag_permutation) {
        std::cout << x << " ";
    }
    std::cout << std::endl;
    in_game = false;
}



void __attribute__((noinline)) permutate_flag(auto const perm) {
    std::array<uint32_t, FLAG_PERMUTATION_SIZE> ret;

    for(uint64_t i = 0; i < flag_permutation.size(); ++i) {
        ret[i] = flag_permutation[ perm(i) ];
    }

    flag_permutation = ret;
}

template<uint64_t N>
constexpr auto get_node_secret_permutation_impl() {
    if constexpr(N == 0) {
        return [](uint32_t const x) {
            if(!(x < FLAG_PERMUTATION_SIZE)) {
                throw std::invalid_argument("Incorrect flag-permutation id.");
            }
            return x;
        };
    } else {
        return compose(
            get_permutation<ct_random{N+1+SECRET, 13-7, 3+N*N, 17*N+1}.next(17),
                N==1? 128 : 9, FLAG_PERMUTATION_SIZE, FLAG_PERMUTATION_SIZE/(N<=3 ? 3 : 2)>(),
            get_node_secret_permutation_impl<N/2>()
        );
    }
}

template<uint64_t N>
constexpr auto get_node_secret_permutation() {
    static_assert(N < GRAPH_SIZE, "Flag id outside.");

    return get_node_secret_permutation_impl<gepo2(FLAG_PERMUTATION_SIZE) + N>();
}


template<uint64_t N>
class node {
public:
    constexpr static uint64_t ID = graph_id_permutation(N);
    constexpr static auto node_permutation = get_node_permutation<ID>();

private:
    static constexpr auto get_connections_for_node() {
        constexpr auto R = ct_random{N+11+SECRET, 32, 7*N+1, N*N};
        constexpr auto allowed_first = gen_random_set<R.next(3), WINING_PATH, 0, GRAPH_SIZE-1>();
        constexpr auto allowed_fix   = fix_correct_tab<R>(allowed_first,
                graph_id_permutation(N < WINING_PATH ? N+1 : 0)
        );

        return [allowed_fix](uint64_t const x) {
            if(graph_id_inv_permutation(x) <= WINING_PATH &&
                    graph_id_inv_permutation(x) != N+1) {
                throw std::invalid_argument("Incorrect path!");
            }

            return is_in(allowed_fix, x);
        };
    }
public:
    constexpr static auto ok_connections = get_connections_for_node();
    constexpr static auto node_flag_permutation = get_node_secret_permutation<N>();

    static auto __attribute__((noinline)) description() {
            static_assert(WINING_PATH < GRAPH_SIZE, "WIN outside GRAPH");
            permutate_flag(node_flag_permutation);
            if constexpr(ID == graph_id_permutation(WINING_PATH)) {
                victory();
            } else {
                std::cout << "You are in middle node." << std::endl;
            }
    }
};

template<uint64_t N>
constexpr auto call_description_impl() {
    static_assert(N < GRAPH_SIZE, "Too big description id.");

    if constexpr ( N > 0) {
        return compose(
                call_description_impl<N-1>(),
                [](uint64_t const x) {if(x==node<N>::ID)node<N>::description(); return x;}
        );
    } else {
        return [](uint64_t const x) {
            if(x==node<N>::ID)node<N>::description();
            return x;
        };
    }
}

constexpr auto call_description_gen() {
    constexpr auto ret = call_description_impl<GRAPH_SIZE-1>();

    return ret;
}

template<uint64_t N>
auto get_call_node_perm_impl(auto const id, auto const v) {
    static_assert(N < GRAPH_SIZE, "Too big description id.");

    if constexpr ( N > 0) {
        if(id == node<N>::ID) {
            return node<N>::node_permutation(v);
        } else {
            return get_call_node_perm_impl<N-1>(id, v);
        }
    } else {
        if(id == node<N>::ID) {
            return node<N>::node_permutation(v);
        } else {
            throw std::invalid_argument("Not known node id (perm).");
        };
    }
}

auto __attribute__((noinline)) call_node_perm(uint64_t const id, uint64_t const v) {
    return get_call_node_perm_impl<GRAPH_SIZE-1>(id, v);
}

template<uint64_t N>
auto get_check_impl(auto const id, auto const v) {
    static_assert(N < GRAPH_SIZE, "Too big description id.");

    if constexpr ( N > 0) {
        if(id == node<N>::ID) {
            return node<N>::ok_connections(v);
        } else {
            return get_check_impl<N-1>(id, v);
        }
    } else {
        if(id == node<N>::ID) {
            return node<N>::ok_connections(v);
        } else {
            throw std::invalid_argument("Not known node id (check).");
        };
    }
}

auto __attribute__((noinline)) call_check(uint64_t const id, uint64_t const v) {
    return get_check_impl<GRAPH_SIZE-1>(id, v);
}


auto __attribute__((noinline)) call_graph_id_permutation(auto const x) {
    return graph_id_permutation(x);
}

class graph_t {
    static constexpr auto call_description_obj = call_description_gen();
    void __attribute__((noinline)) call_description(auto const id) {
        call_description_obj(id);
    }

    uint64_t actual_id = graph_id_permutation(0);
    void __attribute__((noinline)) starting_a_step() {
            std::cout << "Starting a step." << std::endl;
    }

    uint64_t __attribute__((noinline)) get_choice() {
            std::cout << "Choice:" << std::endl;
            uint32_t choice;
            std::cin >> choice;

            return choice;
    }
    public:
        void make_step() {
            starting_a_step();
            call_description(actual_id);

            if(!in_game) {
                return;
            }
            uint64_t const choice_raw = get_choice();

            uint64_t const choice = call_graph_id_permutation( call_node_perm(actual_id, choice_raw) );
            if(!call_check(actual_id, choice)) {
                throw std::runtime_error("Incorrect path!");
            } else {
                actual_id = choice;
                make_step();
            }
        }
} graph;

constexpr static auto RANDOM = graph_id_permutation(1);

int main() { 
    std::cout << "FLAG PERMUTATION: " << std::flush;
    for(uint64_t i = 0; i < FLAG_PERMUTATION_SIZE; ++i) {
        std::cin >> flag_permutation[i];
    }
    std::cout << "Ok, let's start!" << std::endl;
    graph.make_step();
}
