#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

//gcc -std=c99 -fpic -pie -fstack-protector-all -Wall -o phonebook phonebook.c

#define MAX_ENTRIES 10

typedef struct entry {
    bool active;
    char name[128];
    char number[10];
} entry_t;

void show_menu(){
    const char menu[] = "Phonebook\n"
    "---------------------\n"
    "1. Show contact\n"
    "2. Add contact\n"
    "3. Delete contact\n"
    "4. Exit\n"
    "> ";
    printf(menu);
}

int find_first_empty(entry_t list[]) {
    for (int i=0; i<MAX_ENTRIES; i++) {
        if (!list[i].active) return i;
    }
    return -1;
}

bool check_index(int index) {
    if (index < 0) {
        printf("Number parsing error\n");
        return true;
    }

    if ( (index >= MAX_ENTRIES) || (index < 0) ){
        printf("Index out of range 0-9.\n");
        return true;
    }

    return false;
}

void add_entry(entry_t list[]) {
    int empty = find_first_empty(list);
    if (empty == -1) {
        printf("Phonebook is full\n");
        return;
    }

    printf("Name: ");
    scanf("%127s", (char*)&list[empty].name);
    printf("Number: ");
    scanf("%s", (char*)&list[empty].number);
    list[empty].active = true;
    printf("Contant added with index %d\n", empty);
}

void remove_entry(entry_t list[]) {
    int number = 0;
    printf("Index of contact to delete: ");
    int recv = scanf("%d", &number);
    if (recv < 1) {
        printf("Phone number parsing error\n");
        return;
    }
    if ( check_index(number) ) return; 
    list[number].active = false;    
}

void show_entry(entry_t list[]) {
    int number = 0;
    printf("Type number of entry: ");
    int recv = scanf("%d", &number);
    if (recv < 1) {
        printf("Number parsing error\n");
        return;
    }
    if ( check_index(number) ) return;
    if (!list[number].active) {
        printf("Contact is inactive\n");
        return;
    }    

    printf("Name: ");
    printf(list[number].name);
    printf("\nNumber: ");
    printf(list[number].number);
    printf("\n");
}

int main() {
    entry_t list[MAX_ENTRIES];
    memset(list, 0, sizeof(list));
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);

    while (1) {
        show_menu();
        int choose = 0;
        scanf("%d", &choose);
        //if ( (choose < 1) || (choose > 3) ) return 1;

        switch(choose) {
            case 1:
                show_entry(list);
                break;
            case 2:
                add_entry(list);
                break;
            case 3:
                remove_entry(list);
                break;
            case 4:
                return 0;
                break;
            default:
                printf("Unknown function\n");
                return 0;
        }
    }
}