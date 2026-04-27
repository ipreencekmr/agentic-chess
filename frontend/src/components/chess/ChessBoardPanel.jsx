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

  // FIX 1: Guard against non-pawn pieces so king drags never trigger promotion flow
  const isPromotionMove = (sourceSquare, targetSquare, piece) => {
    if (!piece || !sourceSquare || !targetSquare) return false;
    // Only pawns can promote — explicitly exclude kings and all other pieces
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

  const isPromotionCandidate = (sourceSquare, targetSquare, color, type) => {
    if (type !== "p") return false;
    const piece = color === "w" ? "wP" : "bP";
    return (
      ((piece === "wP" && sourceSquare[1] === "7" && targetSquare[1] === "8") ||
        (piece === "bP" && sourceSquare[1] === "2" && targetSquare[1] === "1")) &&
      Math.abs(sourceSquare.charCodeAt(0) - targetSquare.charCodeAt(0)) <= 1
    );
  };

  const onPieceDrop = (sourceSquare, targetSquare, piece) => {
    if (disabled) return false;

    // FIX 1 continued: promotion check now correctly ignores king/castling moves
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
      const next = Math.max(220, Math.floor(Math.min(rect.width, rect.height)));
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
  const customSquareStyles = useMemo(() => {
    if (!isMobile || !selectedSquare) return {};

    // FIX 3: Highlight valid castling destination squares for the selected king
    const styles = {
      [selectedSquare]: {
        boxShadow: "inset 0 0 0 4px rgba(31, 95, 214, 0.92)"
      }
    };

    try {
      const temp = new Chess(position === "start" ? undefined : fen);
      const legalMoves = temp.moves({ square: selectedSquare, verbose: true });
      for (const m of legalMoves) {
        styles[m.to] = {
          background: "radial-gradient(circle, rgba(31,95,214,0.25) 36%, transparent 40%)"
        };
      }
    } catch {
      // ignore
    }

    return styles;
  }, [isMobile, selectedSquare, fen, position]);

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

    // FIX 3: Check if a legal move exists from selectedSquare → square BEFORE
    // deciding to re-select. This fixes castling: tapping g1 (where the rook sits)
    // should castle, not re-select the rook.
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
          animationDuration={500} // FIX 2: was 2000ms — reduced to 500ms so board isn't locked
        />
      </div>
    </div>
  );
}