package main

import (
	"testing"
)

// ... (вставьте весь оригинальный код из <DOCUMENT> сюда, кроме main, чтобы тесты работали в том же пакете)

// Unit tests

func TestCopyBoard(t *testing.T) {
	original := Board{}
	original[0][0] = 1
	original[4][4] = 1

	copied := copyBoard(original)

	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			if copied[i][j] != original[i][j] {
				t.Errorf("copyBoard mismatch at [%d][%d]: got %d, want %d", i, j, copied[i][j], original[i][j])
			}
		}
	}

	// Modify copied and check original unchanged
	copied[0][0] = 0
	if original[0][0] != 1 {
		t.Errorf("Modifying copy affected original")
	}
}

func TestIsValidMove(t *testing.T) {
	tests := []struct {
		name  string
		board Board
		shape Shape
		row   int
		col   int
		want  bool
	}{
		{
			name:  "1x1 on empty board",
			board: Board{},
			shape: shapes[100],
			row:   0,
			col:   0,
			want:  true,
		},
		{
			name:  "1x1 on occupied cell",
			board: Board{{1, 0, 0, 0, 0, 0, 0, 0, 0}},
			shape: shapes[100],
			row:   0,
			col:   0,
			want:  false,
		},
		{
			name:  "2x1 vertical on empty",
			board: Board{},
			shape: shapes[201],
			row:   0,
			col:   0,
			want:  true,
		},
		{
			name:  "2x1 vertical overlapping",
			board: Board{{0, 0}, {1, 0}},
			shape: shapes[201],
			row:   0,
			col:   0,
			want:  false,
		},
		{
			name:  "Partial overlap",
			board: Board{{0, 1, 0}, {0, 0, 0}},
			shape: shapes[301], // 2x2 {{0,1},{1,1}}
			row:   0,
			col:   0,
			want:  false, // overlaps at [0][1]
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := isValidMove(tt.board, tt.shape, tt.row, tt.col)
			if got != tt.want {
				t.Errorf("isValidMove() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestGetAvailableMoves(t *testing.T) {
	tests := []struct {
		name      string
		board     Board
		shape     Shape
		wantCount int // expected number of moves
	}{
		{
			name:      "1x1 on empty board",
			board:     Board{},
			shape:     shapes[100],
			wantCount: 81, // 9x9
		},
		{
			name:      "1x2 horizontal on empty",
			board:     Board{},
			shape:     shapes[200],
			wantCount: 9 * 8, // rows 0-8, cols 0-7
		},
		{
			name:      "2x1 vertical on empty",
			board:     Board{},
			shape:     shapes[201],
			wantCount: 8 * 9, // rows 0-7, cols 0-8
		},
		{
			name:      "1x1 with one occupied",
			board:     Board{{1, 0, 0, 0, 0, 0, 0, 0, 0}},
			shape:     shapes[100],
			wantCount: 80,
		},
		{
			name:      "No moves for large shape on full board",
			board:     [9][9]int{{1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1, 1}},
			shape:     shapes[100],
			wantCount: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := getAvailableMoves(tt.board, tt.shape)
			if len(got) != tt.wantCount {
				t.Errorf("getAvailableMoves() len = %d, want %d", len(got), tt.wantCount)
			}
			// Optional: check all moves are valid
			for _, m := range got {
				if !isValidMove(tt.board, tt.shape, m.Row, m.Col) {
					t.Errorf("Invalid move in available: %+v", m)
				}
			}
		})
	}
}

func TestCheckAndRemoveCompletedRegions(t *testing.T) {
	tests := []struct {
		name  string
		board Board
		want  Board
	}{
		{
			name:  "Empty board",
			board: Board{},
			want:  Board{},
		},
		{
			name: "Full row",
			board: Board{
				{1, 1, 1, 1, 1, 1, 1, 1, 1},
				{0, 0, 0, 0, 0, 0, 0, 0, 0},
				// ... rest 0
			},
			want: Board{
				{0, 0, 0, 0, 0, 0, 0, 0, 0},
				{0, 0, 0, 0, 0, 0, 0, 0, 0},
				// ... rest 0
			},
		},
		{
			name: "Full column",
			board: Board{
				{1, 0},
				{1, 0},
				{1, 0},
				{1, 0},
				{1, 0},
				{1, 0},
				{1, 0},
				{1, 0},
				{1, 0},
				// other columns 0
			},
			want: Board{
				{0, 0},
				{0, 0},
				{0, 0},
				{0, 0},
				{0, 0},
				{0, 0},
				{0, 0},
				{0, 0},
				{0, 0},
				// other 0
			},
		},
		{
			name: "Full 3x3 block",
			board: Board{
				{1, 1, 1, 0},
				{1, 1, 1, 0},
				{1, 1, 1, 0},
				{0, 0, 0, 0},
				// ... rest 0
			},
			want: Board{
				{0, 0, 0, 0},
				{0, 0, 0, 0},
				{0, 0, 0, 0},
				{0, 0, 0, 0},
				// ... rest 0
			},
		},
		{
			name: "Overlapping row and block",
			board: Board{
				{1, 1, 1, 1, 1, 1, 1, 1, 1},
				{1, 1, 1, 0, 0, 0, 0, 0, 0},
				{1, 1, 1, 0, 0, 0, 0, 0, 0},
				// rest 0
			},
			want: Board{
				{0, 0, 0, 0, 0, 0, 0, 0, 0},
				{0, 0, 0, 0, 0, 0, 0, 0, 0},
				{0, 0, 0, 0, 0, 0, 0, 0, 0},
				// rest 0
			}, // block clears first 3x3, row clears whole row
		},
		// Add more for multiple clears, partial fills, etc.
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := checkAndRemoveCompletedRegions(tt.board)
			for i := 0; i < 9; i++ {
				for j := 0; j < 9; j++ {
					if got[i][j] != tt.want[i][j] {
						t.Errorf("checkAndRemoveCompletedRegions mismatch at [%d][%d]: got %d, want %d", i, j, got[i][j], tt.want[i][j])
					}
				}
			}
		})
	}
}

func TestApplyMoveToBoard(t *testing.T) {
	tests := []struct {
		name  string
		board Board
		move  Move
		want  Board
	}{
		{
			name:  "Simple place no clear",
			board: Board{},
			move:  Move{ShapeID: 100, Row: 0, Col: 0},
			want:  Board{{1, 0, 0, 0, 0, 0, 0, 0, 0}}, // rest 0
		},
		{
			name: "Place to complete row",
			board: Board{
				{1, 1, 1, 1, 1, 1, 1, 1, 0},
				// rest 0
			},
			move: Move{ShapeID: 100, Row: 0, Col: 8},
			want: Board{
				{0, 0, 0, 0, 0, 0, 0, 0, 0},
				// rest 0
			},
		},
		// Add more tests for column complete, block complete, etc.
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := applyMoveToBoard(tt.board, tt.move)
			for i := 0; i < 9; i++ {
				for j := 0; j < 9; j++ {
					if got[i][j] != tt.want[i][j] {
						t.Errorf("applyMoveToBoard mismatch at [%d][%d]: got %d, want %d", i, j, got[i][j], tt.want[i][j])
					}
				}
			}
		})
	}
}

// Integration test for the whole app

// func TestStartGame2(t *testing.T) {
// 	// Prepare fixed random shapes with a local random generator
// 	rng := rand.New(rand.NewSource(42)) // Fixed seed for reproducibility

// 	var shapeIDs []int
// 	for id := range shapes {
// 		shapeIDs = append(shapeIDs, id)
// 	}
// 	sort.Ints(shapeIDs) // Sort for consistency

// 	// Pick 3 fixed "random" IDs using rng
// 	id1 := shapeIDs[rng.Intn(len(shapeIDs))]
// 	id2 := shapeIDs[rng.Intn(len(shapeIDs))]
// 	id3 := shapeIDs[rng.Intn(len(shapeIDs))]

// 	input := fmt.Sprintf("%d\n%d\n%d\n", id1, id2, id3) // Simulate one iteration of input

// 	oldStdin := os.Stdin
// 	oldStdout := os.Stdout
// 	defer func() {
// 		os.Stdin = oldStdin
// 		os.Stdout = oldStdout
// 	}()

// 	r, w, _ := os.Pipe()
// 	os.Stdin = r

// 	// To capture stdout, use pipe
// 	outR, outW, _ := os.Pipe()
// 	os.Stdout = outW

// 	// Run in goroutine since infinite loop
// 	go func() {
// 		var board Board // empty
// 		startGame2(board)
// 	}()

// 	// Feed input
// 	_, _ = w.Write([]byte(input))
// 	w.Close()

// 	// Wait a bit for processing
// 	time.Sleep(1 * time.Second) // Adjust if needed

// 	// Close outW to read
// 	outW.Close()
// 	scanner := bufio.NewScanner(outR)
// 	var output strings.Builder
// 	for scanner.Scan() {
// 		output.WriteString(scanner.Text() + "\n")
// 	}

// 	got := output.String()

// 	// Check if output contains expected parts, e.g., "Best moveS:", visualizations
// 	if !strings.Contains(got, "Best moveS:") {
// 		t.Errorf("Expected output to contain 'Best moveS:', got:\n%s", got)
// 	}
// 	if !strings.Contains(got, "Move 1:") || !strings.Contains(got, "Move 2:") || !strings.Contains(got, "Move 3:") {
// 		t.Errorf("Missing move visualizations in output:\n%s", got)
// 	}

// 	// More checks: count 'X' or something, but since deterministic with seed, can hardcode expected if known
// 	if len(got) == 0 {
// 		t.Errorf("No output produced")
// 	}
// }
