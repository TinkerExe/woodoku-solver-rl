package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
)

func randomThreePieces() []Shape {
	ids := make([]int, 0, len(shapes))
	for id := range shapes {
		ids = append(ids, id)
	}
	result := make([]Shape, 3)
	for i := range 3 {
		result[i] = shapes[ids[rand.Intn(len(ids))]]
	}
	return result
}

// applyMoveGetCleared applies a move and returns the updated board and number of cleared cells.
func applyMoveGetCleared(board Board, move Move) (Board, int) {
	shapeObj := shapes[move.ShapeID]
	boardAfterPiece := board
	for r := range shapeObj.Height {
		for c := range shapeObj.Width {
			if shapeObj.Grid[r][c] == 1 {
				boardAfterPiece[move.Row+r][move.Col+c] = 1
			}
		}
	}
	newBoard := checkAndRemoveCompletedRegions(boardAfterPiece)
	cleared := 0
	for i := range 9 {
		for j := range 9 {
			if boardAfterPiece[i][j] == 1 && newBoard[i][j] == 0 {
				cleared++
			}
		}
	}
	return newBoard, cleared
}

func printBoard(board Board) {
	for _, row := range board {
		for _, cell := range row {
			if cell == 1 {
				fmt.Print("■ ")
			} else {
				fmt.Print("· ")
			}
		}
		fmt.Println()
	}
	fmt.Println()
}

func runGame(iterative bool) {
	var board Board
	totalCleared := 0
	turns := 0
	scanner := bufio.NewScanner(os.Stdin)

	for {
		turns++
		pack := randomThreePieces()
		moves := goodAlg(board, pack)

		if len(moves) < 3 {
			fmt.Printf("\nGame over!\nTurns completed: %d | Total cells cleared: %d\n", turns-1, totalCleared)
			return
		}

		if iterative {
			fmt.Printf("=== Turn %d ===\n", turns)
			fmt.Printf("Pieces: %d  %d  %d\n", pack[0].ID, pack[1].ID, pack[2].ID)
		}

		turnCleared := 0
		for idx, move := range moves {
			var cleared int
			board, cleared = applyMoveGetCleared(board, move)
			turnCleared += cleared

			if iterative {
				fmt.Printf("  Move %d: shape %-3d → row %d, col %d", idx+1, move.ShapeID, move.Row, move.Col)
				if cleared > 0 {
					fmt.Printf("  [+%d cleared]", cleared)
				}
				fmt.Println()
			}
		}
		totalCleared += turnCleared

		if iterative {
			if turnCleared > 0 {
				fmt.Printf("Board after turn (%d cells cleared this turn):\n", turnCleared)
			} else {
				fmt.Println("Board after turn:")
			}
			printBoard(board)
			fmt.Print("Press Enter to continue...")
			scanner.Scan()
		}
	}
}
