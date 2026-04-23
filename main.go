package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"
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
		PENALTY_PER_BLOCK     = 10000 // penalty for each filled cell
		PENALTY_PER_PERIMETER = 500   // prefer compact placements
		BONUS_FREE_CUBE       = 300   // small bonus for empty 3x3 box — kept low to avoid corner-hoarding
		BONUS_LINE_6          = 200   // bonus for row/col/box with 6/9 filled
		BONUS_LINE_7          = 900   // bonus for row/col/box with 7/9 filled
		BONUS_LINE_8          = 5000  // bonus for row/col/box with 8/9 filled

		// Isolated empty region penalties (by connected-region size).
		PENALTY_TRAPPED_1 = 25000
		PENALTY_TRAPPED_2 = 10000
		PENALTY_TRAPPED_3 = 4000
		PENALTY_TRAPPED_4 = 1500
		PENALTY_TRAPPED_5 = 500

		// Extra penalty for empty cells with exactly 3 sides blocked by filled cells
		// OR board walls. Such cells are "almost trapped" — one more neighbour fills
		// and they become permanently unreachable. The 4-sided case is already
		// covered by PENALTY_TRAPPED_1 via flood-fill.
		PENALTY_ACCESS_3 = 3000
	)

	score := 0

	// 1. Penalty for each filled block
	filledCount := 0
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] == 1 {
				filledCount++
			}
		}
	}
	score -= filledCount * PENALTY_PER_BLOCK

	// 2. Perimeter penalty (exposed edges facing empty cells or board boundary)
	perimeter := 0
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] != 1 {
				continue
			}
			sides := 4
			if i > 0 && board[i-1][j] == 1 {
				sides--
			}
			if i < 8 && board[i+1][j] == 1 {
				sides--
			}
			if j > 0 && board[i][j-1] == 1 {
				sides--
			}
			if j < 8 && board[i][j+1] == 1 {
				sides--
			}
			perimeter += sides
		}
	}
	score -= perimeter * PENALTY_PER_PERIMETER

	// 3. Isolated empty region penalty via flood-fill (4-connectivity).
	//    Regions fully enclosed by filled cells score highest penalty.
	//    Large open areas are not penalised (size > 5).
	var visited [9][9]bool
	var floodFill func(r, c int) int
	floodFill = func(r, c int) int {
		if r < 0 || r >= 9 || c < 0 || c >= 9 || visited[r][c] || board[r][c] != 0 {
			return 0
		}
		visited[r][c] = true
		return 1 + floodFill(r+1, c) + floodFill(r-1, c) + floodFill(r, c+1) + floodFill(r, c-1)
	}
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if !visited[i][j] && board[i][j] == 0 {
				size := floodFill(i, j)
				switch size {
				case 1:
					score -= PENALTY_TRAPPED_1
				case 2:
					score -= PENALTY_TRAPPED_2
				case 3:
					score -= PENALTY_TRAPPED_3
				case 4:
					score -= PENALTY_TRAPPED_4
				case 5:
					score -= PENALTY_TRAPPED_5
				}
			}
		}
	}

	// 4. Bonus for fully empty 3x3 boxes
	for iBase := 0; iBase <= 6; iBase += 3 {
		for jBase := 0; jBase <= 6; jBase += 3 {
			isEmpty := true
		outerCheck:
			for i := iBase; i < iBase+3; i++ {
				for j := jBase; j < jBase+3; j++ {
					if board[i][j] != 0 {
						isEmpty = false
						break outerCheck
					}
				}
			}
			if isEmpty {
				score += BONUS_FREE_CUBE
			}
		}
	}

	lineBonus := func(k int) int {
		switch k {
		case 8:
			return BONUS_LINE_8
		case 7:
			return BONUS_LINE_7
		case 6:
			return BONUS_LINE_6
		default:
			return 0
		}
	}

	// 5. Near-complete bonuses for rows, columns, and 3x3 boxes
	for i := range 9 {
		k := 0
		for j := range 9 {
			if board[i][j] == 1 {
				k++
			}
		}
		score += lineBonus(k)
	}
	for j := range 9 {
		k := 0
		for i := range 9 {
			if board[i][j] == 1 {
				k++
			}
		}
		score += lineBonus(k)
	}
	for iBase := 0; iBase <= 6; iBase += 3 {
		for jBase := 0; jBase <= 6; jBase += 3 {
			k := 0
			for i := iBase; i < iBase+3; i++ {
				for j := jBase; j < jBase+3; j++ {
					if board[i][j] == 1 {
						k++
					}
				}
			}
			score += lineBonus(k)
		}
	}

	// 6. Penalty for empty cells with 3 sides blocked (walls + filled cells).
	//    These are "pre-trapped" — one more filled neighbour makes them unreachable.
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] != 0 {
				continue
			}
			blocked := 0
			if i == 0 || board[i-1][j] == 1 {
				blocked++
			}
			if i == 8 || board[i+1][j] == 1 {
				blocked++
			}
			if j == 0 || board[i][j-1] == 1 {
				blocked++
			}
			if j == 8 || board[i][j+1] == 1 {
				blocked++
			}
			if blocked == 3 {
				score -= PENALTY_ACCESS_3
			}
		}
	}

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
			switch cell {
			case 'X':
				fmt.Print("▣ ")
			case 1:
				fmt.Print("■ ")
			default:
				fmt.Print("· ")
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

// runCVMode reads board+pieces from stdin repeatedly, outputs moves.
// Input per iteration: 9 lines of "0 1 0 ..." (board rows), then "id1 id2 id3".
// Output per iteration: 3 lines of "shapeID row col", then "DONE". Or "GAME_OVER".
func runCVMode() {
	scanner := bufio.NewScanner(os.Stdin)
	var board Board
	for {
		for i := 0; i < 9; i++ {
			if !scanner.Scan() {
				return
			}
			for j, f := range strings.Fields(scanner.Text()) {
				board[i][j], _ = strconv.Atoi(f)
			}
		}
		if !scanner.Scan() {
			return
		}
		fields := strings.Fields(scanner.Text())
		if len(fields) < 3 {
			return
		}
		id1, _ := strconv.Atoi(fields[0])
		id2, _ := strconv.Atoi(fields[1])
		id3, _ := strconv.Atoi(fields[2])

		s1, ok1 := shapes[id1]
		s2, ok2 := shapes[id2]
		s3, ok3 := shapes[id3]
		if !ok1 || !ok2 || !ok3 {
			fmt.Println("GAME_OVER")
			return
		}

		moves := goodAlg(board, []Shape{s1, s2, s3})
		if len(moves) < 3 {
			fmt.Println("GAME_OVER")
			return
		}
		for _, m := range moves {
			fmt.Printf("%d %d %d\n", m.ShapeID, m.Row, m.Col)
		}
		fmt.Println("DONE")
	}
}

func main() {
	modeAuto := flag.Bool("a", false, "Auto mode: play to completion and print result")
	modeIter := flag.Bool("i", false, "Iterative mode: show each turn, wait for Enter")
	modeCV := flag.Bool("cv", false, "CV mode: read board+pieces from stdin, output moves")
	flag.Parse()

	if *modeAuto {
		runGame(false)
		return
	}
	if *modeIter {
		runGame(true)
		return
	}
	if *modeCV {
		runCVMode()
		return
	}

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
