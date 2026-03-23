import './Dashboard.css';

export const Dashboard: React.FC = () => (
  <div className="dashboard">
    <h1>대시보드</h1>
    <section className="dashboard__summary">
      <h3>이슈 요약</h3>
      <div className="dashboard__cards">
        <div className="dashboard__card">
          <span className="dashboard__card-label">전체 이슈</span>
          <span className="dashboard__card-value">-</span>
        </div>
        <div className="dashboard__card">
          <span className="dashboard__card-label">진행 중</span>
          <span className="dashboard__card-value">-</span>
        </div>
        <div className="dashboard__card">
          <span className="dashboard__card-label">완료</span>
          <span className="dashboard__card-value">-</span>
        </div>
      </div>
    </section>
  </div>
);
