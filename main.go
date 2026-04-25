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

// evaluateBoard evaluates the board state.
//
// Three signals:
//
//  1. blockPenalty per filled cell — line clears are naturally rewarded.
//
//  2. emptyEdgePenalty per empty cell on the board boundary — mild constant
//     pressure to fill edges before they become isolated.
//
//  3. Per-region penalties (graph.go):
//     - Small regions (size 1–4): always penalised, heavily on edges/corners.
//     - Chain regions (elongation ≥ 3×, or 1 cell wide): penalised for sizes
//     up to 8, because thin channels need rare piece orientations to fill.
//     Edge/corner touching always adds a multiplier; the worst case is an
//     isolated or chain region wedged into a corner.
func evaluateBoard(board Board) int {
	const (
		// One line clear = 9 cells → +9×blockPenalty. Keep this the reference.
		blockPenalty = 3_000

		// Mild per-cell penalty for every empty cell on the board boundary.
		// Filling an edge cell saves this → edge placements are slightly preferred.
		emptyEdgePenalty   = 400
		emptyCornerPenalty = 700 // stacks on top of emptyEdgePenalty for corners

		// Per-region base penalties by size (always applied, compact or not).
		penaltySize1 = 50_000
		penaltySize2 = 20_000
		penaltySize3 = 9_000
		penaltySize4 = 3_500

		// Chain penalty: applied to regions of any size (up to 8) when the
		// region is thin/elongated (isChain() == true). A 1×6 corridor or a
		// zigzag can only be filled by specific piece shapes, making them risky.
		penaltyChain = 6_000

		// Extra when a penalised region touches the board boundary.
		// Edge cells have one fewer neighbour direction, making escape harder.
		extraEdge   = 250_000
		extraCorner = 200_000 // stacks on top of extraEdge

		// Penalties for small isolated groups of *filled* cells.
		// Smaller than empty-isolation penalties: a stray filled cell won't
		// block placement, but it's wasted until the rest of its row/col/box fills.
		penaltyFilledSize1 = 7_000
		penaltyFilledSize2 = 3_000
		penaltyFilledSize3 = 1_200
	)

	score := 0

	// Signal 1 + 2: per-cell pass.
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] == 1 {
				score -= blockPenalty
				continue
			}
			// Empty cell on the board boundary.
			if i == 0 || i == 8 || j == 0 || j == 8 {
				score -= emptyEdgePenalty
				if (i == 0 || i == 8) && (j == 0 || j == 8) {
					score -= emptyCornerPenalty
				}
			}
		}
	}

	// Signal 3: per-region penalties.
	for _, r := range emptyRegions(board) {
		penalised := false

		// Small compact regions are always dangerous.
		switch r.Size {
		case 1:
			score -= penaltySize1
			penalised = true
		case 2:
			score -= penaltySize2
			penalised = true
		case 3:
			score -= penaltySize3
			penalised = true
		case 4:
			score -= penaltySize4
			penalised = true
		}

		// Thin/chain regions up to size 8: hard to fill regardless of total size.
		if r.Size <= 8 && r.isChain() {
			score -= penaltyChain
			penalised = true
		}

		// Edge/corner multiplier for any penalised region.
		if penalised {
			if r.OnEdge {
				score -= extraEdge
			}
			if r.OnCorner {
				score -= extraCorner
			}
		}
	}

	// Signal 4: penalties for small isolated groups of filled cells.
	for _, r := range filledRegions(board) {
		switch r.Size {
		case 1:
			score -= penaltyFilledSize1
		case 2:
			score -= penaltyFilledSize2
		case 3:
			score -= penaltyFilledSize3
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
