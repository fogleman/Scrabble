#include <stdio.h>
#include <stdlib.h>

#define SENTINEL '$'
#define FAILED 0xffffffff

#define DAWG_MORE(x) (x & 0x80000000)
#define DAWG_LETTER(x) ((x >> 24) & 0x7f)
#define DAWG_LINK(x) (x & 0xffffff)

typedef unsigned int DawgRecord;

DawgRecord* dawg;

char* loadFile(char* path) {
    FILE* file = fopen(path, "rb");
    fseek(file, 0, SEEK_END);
    int length = ftell(file);
    rewind(file);
    char* buffer = (char*)malloc(length);
    fread(buffer, 1, length, file);
    fclose(file);
    return buffer;
}

void init(char* dawgPath) {
    dawg = (DawgRecord*)loadFile(dawgPath);
}

void uninit() {
    free(dawg);
}

int getDawgRecord(DawgRecord* records, int index, char letter) {
    DawgRecord record;
    while (1) {
        record = records[index];
        if (DAWG_LETTER(record) == letter) {
            return index;
        }
        if (!DAWG_MORE(record)) {
            return FAILED;
        }
        index++;
    }
}

int checkDawg(DawgRecord* records, char* letters, int length) {
    int index = 0;
    for (int i = 0; i < length; i++) {
        index = getDawgRecord(records, index, letters[i]);
        if (index == FAILED) {
            return 0;
        }
        index = DAWG_LINK(records[index]);
    }
    return 1;
}


#define EMPTY '.'
#define INDEX(board, x, y) (y * board->width + x)
#define IS_EMPTY(board, x, y) (board->tiles[INDEX(board, x, y)] == EMPTY)

typedef struct {
	int width;
	int height;
	int start;
	int *letterMultiplier;
	int *wordMultiplier;
	int *tileValue;
	char *tiles;
} Board;

typedef struct {
	int x;
	int y;
	int direction;
	int score;
	char tiles[16];
} Move;

int isAdjacent(Board *board, int x, int y) {
	int index = INDEX(board, x, y);
	if (index == board->start) {
		return 1;
	}
	if (x > 0 && !IS_EMPTY(board, x - 1, y)) {
		return 1;
	}
	if (y > 0 && !IS_EMPTY(board, x, y - 1)) {
		return 1;
	}
	if (x < board->width - 2 && !IS_EMPTY(board, x + 1, y)) {
		return 1;
	}
	if (y < board->height - 2 && !IS_EMPTY(board, x, y + 1)) {
		return 1;
	}
	return 0;
}

void getHorizontalStarts(Board *board, int tileCount, int *result) {
	for (int y = 0; y < board->height; y++) {
		for (int x = 0; x < board->width; x++) {
			int index = INDEX(board, x, y);
			result[index] = 0;
			if (x > 0 && !IS_EMPTY(board, x - 1, y)) {
				continue;
			}
			if (IS_EMPTY(board, x, y)) {
				for (int i = 0; i < tileCount; i++) {
					if (x + i < board->width && isAdjacent(board, x + i, y)) {
						result[index] = i + 1;
						break;
					}
				}
			}
			else {
				result[index] = 1;
			}
		}
	}
}

void getVerticalStarts(Board *board, int tileCount, int *result) {
	for (int y = 0; y < board->height; y++) {
		for (int x = 0; x < board->width; x++) {
			int index = INDEX(board, x, y);
			result[index] = 0;
			if (y > 0 && !IS_EMPTY(board, x, y - 1)) {
				continue;
			}
			if (IS_EMPTY(board, x, y)) {
				for (int i = 0; i < tileCount; i++) {
					if (y + i < board->height && isAdjacent(board, x, y + i)) {
						result[index] = i + 1;
						break;
					}
				}
			}
			else {
				result[index] = 1;
			}
		}
	}
}

int main(int argc, char* argv[]) {
    init("files/twl.dawg");
    uninit();
    return 0;
}
