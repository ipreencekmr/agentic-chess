import { useEffect, useMemo, useRef, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";

export function ChessBoardPanel({ fen, mode, onMove, disabled }) {
  const boardRef = useRef(null);
  const boardBoxRef = useRef(null);
  const [fullscreen, setFullscreen] = useState(false);
  const [boardWidth, setBoardWidth] = useState(560);

  const position = fen || "start";

  const isPromotionMove = (sourceSquare, targetSquare, piece) => {
    if (!piece || !sourceSquare || !targetSquare) return false;
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
    const updateBoardSize = () => {
      const box = boardBoxRef.current;
      if (!box) return;
      const rect = box.getBoundingClientRect();
      const next = Math.max(220, Math.floor(Math.min(rect.width, rect.height)));
      setBoardWidth((prev) => (Math.abs(prev - next) >= 2 ? next : prev));
    };

    updateBoardSize();
    const observer = new ResizeObserver(updateBoardSize);
    if (boardBoxRef.current) observer.observe(boardBoxRef.current);
    window.addEventListener("resize", updateBoardSize);

    const onFullscreenChange = () => {
      setFullscreen(Boolean(document.fullscreenElement));
      updateBoardSize();
    };
    document.addEventListener("fullscreenchange", onFullscreenChange);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", updateBoardSize);
      document.removeEventListener("fullscreenchange", onFullscreenChange);
    };
  }, []);

  const orientation = useMemo(() => "white", []);
  const customBoardStyle = useMemo(
    () => ({
      borderRadius: "12px",
      boxShadow: "0 10px 35px rgba(0, 0, 0, 0.24)"
    }),
    []
  );

  return (
    <div className="board-wrap" ref={boardRef}>
      <div className="board-toolbar">
        <span>{mode || "Game not started"}</span>
        <button type="button" onClick={toggleFullscreen}>
          {fullscreen ? "Exit Maximize" : "Maximize Board"}
        </button>
      </div>
      <div className="board-box" ref={boardBoxRef}>
        <Chessboard
          id="agentic-board"
          boardOrientation={orientation}
          position={position}
          onPieceDrop={onPieceDrop}
          onPromotionCheck={isPromotionMove}
          onPromotionPieceSelect={onPromotionPieceSelect}
          autoPromoteToQueen={false}
          promotionDialogVariant="modal"
          boardWidth={boardWidth}
          customBoardStyle={customBoardStyle}
          arePiecesDraggable={!disabled}
          animationDuration={160}
        />
      </div>
    </div>
  );
}
