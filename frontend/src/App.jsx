import { useEffect, useState } from 'react';
import PolicySidebar from './components/PolicySidebar';
import AskPanel from './components/AskPanel';
import ComparePanel from './components/ComparePanel';
import { listPolicies } from './api';
import './app.css';

export default function App() {
  const [policies, setPolicies] = useState([]);
  const [selected, setSelected] = useState([]);
  const [tab, setTab] = useState('ask');

  useEffect(() => {
    listPolicies().then((res) => {
      setPolicies(res.policies);
      setSelected(res.policies.map((p) => p.policy_id));
    }).catch(() => {});
  }, []);

  return (
    <div className="app-shell">
      <PolicySidebar
        policies={policies}
        setPolicies={setPolicies}
        selected={selected}
        setSelected={setSelected}
      />
      <main className="main">
        <nav className="tabs">
          <button className={tab === 'ask' ? 'active' : ''} onClick={() => setTab('ask')}>Ask</button>
          <button className={tab === 'compare' ? 'active' : ''} onClick={() => setTab('compare')}>Compare</button>
        </nav>
        {tab === 'ask'
          ? <AskPanel selected={selected} policies={policies} />
          : <ComparePanel selected={selected} policies={policies} />}
      </main>
    </div>
  );
}
