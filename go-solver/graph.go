package main

// regionInfo describes a connected group of empty cells found by flood-fill.
type regionInfo struct {
	Size           int  // number of empty cells
	OnEdge         bool // any cell touches the board boundary (row/col 0 or 8)
	OnCorner       bool // any cell is at a board corner
	MinRow, MaxRow int  // bounding-box row extent
	MinCol, MaxCol int  // bounding-box col extent
}

// rowSpan returns the height of the bounding box.
func (r regionInfo) rowSpan() int { return r.MaxRow - r.MinRow + 1 }

// colSpan returns the width of the bounding box.
func (r regionInfo) colSpan() int { return r.MaxCol - r.MinCol + 1 }

// minSpan returns the shorter bounding-box dimension.
func (r regionInfo) minSpan() int {
	if r.rowSpan() < r.colSpan() {
		return r.rowSpan()
	}
	return r.colSpan()
}

// maxSpan returns the longer bounding-box dimension.
func (r regionInfo) maxSpan() int {
	if r.rowSpan() > r.colSpan() {
		return r.rowSpan()
	}
	return r.colSpan()
}

// isChain returns true when the region is shaped like a thin line or zigzag.
// Criteria: the bounding box is at least 3× longer than wide, or the region
// is literally 1 cell wide (minSpan == 1). Such regions can only be filled
// by pieces that happen to match their narrow shape.
func (r regionInfo) isChain() bool {
	ms := r.minSpan()
	return ms == 1 || r.maxSpan() >= 3*ms
}

// dfs4 flood-fills from (row,col) using 4-connectivity (no diagonals).
// Diagonal neighbours are excluded because pieces are placed orthogonally;
// a diagonal-only connection provides no shared filling advantage.
// Board edges are natural boundaries — no wrapping is applied.
func dfs4(board *Board, visited *[9][9]bool, row, col int, info *regionInfo) {
	if row < 0 || row >= 9 || col < 0 || col >= 9 {
		return
	}
	if visited[row][col] || board[row][col] != 0 {
		return
	}
	visited[row][col] = true
	info.Size++

	if row < info.MinRow {
		info.MinRow = row
	}
	if row > info.MaxRow {
		info.MaxRow = row
	}
	if col < info.MinCol {
		info.MinCol = col
	}
	if col > info.MaxCol {
		info.MaxCol = col
	}

	if row == 0 || row == 8 || col == 0 || col == 8 {
		info.OnEdge = true
	}
	if (row == 0 || row == 8) && (col == 0 || col == 8) {
		info.OnCorner = true
	}

	dfs4(board, visited, row-1, col, info)
	dfs4(board, visited, row+1, col, info)
	dfs4(board, visited, row, col-1, info)
	dfs4(board, visited, row, col+1, info)
}

// emptyRegions returns info for every 4-connected group of empty cells.
// Each cell belongs to exactly one region.
func emptyRegions(board Board) []regionInfo {
	var visited [9][9]bool
	var regions []regionInfo
	for r := 0; r < 9; r++ {
		for c := 0; c < 9; c++ {
			if !visited[r][c] && board[r][c] == 0 {
				info := regionInfo{MinRow: r, MaxRow: r, MinCol: c, MaxCol: c}
				dfs4(&board, &visited, r, c, &info)
				regions = append(regions, info)
			}
		}
	}
	return regions
}

// dfs4Filled flood-fills connected filled cells (value != 0) from (row,col).
func dfs4Filled(board *Board, visited *[9][9]bool, row, col int, info *regionInfo) {
	if row < 0 || row >= 9 || col < 0 || col >= 9 {
		return
	}
	if visited[row][col] || board[row][col] == 0 {
		return
	}
	visited[row][col] = true
	info.Size++

	if row < info.MinRow {
		info.MinRow = row
	}
	if row > info.MaxRow {
		info.MaxRow = row
	}
	if col < info.MinCol {
		info.MinCol = col
	}
	if col > info.MaxCol {
		info.MaxCol = col
	}

	dfs4Filled(board, visited, row-1, col, info)
	dfs4Filled(board, visited, row+1, col, info)
	dfs4Filled(board, visited, row, col-1, info)
	dfs4Filled(board, visited, row, col+1, info)
}

// filledRegions returns info for every 4-connected group of filled cells.
func filledRegions(board Board) []regionInfo {
	var visited [9][9]bool
	var regions []regionInfo
	for r := 0; r < 9; r++ {
		for c := 0; c < 9; c++ {
			if !visited[r][c] && board[r][c] != 0 {
				info := regionInfo{MinRow: r, MaxRow: r, MinCol: c, MaxCol: c}
				dfs4Filled(&board, &visited, r, c, &info)
				regions = append(regions, info)
			}
		}
	}
	return regions
}
