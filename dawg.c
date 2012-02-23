#include <stdio.h>
#include <stdlib.h>

// Dawg
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

// Board
#define HORIZONTAL 1
#define VERTICAL 2

typedef struct {
	int width;
	int height;
	int start;
	int *letterMultiplier;
	int *wordMultiplier;
	char *tiles;
} Board;

typedef struct {
	int index;
	int direction;
	char tiles[16];
} Move;

int _generateMoves(
		Move *moves,
		int maxMoves,
		int moveIndex,
		Board *board,
		int *tileCounts,
		int wildCount,
		int x,
		int y,
		char *tiles,
		int tileIndex,
		int dawgIndex)
{
}

int generateMoves(
		Move *moves,
		int maxMoves,
		Board *board,
		int *tileCounts,
		int wildCount)
{
	int result = 0;
	for (int y = 0; y < board->height; y++) {
		for (int x = 0; x < board->width; x++) {
			for (int direction = 1; direction <= 2; direction++) {
				int dx = direction == HORIZONTAL ? 1 : 0;
				int dy = direction == HORIZONTAL ? 0 : 1;
			}
		}
	}
	return result;
}

// Main
int main(int argc, char* argv[]) {
    init("files/twl.dawg");
    uninit();
    return 0;
}
