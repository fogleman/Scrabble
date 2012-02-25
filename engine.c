#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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



#define MAX_RESULTS 4096
#define RACK_SIZE 7
#define BINGO 50
#define HORIZONTAL 1
#define VERTICAL 2
#define EMPTY '.'
#define WILD '?'
#define SKIP '-'
#define INDEX(board, x, y) ((y) * board->width + (x))
#define IS_EMPTY(board, x, y) (board->tiles[INDEX(board, (x), (y))] == EMPTY)
#define IS_LOWER(c) ((c) >= 'a' && (c) <= 'z')
#define IS_UPPER(c) ((c) >= 'A' && (c) <= 'Z')
#define LOWER(c) ((c) | 32)
#define UPPER(c) ((c) & ~32)
#define VALUE(board, c) (board->tileValue[IS_UPPER(c) ? 0 : ((c) - 'a' + 1)])

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

typedef struct {
    char tiles[16];
} Result;

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

int computeMove(Board *board, int x, int y, int dx, int dy, 
    Result *result, Move *move) {
    int mx = x;
    int my = y;
    int px = !dx;
    int py = !dy;
    int mainScore = 0;
    int subScores = 0;
    int multiplier = 1;
    int placed = 0;
    int adjacent = 0;
    char mainWord[16];
    int mainWordIndex = 0;

    int ax = x - dx;
    int ay = y - dy;
    if (ax >= 0 && ay >= 0 && !IS_EMPTY(board, ax, ay)) {
        return 0;
    }

    int length = strlen(result->tiles);
    for (int i = 0; i < length; i++) {
        if (x < 0 || y < 0 || x >= board->width || y >= board->height) {
            return 0;
        }
        if (!adjacent) {
            adjacent = isAdjacent(board, x, y);
        }
        int index = INDEX(board, x, y);
        char tile = result->tiles[i];
        if (tile == SKIP) {
            tile = board->tiles[index];
            if (tile == EMPTY) {
                return 0;
            }
            mainWord[mainWordIndex++] = LOWER(tile);
            mainScore += VALUE(board, tile);
        }
        else {
            placed++;
            mainWord[mainWordIndex++] = LOWER(tile);
            mainScore += VALUE(board, tile) * board->letterMultiplier[index];
            multiplier *= board->wordMultiplier[index];

            int subScore = VALUE(board, tile) * board->letterMultiplier[index];
            char subWord[16];
            int subWordIndex = 0;
            int sx = x - px;
            int sy = y - py;
            while (sx >= 0 && sy >= 0) {
                if (IS_EMPTY(board, sx, sy)) {
                    break;
                }
                sx -= px;
                sy -= py;
            }
            sx += px;
            sy += py;
            while (sx < board->width && sy < board->height) {
                if (sx == x && sy == y) {
                    subWord[subWordIndex++] = LOWER(tile);
                }
                else {
                    if (IS_EMPTY(board, sx, sy)) {
                        break;
                    }
                    char subTile = board->tiles[INDEX(board, sx, sy)];
                    subWord[subWordIndex++] = LOWER(subTile);
                    subScore += VALUE(board, subTile);
                }
                sx += px;
                sy += py;
            }
            if (subWordIndex > 1) {
                subWord[subWordIndex++] = SENTINEL;
                if (!checkDawg(dawg, subWord, subWordIndex)) {
                    return 0;
                }
                subScore *= board->wordMultiplier[index];
                subScores += subScore;
            }
        }
        x += dx;
        y += dy;
    }

    if (x < board->width && y < board->height && !IS_EMPTY(board, x, y)) {
        return 0;
    }

    if (placed < 1 || placed > RACK_SIZE || !adjacent) {
        return 0;
    }

    mainWord[mainWordIndex++] = SENTINEL;
    if (!checkDawg(dawg, mainWord, mainWordIndex)) {
        return 0;
    }

    mainScore *= multiplier;
    int score = mainScore + subScores;
    if (placed == RACK_SIZE) {
        score += BINGO;
    }
    move->score = score;
    return 1;
}

int _generateMoves(Board *board, int x, int y, int dx, int dy, 
    int *letterCounts, int wildCount, int minTiles, int dawgIndex, 
    char *path, int pathIndex, Result *results, int resultIndex) {
    if (resultIndex == MAX_RESULTS) {
        return resultIndex;
    }
    if (pathIndex >= minTiles) {
        int link = getDawgRecord(dawg, dawgIndex, SENTINEL);
        if (link != FAILED) {
            path[pathIndex] = '\0';
            strcpy(results[resultIndex++].tiles, path);
        }
    }
    if (x >= board->width || y >= board->height) {
        return resultIndex;
    }
    int index = INDEX(board, x, y);
    char tile = board->tiles[index];
    if (tile == EMPTY) {
        for (int i = 0; i < 26; i++) {
            if (letterCounts[i] || wildCount) {
                tile = 'a' + i;
                int link = getDawgRecord(dawg, dawgIndex, tile);
                if (link != FAILED) {
                    link = DAWG_LINK(dawg[link]);
                    if (letterCounts[i]) {
                        letterCounts[i]--;
                        path[pathIndex] = tile;
                        resultIndex = _generateMoves(board, x + dx, y + dy, 
                            dx, dy, letterCounts, wildCount, minTiles, link, 
                            path, pathIndex + 1, results, resultIndex);
                        letterCounts[i]++;
                    }
                    if (wildCount) {
                        wildCount--;
                        path[pathIndex] = UPPER(tile);
                        resultIndex = _generateMoves(board, x + dx, y + dy, 
                            dx, dy, letterCounts, wildCount, minTiles, link, 
                            path, pathIndex + 1, results, resultIndex);
                        wildCount++;
                    }
                }
            }
        }
    }
    else {
        int link = getDawgRecord(dawg, dawgIndex, LOWER(tile));
        if (link != FAILED) {
            link = DAWG_LINK(dawg[link]);
            path[pathIndex] = SKIP;
            resultIndex = _generateMoves(board, x + dx, y + dy, dx, dy, 
                letterCounts, wildCount, minTiles, link, path, pathIndex + 1, 
                results, resultIndex);
        }
    }
    return resultIndex;
}

int generateMoves(Board *board, char *tiles, int tileCount, 
    Move *moves, int maxMoves) {
    int letterCounts[26] = {0};
    int wildCount = 0;
    for (int i = 0; i < tileCount; i++) {
        char c = tiles[i];
        if (c == WILD) {
            wildCount++;
        }
        else {
            letterCounts[c - 'a']++;
        }
    }
    int hstarts[board->width * board->height];
    int vstarts[board->width * board->height];
    getHorizontalStarts(board, tileCount, hstarts);
    getVerticalStarts(board, tileCount, vstarts);
    Result results[MAX_RESULTS];
    int moveCount = 0;
    for (int y = 0; y < board->height; y++) {
        for (int x = 0; x < board->width; x++) {
            int index = INDEX(board, x, y);
            char path[16];
            int minTiles;
            minTiles = hstarts[index];
            if (minTiles) {
                int resultIndex = _generateMoves(board, x, y, 1, 0, 
                    letterCounts, wildCount, minTiles, 0, path, 0, results, 0);
                for (int i = 0; i < resultIndex; i++) {
                    Result *result = results + i;
                    Move *move = moves + moveCount;
                    if (computeMove(board, x, y, 1, 0, result, move)) {
                        move->x = x;
                        move->y = y;
                        move->direction = HORIZONTAL;
                        strcpy(move->tiles, result->tiles);
                        moveCount++;
                        if (moveCount == maxMoves) {
                            return moveCount;
                        }
                    }
                }
            }
            minTiles = vstarts[index];
            if (minTiles) {
                int resultIndex = _generateMoves(board, x, y, 0, 1, 
                    letterCounts, wildCount, minTiles, 0, path, 0, results, 0);
                for (int i = 0; i < resultIndex; i++) {
                    Result *result = results + i;
                    Move *move = moves + moveCount;
                    if (computeMove(board, x, y, 0, 1, result, move)) {
                        move->x = x;
                        move->y = y;
                        move->direction = VERTICAL;
                        strcpy(move->tiles, result->tiles);
                        moveCount++;
                        if (moveCount == maxMoves) {
                            return moveCount;
                        }
                    }
                }
            }
        }
    }
    return moveCount;
}

void doMove(Board *board, Move *move) {
    int x = move->x;
    int y = move->y;
    int dx = move->direction == HORIZONTAL ? 1 : 0;
    int dy = move->direction == HORIZONTAL ? 0 : 1;
    int length = strlen(move->tiles);
    for (int i = 0; i < length; i++) {
        char tile = move->tiles[i];
        if (tile != SKIP) {
            board->tiles[INDEX(board, x, y)] = tile;
        }
        x += dx;
        y += dy;
    }
}
