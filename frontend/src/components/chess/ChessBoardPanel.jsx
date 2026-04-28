import { useEffect, useMemo, useRef, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";

export function ChessBoardPanel({ fen, lastMove, mode, onMove, disabled }) {
  const boardRef = useRef(null);
  const boardBoxRef = useRef(null);
  const [fullscreen, setFullscreen] = useState(false);
  const [boardWidth, setBoardWidth] = useState(560);
  const [animateMovePulse, setAnimateMovePulse] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [selectedSquare, setSelectedSquare] = useState(null);

  const position = fen || "start";

  // Only pawns can promote — explicitly exclude kings and all other pieces
  const isPromotionMove = (sourceSquare, targetSquare, piece) => {
    if (!piece || !sourceSquare || !targetSquare) return false;
    if (!piece.endsWith("P")) return false;
    const fileDistance = Math.abs(sourceSquare.charCodeAt(0) - targetSquare.charCodeAt(0));
    return (
      ((piece === "wP" && sourceSquare[1] === "7" && targetSquare[1] === "8") ||
        (piece === "bP" && sourceSquare[1] === "2" && targetSquare[1] === "1")) &&
      fileDistance <= 1
    );
  };

  const submitMove = (uci) => {
    void onMove(uci);
  };

  // Helper to check if a pawn move is a promotion candidate
  const isPromotionCandidate = (sourceSquare, targetSquare, color, type) => {
    if (type !== "p") return false;
    const piece = color === "w" ? "wP" : "bP";
    return (
      ((piece === "wP" && sourceSquare[1] === "7" && targetSquare[1] === "8") ||
        (piece === "bP" && sourceSquare[1] === "2" && targetSquare[1] === "1")) &&
      Math.abs(sourceSquare.charCodeAt(0) - targetSquare.charCodeAt(0)) <= 1
    );
  };

  // Handles piece drop for desktop drag-and-drop
  const onPieceDrop = (sourceSquare, targetSquare, piece) => {
    if (disabled) return false;

    if (isPromotionMove(sourceSquare, targetSquare, piece)) {
      return true;
    }

    const temp = new Chess(position === "start" ? undefined : fen);
    const move = temp.move({
      from: sourceSquare,
      to: targetSquare
    });

    if (!move) return false;
    submitMove(move.from + move.to + (move.promotion || ""));
    return true;
  };

  // Handles promotion piece selection in modal
  const onPromotionPieceSelect = (piece, promoteFromSquare, promoteToSquare) => {
    if (disabled) return false;
    if (!piece || !promoteFromSquare || !promoteToSquare) return false;

    const promotion = piece[1]?.toLowerCase();
    if (!promotion || !["q", "r", "b", "n"].includes(promotion)) return false;

    const temp = new Chess(position === "start" ? undefined : fen);
    const move = temp.move({
      from: promoteFromSquare,
      to: promoteToSquare,
      promotion
    });
    if (!move) return false;

    submitMove(move.from + move.to + promotion);
    return true;
  };

  // Handles toggling fullscreen mode for the board
  const toggleFullscreen = async () => {
    const container = boardRef.current;
    if (!container) return;
    if (!document.fullscreenElement) {
      await container.requestFullscreen();
      setFullscreen(true);
    } else {
      await document.exitFullscreen();
      setFullscreen(false);
    }
  };

  // Effect: handle board resizing, fullscreen, and mobile detection
  useEffect(() => {
    const updateMobileFlag = () => {
      const coarse = window.matchMedia("(pointer: coarse)").matches;
      const narrow = window.matchMedia("(max-width: 900px)").matches;
      setIsMobile(coarse || narrow);
    };

    const updateBoardSize = () => {
      const box = boardBoxRef.current;
      if (!box) return;
      const rect = box.getBoundingClientRect();
      const minBoardSize = 220;
      const next = Math.max(minBoardSize, Math.floor(Math.min(rect.width, rect.height)));
      setBoardWidth((prev) => (Math.abs(prev - next) >= 2 ? next : prev));
    };

    updateMobileFlag();
    updateBoardSize();
    const observer = new ResizeObserver(updateBoardSize);
    if (boardBoxRef.current) observer.observe(boardBoxRef.current);
    window.addEventListener("resize", updateBoardSize);
    window.addEventListener("resize", updateMobileFlag);

    const onFullscreenChange = () => {
      setFullscreen(Boolean(document.fullscreenElement));
      updateBoardSize();
    };
    document.addEventListener("fullscreenchange", onFullscreenChange);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", updateBoardSize);
      window.removeEventListener("resize", updateMobileFlag);
      document.removeEventListener("fullscreenchange", onFullscreenChange);
    };
  }, []);

  // Effect: animate move pulse when lastMove changes
  useEffect(() => {
    if (!lastMove) return;
    setSelectedSquare(null);
    setAnimateMovePulse(false);
    const raf = window.requestAnimationFrame(() => {
      setAnimateMovePulse(true);
    });
    const timer = window.setTimeout(() => {
      setAnimateMovePulse(false);
    }, 260);
    return () => {
      window.cancelAnimationFrame(raf);
      window.clearTimeout(timer);
    };
  }, [lastMove]);

  // Effect: clear selection when switching to desktop
  useEffect(() => {
    if (!isMobile) {
      setSelectedSquare(null);
    }
  }, [isMobile]);

  const orientation = useMemo(() => "white", []);
  const dndOptions = useMemo(
    () => ({
      enableMouseEvents: true,
      delayTouchStart: 0,
      touchSlop: 0
    }),
    []
  );
  const customBoardStyle = useMemo(
    () => ({
      borderRadius: "12px",
      boxShadow: "0 10px 35px rgba(0, 0, 0, 0.24)",
      touchAction: "none"
    }),
    []
  );

  // Find the king's square if in check, for highlighting
  const checkSquare = useMemo(() => {
    if (!fen || fen === "start") return null;
    try {
      const temp = new Chess(fen);
      if (!temp.inCheck()) return null;
      const turn = temp.turn(); // "w" or "b"
      // Find the king square for the side in check
      for (const row of temp.board()) {
        for (const square of row) {
          if (square && square.type === "k" && square.color === turn) {
            return square.square;
          }
        }
      }
    } catch {
      // ignore
    }
    return null;
  }, [fen]);

  // Compute custom square styles for check, selection, and legal moves
  const customSquareStyles = useMemo(() => {
    const styles = {};

    // Red pulse on the king's square when in check
    if (checkSquare) {
      styles[checkSquare] = {
        background: "radial-gradient(circle, rgba(220,38,38,0.85) 0%, rgba(220,38,38,0.4) 60%, transparent 80%)",
        boxShadow: "inset 0 0 0 3px rgba(220,38,38,0.9)"
      };
    }

    // Mobile tap-to-move: selected piece and legal move dots
    if (isMobile && selectedSquare) {
      // Selected square — blue ring (overrides check highlight if king is selected while in check)
      styles[selectedSquare] = {
        ...(styles[selectedSquare] || {}),
        boxShadow: "inset 0 0 0 4px rgba(31, 95, 214, 0.92)"
      };

      try {
        const temp = new Chess(position === "start" ? undefined : fen);
        const legalMoves = temp.moves({ square: selectedSquare, verbose: true });
        for (const m of legalMoves) {
          // Don't overwrite the check highlight with a plain dot if destination is the check square
          if (!styles[m.to]) {
            styles[m.to] = {
              background: "radial-gradient(circle, rgba(31,95,214,0.25) 36%, transparent 40%)"
            };
          }
        }
      } catch {
        // ignore
      }
    }

    return styles;
  }, [checkSquare, isMobile, selectedSquare, fen, position]);

  // Handles tap-to-move logic for mobile
  const handleSquareClick = (square) => {
    if (!isMobile || disabled) return;

    const temp = new Chess(position === "start" ? undefined : fen);
    const piece = temp.get(square);
    const turn = temp.turn();

    if (!selectedSquare) {
      if (!piece || piece.color !== turn) return;
      setSelectedSquare(square);
      return;
    }

    if (selectedSquare === square) {
      setSelectedSquare(null);
      return;
    }

    const selectedPiece = temp.get(selectedSquare);
    if (!selectedPiece) {
      setSelectedSquare(null);
      return;
    }

    // Check if a legal move exists from selectedSquare → square BEFORE deciding to re-select
    const legalMoves = temp.moves({ square: selectedSquare, verbose: true });
    const isLegalTarget = legalMoves.some((m) => m.to === square);

    if (!isLegalTarget && piece && piece.color === turn) {
      // No legal move to this square, but it's our own piece — re-select it
      setSelectedSquare(square);
      return;
    }

    if (!isLegalTarget) {
      setSelectedSquare(null);
      return;
    }

    const promotion = isPromotionCandidate(selectedSquare, square, selectedPiece.color, selectedPiece.type)
      ? "q"
      : undefined;

    const move = temp.move({
      from: selectedSquare,
      to: square,
      promotion
    });

    if (!move) {
      setSelectedSquare(null);
      return;
    }

    submitMove(move.from + move.to + (move.promotion || ""));
    setSelectedSquare(null);
  };

  return (
    <div className="board-wrap" ref={boardRef}>
      <div className="board-toolbar">
        <span>{mode || "Game not started"}</span>
        <button type="button" onClick={toggleFullscreen}>
          {fullscreen ? "Exit Maximize" : "Maximize Board"}
        </button>
      </div>
      <div className={`board-box${animateMovePulse ? " move-pulse" : ""}`} ref={boardBoxRef}>
        <Chessboard
          id="agentic-board"
          boardOrientation={orientation}
          position={position}
          customDndBackendOptions={dndOptions}
          onPieceDrop={onPieceDrop}
          onSquareClick={handleSquareClick}
          onPromotionCheck={isPromotionMove}
          onPromotionPieceSelect={onPromotionPieceSelect}
          autoPromoteToQueen={false}
          promotionDialogVariant="modal"
          boardWidth={boardWidth}
          customBoardStyle={customBoardStyle}
          customSquareStyles={customSquareStyles}
          arePiecesDraggable={!disabled && !isMobile}
          animationDuration={500}
        />
      </div>
    </div>
  );
}
