package main

import (
	"bufio"
	"fmt"
	"math"
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
	var newBoard Board
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			newBoard[i][j] = board[i][j]
		}
	}
	return newBoard
}

// getAvailableMoves finds all possible moves for a given shape
func getAvailableMoves(board Board, shape Shape) []Move {
	var moves []Move
	for shapeID, shapeObj := range shapes {
		if shapeObj.ID == shape.ID {
			for row := 0; row <= 9-shape.Height; row++ {
				for col := 0; col <= 9-shape.Width; col++ {
					if isValidMove(board, shape, row, col) {
						moves = append(moves, Move{ShapeID: shapeID, Row: row, Col: col})
					}
				}
			}
		}
	}
	return moves
}

// isValidMove checks if a move is valid
func isValidMove(board Board, shape Shape, row, col int) bool {
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
				for x := 0; x < 3; x++ {
					for y := 0; y < 3; y++ {
						board[i+x][j+y] = 2 // Temporary marker (equivalent to 'T')
					}
				}
			}
		}
	}

	// Check rows
	for i := 0; i < 9; i++ {
		allFilled := true
		for j := 0; j < 9; j++ {
			if board[i][j] != 1 && board[i][j] != 2 {
				allFilled = false
				break
			}
		}
		if allFilled {
			for j := 0; j < 9; j++ {
				board[i][j] = 2
			}
		}
	}

	// Check columns
	for j := 0; j < 9; j++ {
		allFilled := true
		for i := 0; i < 9; i++ {
			if board[i][j] != 1 && board[i][j] != 2 {
				allFilled = false
				break
			}
		}
		if allFilled {
			for i := 0; i < 9; i++ {
				board[i][j] = 2
			}
		}
	}

	// Replace temporary markers with 0
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] == 2 {
				board[i][j] = 0
			}
		}
	}
	return board
}

// evaluateBoard evaluates the board state

func evaluateBoard(board Board) int {
	var compactness, occupiedCells, edgeCells, emptyNeighbors, occupiedNeighbors float64

	// Check for adjacent filled cells
	for i := 0; i < 8; i++ {
		for j := 0; j < 8; j++ {
			if board[i][j] == 1 && board[i+1][j] == 1 && board[i][j+1] == 1 {
				compactness += 1
			}
		}
	}

	// Evaluate each cell
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if board[i][j] == 1 {
				occupiedCells += 1
				if i == 0 || i == 8 || j == 0 || j == 8 {
					edgeCells += 1
				} else {
					counter := 0
					if i < 8 && board[i+1][j] == 0 {
						counter++
					}
					if j < 8 && board[i][j+1] == 0 {
						counter++
					}
					if i > 0 && board[i-1][j] == 0 {
						counter++
					}
					if j > 0 && board[i][j-1] == 0 {
						counter++
					}
					if counter >= 3 {
						emptyNeighbors += math.Pow(4, float64(counter))
					}
				}
			} else {
				counter := 0
				if i < 8 && board[i+1][j] == 1 {
					counter++
				}
				if j < 8 && board[i][j+1] == 1 {
					counter++
				}
				if i > 0 && board[i-1][j] == 1 {
					counter++
				}
				if j > 0 && board[i][j-1] == 1 {
					counter++
				}
				if counter >= 2 {
					occupiedNeighbors += math.Pow(4, float64(counter))
				}
			}
		}
	}

	// Combine criteria with fixed weights
	score := int(
		1.8867064192066485*compactness +
			(-901.8024822913344)*occupiedCells +
			46.791621056031374*edgeCells +
			(-0.3287090910678472)*emptyNeighbors +
			(-1.383686993845287)*occupiedNeighbors,
	)
	return score
}

// isGameOver checks if no moves are possible for a shape
func isGameOver(board Board, shape Shape) bool {
	return len(getAvailableMoves(board, shape)) == 0
}

// placeShapeOnBoard places a shape on the board and applies the move
func placeShapeOnBoard(board Board, move Move) Board {
	shape := shapes[move.ShapeID]
	for r := 0; r < shape.Height; r++ {
		for c := 0; c < shape.Width; c++ {
			if shape.Grid[r][c] == 1 {
				board[move.Row+r][move.Col+c] = 1
			}
		}
	}
	return applyMoveToBoard(board, move)
}

// selectBestMove finds the best move for a given shape
func selectBestMove(board Board, shape Shape) (int, Move) {
	bestScore := -1 << 31 // Equivalent to float('-inf')
	var bestMove Move

	for _, move := range getAvailableMoves(board, shape) {
		tempBoard := copyBoard(board)
		tempBoard = placeShapeOnBoard(tempBoard, move)
		score := evaluateBoard(tempBoard)
		if score > bestScore {
			bestScore = score
			bestMove = move
		}
	}
	return bestScore, bestMove
}

// visualizeMove displays the board with the move marked
func visualizeMove(board Board, move Move, myShapes []Shape) {
	visualBoard := copyBoard(board)
	shapeObj := shapes[move.ShapeID] // Use global shapes map
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
	var boardsAfterMove1 [][2]interface{}
	for _, move := range getAvailableMoves(board, order[0]) {
		newBoard := applyMoveToBoard(copyBoard(board), move)
		boardsAfterMove1 = append(boardsAfterMove1, [2]interface{}{newBoard, move})
	}

	var boardsAfterMove2 [][2]interface{}
	for _, b := range boardsAfterMove1 {
		board := b[0].(Board)
		move1 := b[1].(Move)
		for _, move := range getAvailableMoves(board, order[1]) {
			newBoard := applyMoveToBoard(copyBoard(board), move)
			boardsAfterMove2 = append(boardsAfterMove2, [2]interface{}{newBoard, []Move{move1, move}})
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

// startGame2 runs the game loop
func startGame2(board Board) {
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
		visualizeMove(board, moves[0], myShapes)
		board = applyMoveToBoard(board, moves[0])
		fmt.Println("Move 2:")
		visualizeMove(board, moves[1], myShapes)
		board = applyMoveToBoard(board, moves[1])
		fmt.Println("Move 3:")
		visualizeMove(board, moves[2], myShapes)
		board = applyMoveToBoard(board, moves[2])
	}
}

func main() {
	var realBoard Board // 9x9 board initialized to zeros
	realBoard = [9][9]int{
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
	startGame2(realBoard)
}
