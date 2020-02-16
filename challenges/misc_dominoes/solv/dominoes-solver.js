var trie = require('trie-prefix-tree');
var fs = require('fs');

// Load english dictionary
const english_dict = fs.readFileSync('google-10000-english.txt').toString().split('\n').map(x=>x.trim())

// Create prefix tree, for faster search
const TREE = trie(english_dict);

// save some memory in recursion
var tmp_s = ""

// check for hints
var HINTS = []

// all valid solutions
var SOLVES = []

// search graph
var GRAPH = {}

// recursive route to read the solution
var route = []

// cache to cut nodes in recursion
var CACHE = new Set()

// simple function calculating last word betwen _
function last_word(key=''){
    var s = []
    for(var i=route.length-1; i>=0 && route[i] != '_'; i--){
        s.push(route[i])
    }
    return s.reverse().join('')+key
}

// dfs function searching for solutions
function dfs(key, depth){
    // current prefix
    tmp_s = route.join('')

    // cache handling
    if(CACHE.has(tmp_s + key)){
        return;
    }
    CACHE.add(tmp_s + key);
    
    // check if the prefix is a valid english word
    // in case of _ check if is a valid word
    if(key[0] == '_'){
        if(!TREE.hasWord(last_word())) {
            return;
        }
    }else{
        if(!TREE.isPrefix(last_word(key[0]))) {
            return;
        }
    }


    // end of recursion
    // check if the solution contains all the hints
    // if so, add solution to SOLVES
    if(depth == 0){
        var sol = tmp_s + key
        for(var hint of HINTS){
            if(sol.indexOf(hint) == -1) return;
        }
        SOLVES.push(tmp_s+key)
        return
    }
        

    // push current character to the recursion route
    route.push(key[0]);

    for(var i = 0; i < GRAPH[key].length; i++){
        // visit if the node wasn't visited
        if(!GRAPH[key][i][1]){
            // set node as visited
            GRAPH[key][i][1] = 1;
                dfs(GRAPH[key][i][0], depth-1)
            // set node as not visited after end of recursion
            GRAPH[key][i][1] = 0;
        }
    }

    // pop current character from the recursion route
    route.pop();
}

// this is helper function to generaate best hints.
// not part of the solution
function least_popular(str, k){
    let s = new Map()
    for(let i=0; i<str.length-k; i++){
        let key = str.substr(i, k);
        let counter = 0;
        for(let solve of SOLVES){
            if(solve.indexOf(key) === 0) counter++
        }
        s.set(key, counter)
    }
    return s;
}

function clearGlobals(){
    HINTS = []
    SOLVES = []
    GRAPH = {}
    route = []
    CACHE = new Set()
}

// solving function
function solve(dominoes, hints=[]){
    clearGlobals()
    HINTS = hints;
    
    // iterate over dominos and fill the GRAPH
    // e.g for tuple (A, B, C) we mark that from AB we can go to BC
    for(let [x, y, z] of dominoes){
        if(GRAPH[x+y]) GRAPH[x+y].push([y+z, 0])
        else GRAPH[x+y] = [[y+z,0]]
    }

    /*
    // iterate over all possible starting characters, might exceed the heap
    for(var key of Object.keys(GRAPH)){
        console.log(key)
        dfs(key, dominoes.length)
    }
    */
   
    // you can quickly notice that only 'th' produces any solutions
    dfs("th", dominoes.length)

    // display how many hints provided and how many solutions there are
    console.log(`hints: ${hints.length} | solutions: ${SOLVES.length}`);
    l = least_popular("there_was_no_single_doubt_in_my_mind_that_great_player_like_you_shall_solve_the_puzzle", 4)

    // display three best hints
    console.log(Array.from(l.entries()).filter(y=>y[1]>0).sort((a,b)=>a[1]-b[1]).slice(0,3))

    // write solutions to file
    fs.writeFileSync(`solutions_${hints.length}.txt`, SOLVES.join('\n'))

    return;
}

// 0 hints
solve(['ou_', '_pl', '_th', 'ind', 'gre', 'y_m', '_my', 'sol', '_gr', 'all', 'olv', '_wa', 'll_', 'as_', 'in_', 'sha', 'at_', 'e_t', 'ike', 'd_t', 'e_p', 'ubt', 'you', 'zle', 'ke_', 'zzl', 'oub', 'aye', 'u_s', '_yo', '_mi', 'l_s', 'gle', 'nd_', '_do', 'lay', 'eat', '_no', 'bt_', 'e_y', 'uzz', 't_g', 'the', 'r_l', 'no_', 'the', '_in', 'at_', 'n_m', '_th', 'dou', 't_i', 'her', 'hat', 'ngl', 'er_', 'ere', 'rea', 'e_d', 'lik', 'le_', 'puz', 'yer', 'was', 'ing', 'o_s', 'e_w', 'hal', '_pu', '_sh', 's_n', 'pla', 'sin', 'my_', 're_', '_so', 'lve', 'tha', '_li', 'min', 't_p', 've_', 'he_', '_si'], [])

// 1 hint
solve(['ou_', '_pl', '_th', 'ind', 'gre', 'y_m', '_my', 'sol', '_gr', 'all', 'olv', '_wa', 'll_', 'as_', 'in_', 'sha', 'at_', 'e_t', 'ike', 'd_t', 'e_p', 'ubt', 'you', 'zle', 'ke_', 'zzl', 'oub', 'aye', 'u_s', '_yo', '_mi', 'l_s', 'gle', 'nd_', '_do', 'lay', 'eat', '_no', 'bt_', 'e_y', 'uzz', 't_g', 'the', 'r_l', 'no_', 'the', '_in', 'at_', 'n_m', '_th', 'dou', 't_i', 'her', 'hat', 'ngl', 'er_', 'ere', 'rea', 'e_d', 'lik', 'le_', 'puz', 'yer', 'was', 'ing', 'o_s', 'e_w', 'hal', '_pu', '_sh', 's_n', 'pla', 'sin', 'my_', 're_', '_so', 'lve', 'tha', '_li', 'min', 't_p', 've_', 'he_', '_si'], ["le_d"])

// 2 hints
solve(['ou_', '_pl', '_th', 'ind', 'gre', 'y_m', '_my', 'sol', '_gr', 'all', 'olv', '_wa', 'll_', 'as_', 'in_', 'sha', 'at_', 'e_t', 'ike', 'd_t', 'e_p', 'ubt', 'you', 'zle', 'ke_', 'zzl', 'oub', 'aye', 'u_s', '_yo', '_mi', 'l_s', 'gle', 'nd_', '_do', 'lay', 'eat', '_no', 'bt_', 'e_y', 'uzz', 't_g', 'the', 'r_l', 'no_', 'the', '_in', 'at_', 'n_m', '_th', 'dou', 't_i', 'her', 'hat', 'ngl', 'er_', 'ere', 'rea', 'e_d', 'lik', 'le_', 'puz', 'yer', 'was', 'ing', 'o_s', 'e_w', 'hal', '_pu', '_sh', 's_n', 'pla', 'sin', 'my_', 're_', '_so', 'lve', 'tha', '_li', 'min', 't_p', 've_', 'he_', '_si'], ["le_d","o_si"])

// 3 hints
solve(['ou_', '_pl', '_th', 'ind', 'gre', 'y_m', '_my', 'sol', '_gr', 'all', 'olv', '_wa', 'll_', 'as_', 'in_', 'sha', 'at_', 'e_t', 'ike', 'd_t', 'e_p', 'ubt', 'you', 'zle', 'ke_', 'zzl', 'oub', 'aye', 'u_s', '_yo', '_mi', 'l_s', 'gle', 'nd_', '_do', 'lay', 'eat', '_no', 'bt_', 'e_y', 'uzz', 't_g', 'the', 'r_l', 'no_', 'the', '_in', 'at_', 'n_m', '_th', 'dou', 't_i', 'her', 'hat', 'ngl', 'er_', 'ere', 'rea', 'e_d', 'lik', 'le_', 'puz', 'yer', 'was', 'ing', 'o_s', 'e_w', 'hal', '_pu', '_sh', 's_n', 'pla', 'sin', 'my_', 're_', '_so', 'lve', 'tha', '_li', 'min', 't_p', 've_', 'he_', '_si'], ["le_d","o_si","re_w"])

// 4 hints
solve(['ou_', '_pl', '_th', 'ind', 'gre', 'y_m', '_my', 'sol', '_gr', 'all', 'olv', '_wa', 'll_', 'as_', 'in_', 'sha', 'at_', 'e_t', 'ike', 'd_t', 'e_p', 'ubt', 'you', 'zle', 'ke_', 'zzl', 'oub', 'aye', 'u_s', '_yo', '_mi', 'l_s', 'gle', 'nd_', '_do', 'lay', 'eat', '_no', 'bt_', 'e_y', 'uzz', 't_g', 'the', 'r_l', 'no_', 'the', '_in', 'at_', 'n_m', '_th', 'dou', 't_i', 'her', 'hat', 'ngl', 'er_', 'ere', 'rea', 'e_d', 'lik', 'le_', 'puz', 'yer', 'was', 'ing', 'o_s', 'e_w', 'hal', '_pu', '_sh', 's_n', 'pla', 'sin', 'my_', 're_', '_so', 'lve', 'tha', '_li', 'min', 't_p', 've_', 'he_', '_si'], ["le_d","o_si","re_w", "bt_i"])

// 5 hints
solve(['ou_', '_pl', '_th', 'ind', 'gre', 'y_m', '_my', 'sol', '_gr', 'all', 'olv', '_wa', 'll_', 'as_', 'in_', 'sha', 'at_', 'e_t', 'ike', 'd_t', 'e_p', 'ubt', 'you', 'zle', 'ke_', 'zzl', 'oub', 'aye', 'u_s', '_yo', '_mi', 'l_s', 'gle', 'nd_', '_do', 'lay', 'eat', '_no', 'bt_', 'e_y', 'uzz', 't_g', 'the', 'r_l', 'no_', 'the', '_in', 'at_', 'n_m', '_th', 'dou', 't_i', 'her', 'hat', 'ngl', 'er_', 'ere', 'rea', 'e_d', 'lik', 'le_', 'puz', 'yer', 'was', 'ing', 'o_s', 'e_w', 'hal', '_pu', '_sh', 's_n', 'pla', 'sin', 'my_', 're_', '_so', 'lve', 'tha', '_li', 'min', 't_p', 've_', 'he_', '_si'], ["le_d","o_si","re_w", "bt_i", "he_p"])

