package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

// Shape represents a game piece with a grid, height, and width
type Shape struct {
	ID     int
	Height int
	Width  int
	Grid   [][]int
}

// Move represents a move with shape ID, row, and column
type Move struct {
	ShapeID int
	Row     int
	Col     int
}

// shapes is a map of shape IDs to Shape structs, translated from shapes.py
var shapes = map[int]Shape{
	100: {ID: 100, Height: 1, Width: 1, Grid: [][]int{{1}}},
	200: {ID: 200, Height: 1, Width: 2, Grid: [][]int{{1, 1}}},
	201: {ID: 201, Height: 2, Width: 1, Grid: [][]int{{1}, {1}}},
	202: {ID: 202, Height: 2, Width: 2, Grid: [][]int{{0, 1}, {1, 0}}},
	203: {ID: 203, Height: 2, Width: 2, Grid: [][]int{{1, 0}, {0, 1}}},
	300: {ID: 300, Height: 1, Width: 3, Grid: [][]int{{1, 1, 1}}},
	301: {ID: 301, Height: 2, Width: 2, Grid: [][]int{{0, 1}, {1, 1}}},
	302: {ID: 302, Height: 2, Width: 2, Grid: [][]int{{1, 0}, {1, 1}}},
	303: {ID: 303, Height: 3, Width: 1, Grid: [][]int{{1}, {1}, {1}}},
	304: {ID: 304, Height: 2, Width: 2, Grid: [][]int{{1, 1}, {0, 1}}},
	305: {ID: 305, Height: 2, Width: 2, Grid: [][]int{{1, 1}, {1, 0}}},
	306: {ID: 306, Height: 3, Width: 3, Grid: [][]int{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}},
	307: {ID: 307, Height: 3, Width: 3, Grid: [][]int{{0, 0, 1}, {0, 1, 0}, {1, 0, 0}}},
	400: {ID: 400, Height: 2, Width: 2, Grid: [][]int{{1, 1}, {1, 1}}},
	401: {ID: 401, Height: 4, Width: 1, Grid: [][]int{{1}, {1}, {1}, {1}}},
	402: {ID: 402, Height: 2, Width: 3, Grid: [][]int{{1, 1, 1}, {1, 0, 0}}},
	403: {ID: 403, Height: 2, Width: 3, Grid: [][]int{{0, 1, 1}, {1, 1, 0}}},
	404: {ID: 404, Height: 3, Width: 2, Grid: [][]int{{1, 0}, {1, 1}, {1, 0}}},
	405: {ID: 405, Height: 2, Width: 3, Grid: [][]int{{1, 1, 0}, {0, 1, 1}}},
	406: {ID: 406, Height: 2, Width: 3, Grid: [][]int{{1, 0, 0}, {1, 1, 1}}},
	407: {ID: 407, Height: 1, Width: 4, Grid: [][]int{{1, 1, 1, 1}}},
	408: {ID: 408, Height: 3, Width: 2, Grid: [][]int{{1, 1}, {0, 1}, {0, 1}}},
	409: {ID: 409, Height: 3, Width: 2, Grid: [][]int{{0, 1}, {1, 1}, {0, 1}}},
	410: {ID: 410, Height: 3, Width: 2, Grid: [][]int{{1, 0}, {1, 1}, {0, 1}}},
	411: {ID: 411, Height: 2, Width: 3, Grid: [][]int{{0, 0, 1}, {1, 1, 1}}},
	412: {ID: 412, Height: 2, Width: 3, Grid: [][]int{{1, 1, 1}, {0, 0, 1}}},
	413: {ID: 413, Height: 3, Width: 2, Grid: [][]int{{0, 1}, {1, 1}, {1, 0}}},
	414: {ID: 414, Height: 2, Width: 3, Grid: [][]int{{0, 1, 0}, {1, 1, 1}}},
	415: {ID: 415, Height: 3, Width: 2, Grid: [][]int{{0, 1}, {0, 1}, {1, 1}}},
	416: {ID: 416, Height: 2, Width: 3, Grid: [][]int{{1, 1, 1}, {0, 1, 0}}},
	417: {ID: 417, Height: 4, Width: 4, Grid: [][]int{{1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1}}},
	418: {ID: 418, Height: 4, Width: 4, Grid: [][]int{{0, 0, 0, 1}, {0, 0, 1, 0}, {0, 1, 0, 0}, {1, 0, 0, 0}}},
	419: {ID: 419, Height: 3, Width: 2, Grid: [][]int{{1, 1}, {1, 0}, {1, 0}}},
	500: {ID: 500, Height: 3, Width: 3, Grid: [][]int{{0, 0, 1}, {0, 0, 1}, {1, 1, 1}}},
	501: {ID: 501, Height: 3, Width: 3, Grid: [][]int{{1, 0, 0}, {1, 1, 1}, {1, 0, 0}}},
	502: {ID: 502, Height: 3, Width: 3, Grid: [][]int{{0, 1, 0}, {1, 1, 1}, {0, 1, 0}}},
	503: {ID: 503, Height: 3, Width: 3, Grid: [][]int{{1, 1, 1}, {1, 0, 0}, {1, 0, 0}}},
	504: {ID: 504, Height: 3, Width: 3, Grid: [][]int{{1, 1, 1}, {0, 0, 1}, {0, 0, 1}}},
	505: {ID: 505, Height: 1, Width: 5, Grid: [][]int{{1, 1, 1, 1, 1}}},
	506: {ID: 506, Height: 5, Width: 1, Grid: [][]int{{1}, {1}, {1}, {1}, {1}}},
	507: {ID: 507, Height: 3, Width: 3, Grid: [][]int{{1, 1, 1}, {0, 1, 0}, {0, 1, 0}}},
	508: {ID: 508, Height: 3, Width: 3, Grid: [][]int{{1, 0, 0}, {1, 0, 0}, {1, 1, 1}}},
	509: {ID: 509, Height: 3, Width: 3, Grid: [][]int{{0, 0, 1}, {1, 1, 1}, {0, 0, 1}}},
	510: {ID: 510, Height: 3, Width: 3, Grid: [][]int{{0, 1, 0}, {0, 1, 0}, {1, 1, 1}}},
	511: {ID: 511, Height: 2, Width: 3, Grid: [][]int{{1, 0, 1}, {1, 1, 1}}},
	512: {ID: 512, Height: 2, Width: 3, Grid: [][]int{{1, 1, 1}, {1, 0, 1}}},
	513: {ID: 513, Height: 3, Width: 2, Grid: [][]int{{1, 1}, {1, 0}, {1, 1}}},
	514: {ID: 514, Height: 3, Width: 2, Grid: [][]int{{1, 1}, {0, 1}, {1, 1}}},
}

// Board is a 9x9 grid
type Board [9][9]int

// copyBoard creates a deep copy of the board
func copyBoard(board Board) Board {
	newBoard := board
	return newBoard
}

// getAvailableMoves finds all possible moves for a given shape
func getAvailableMoves(board Board, shape Shape) []Move {
	var moves []Move
	for row := 0; row <= 9-shape.Height; row++ {
		for col := 0; col <= 9-shape.Width; col++ {
			if isValidMove(board, shape, row, col) {
				moves = append(moves, Move{ShapeID: shape.ID, Row: row, Col: col})
			}
		}
	}
	return moves
}

// isValidMove checks if a move is valid
func isValidMove(board Board, shape Shape, row, col int) bool {
	// This is unnecessary check, since the getAvailableMoves
	// function returns only moves that do not go beyond the boundaries of the board.
	if row+shape.Height > 9 || col+shape.Width > 9 {
		return false
	}

	for r := 0; r < shape.Height; r++ {
		for c := 0; c < shape.Width; c++ {
			if shape.Grid[r][c] == 1 && board[row+r][col+c] != 0 {
				return false
			}
		}
	}
	return true
}

// applyMoveToBoard applies a move to the board and removes completed regions
func applyMoveToBoard(board Board, move Move) Board {
	shapeObj := shapes[move.ShapeID]
	for r := 0; r < shapeObj.Height; r++ {
		for c := 0; c < shapeObj.Width; c++ {
			if shapeObj.Grid[r][c] == 1 {
				board[move.Row+r][move.Col+c] = 1
			}
		}
	}
	return checkAndRemoveCompletedRegions(board)
}

// checkAndRemoveCompletedRegions removes filled 3x3 regions, rows, and columns
func checkAndRemoveCompletedRegions(board Board) Board {
	// Check 3x3 regions
	for i := 0; i < 9; i += 3 {
		for j := 0; j < 9; j += 3 {
			allFilled := true
			for x := 0; x < 3; x++ {
				for y := 0; y < 3; y++ {
					if board[i+x][j+y] != 1 {
						allFilled = false
						break
					}
				}
				if !allFilled {
					break
				}
			}
			if allFilled {
				for x := range 3 {
					for y := range 3 {
						board[i+x][j+y] = 2 // Temporary marker (equivalent to 'T')
					}
				}
			}
		}
	}

	// Check rows
	for i := range 9 {
		allFilled := true
		for j := range 9 {
			if board[i][j] != 1 && board[i][j] != 2 {
				allFilled = false
				break
			}
		}
		if allFilled {
			for j := range 9 {
				board[i][j] = 2
			}
		}
	}

	// Check columns
	for j := range 9 {
		allFilled := true
		for i := range 9 {
			if board[i][j] != 1 && board[i][j] != 2 {
				allFilled = false
				break
			}
		}
		if allFilled {
			for i := range 9 {
				board[i][j] = 2
			}
		}
	}

	// Replace temporary markers with 0
	for i := range 9 {
		for j := range 9 {
			if board[i][j] == 2 {
				board[i][j] = 0
			}
		}
	}
	return board
}

// evaluateBoard evaluates the board state

func evaluateBoard(board Board) int {
	const (
		PENALTY_PER_BLOCK     = 10000 // Penalty for each filled cell
		PENALTY_PER_PERIMETER = 200   // Penalty per perimeter unit
		PENALTY_JAGGED_EDGE   = 500   // Penalty for filled cells with empty neighbors
		PENALTY_SINGLE_EMPTY  = 500   // Penalty for empty cells between two filled cells
		BONUS_FREE_CUBE       = 1000  // Bonus for each fully empty 3x3 cube
	)

	score := 0

	// 1. Penalty for each filled block (cell)
	filledCount := 0
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] == 1 {
				filledCount++
			}
		}
	}
	score -= filledCount * PENALTY_PER_BLOCK

	// 2. Penalty for perimeter of filled shapes
	perimeter := 0
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] != 1 {
				continue
			}
			// Count open sides (up, down, left, right)
			sides := 4
			if i > 0 && board[i-1][j] == 1 { // Up
				sides--
			}
			if i < 8 && board[i+1][j] == 1 { // Down
				sides--
			}
			if j > 0 && board[i][j-1] == 1 { // Left
				sides--
			}
			if j < 8 && board[i][j+1] == 1 { // Right
				sides--
			}
			perimeter += sides
		}
	}
	score -= perimeter * PENALTY_PER_PERIMETER

	// 3. Penalty for jagged edges (filled cells with empty neighbors)
	jaggedCount := 0
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] != 1 {
				continue
			}
			// Check if any neighbor is empty
			if (i > 0 && board[i-1][j] == 0) || // Up
				(i < 8 && board[i+1][j] == 0) || // Down
				(j > 0 && board[i][j-1] == 0) || // Left
				(j < 8 && board[i][j+1] == 0) { // Right
				jaggedCount++
			}
		}
	}
	score -= jaggedCount * PENALTY_JAGGED_EDGE

	// 4. Penalty for single empty cells between two filled cells
	singleEmptyCount := 0
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] != 0 {
				continue
			}
			// Check vertical: empty cell with filled cells above and below
			if i > 0 && i < 8 && board[i-1][j] == 1 && board[i+1][j] == 1 {
				singleEmptyCount++
			}
			// Check horizontal: empty cell with filled cells left and right
			if j > 0 && j < 8 && board[i][j-1] == 1 && board[i][j+1] == 1 {
				singleEmptyCount++
			}
		}
	}
	score -= singleEmptyCount * PENALTY_SINGLE_EMPTY

	// 5. Bonus for fully empty 3x3 cubes
	freeCubeCount := 0
	for iBase := 0; iBase <= 6; iBase += 3 {
		for jBase := 0; jBase <= 6; jBase += 3 {
			isEmpty := true
			for i := iBase; i < iBase+3; i++ {
				for j := jBase; j < jBase+3; j++ {
					if board[i][j] != 0 {
						isEmpty = false
						break
					}
				}
				if !isEmpty {
					break
				}
			}
			if isEmpty {
				freeCubeCount++
			}
		}
	}
	score += freeCubeCount * BONUS_FREE_CUBE

	// Invert score: higher is better
	return score
}

// selectBestMove finds the best move for a given shape

// visualizeMove displays the board with the move marked
func visualizeMove(board Board, move Move) {
	visualBoard := copyBoard(board)
	shapeObj := shapes[move.ShapeID]
	for r := 0; r < shapeObj.Height; r++ {
		for c := 0; c < shapeObj.Width; c++ {
			if shapeObj.Grid[r][c] == 1 {
				visualBoard[move.Row+r][move.Col+c] = 'X'
			}
		}
	}
	for _, row := range visualBoard {
		for _, cell := range row {
			if cell == 'X' {
				fmt.Print("X ")
			} else {
				fmt.Printf("%d ", cell)
			}

		}
		fmt.Println()
	}
	fmt.Println()
}

// tripleMovesInOrder evaluates moves for a given shape order
func tripleMovesInOrder(board Board, order []Shape) ([]Move, int) {
	var boardsAfterMove1 [][2]any
	for _, move := range getAvailableMoves(board, order[0]) {
		newBoard := applyMoveToBoard(copyBoard(board), move)
		boardsAfterMove1 = append(boardsAfterMove1, [2]any{newBoard, move})
	}

	var boardsAfterMove2 [][2]any
	for _, b := range boardsAfterMove1 {
		board := b[0].(Board)
		move1 := b[1].(Move)
		for _, move := range getAvailableMoves(board, order[1]) {
			newBoard := applyMoveToBoard(copyBoard(board), move)
			boardsAfterMove2 = append(boardsAfterMove2, [2]any{newBoard, []Move{move1, move}})
		}
	}

	maxScore := -1 << 31
	var realMoves []Move
	for _, b := range boardsAfterMove2 {
		board := b[0].(Board)
		moves := b[1].([]Move)
		for _, move := range getAvailableMoves(board, order[2]) {
			newBoard := applyMoveToBoard(copyBoard(board), move)
			score := evaluateBoard(newBoard)
			if score > maxScore {
				maxScore = score
				realMoves = append(moves, move)
			}
		}
	}
	return realMoves, maxScore
}

// goodAlg finds the best sequence of three moves
func goodAlg(board Board, shapes []Shape) []Move {
	maxScore := -1 << 31
	var bestMoves []Move
	possibleOrders := [][]Shape{
		{shapes[0], shapes[1], shapes[2]},
		{shapes[0], shapes[2], shapes[1]},
		{shapes[1], shapes[2], shapes[0]},
		{shapes[1], shapes[0], shapes[2]},
		{shapes[2], shapes[0], shapes[1]},
		{shapes[2], shapes[1], shapes[0]},
	}
	for _, order := range possibleOrders {
		result, score := tripleMovesInOrder(copyBoard(board), order)
		if score > maxScore {
			maxScore = score
			bestMoves = result
		}
	}
	return bestMoves
}

func main() {
	var board Board // 9x9 board initialized to zeros
	board = [9][9]int{
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
		{0, 0, 0, 0, 0, 0, 0, 0, 0},
	}
	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("shape_id = ")
		scanner.Scan()
		id1, _ := strconv.Atoi(scanner.Text())
		fmt.Print("shape_id = ")
		scanner.Scan()
		id2, _ := strconv.Atoi(scanner.Text())
		fmt.Print("shape_id = ")
		scanner.Scan()
		id3, _ := strconv.Atoi(scanner.Text())

		myShapes := []Shape{shapes[id1], shapes[id2], shapes[id3]}
		copyBoard := copyBoard(board)

		moves := goodAlg(copyBoard, myShapes)

		fmt.Println("Best moveS:")
		fmt.Println("Move 1:")
		visualizeMove(board, moves[0])
		board = applyMoveToBoard(board, moves[0])
		fmt.Println("Move 2:")
		visualizeMove(board, moves[1])
		board = applyMoveToBoard(board, moves[1])
		fmt.Println("Move 3:")
		visualizeMove(board, moves[2])
		board = applyMoveToBoard(board, moves[2])
	}
}
