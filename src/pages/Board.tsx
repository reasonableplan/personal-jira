import './Board.css';

const BOARD_COLUMNS = ['Backlog', 'Ready', 'In Progress', 'Done'] as const;

export const Board: React.FC = () => (
  <div className="board">
    <h1>보드</h1>
    <div className="board__columns">
      {BOARD_COLUMNS.map((column) => (
        <div key={column} className="board__column">
          <h3 className="board__column-title">{column}</h3>
          <div className="board__column-body" />
        </div>
      ))}
    </div>
  </div>
);
