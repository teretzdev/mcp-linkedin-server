import React, { useEffect, useState } from 'react';

const API = (path) => `http://localhost:8001/api/automation${path}`;

export default function AutomationDashboard() {
  const [status, setStatus] = useState({ running: false, interval: 3600, log: [] });
  const [queue, setQueue] = useState([]);
  const [interval, setInterval] = useState(3600);
  const [jobData, setJobData] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch status and queue
  const fetchStatus = async () => {
    const res = await fetch(API('/status'));
    setStatus(await res.json());
  };
  const fetchQueue = async () => {
    const res = await fetch(API('/queue'));
    const data = await res.json();
    setQueue(data.jobs || []);
  };
  useEffect(() => {
    fetchStatus();
    fetchQueue();
    const timer = setInterval(() => {
      fetchStatus();
      fetchQueue();
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  // Start/stop automation
  const startAutomation = async () => {
    setLoading(true); setError('');
    try {
      await fetch(API('/start'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interval: Number(interval) })
      });
      await fetchStatus();
    } catch (e) { setError('Failed to start automation'); }
    setLoading(false);
  };
  const stopAutomation = async () => {
    setLoading(true); setError('');
    try {
      await fetch(API('/stop'), { method: 'POST' });
      await fetchStatus();
    } catch (e) { setError('Failed to stop automation'); }
    setLoading(false);
  };

  // Add job
  const addJob = async () => {
    setLoading(true); setError('');
    try {
      await fetch(API('/add_job'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_data: JSON.parse(jobData) })
      });
      setJobData('');
      await fetchQueue();
    } catch (e) { setError('Invalid job data (must be JSON)'); }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 800, margin: '40px auto', padding: 24, background: '#fff', borderRadius: 12, boxShadow: '0 2px 8px #0001' }}>
      <h2>AI Job Automation Dashboard</h2>
      <div style={{ marginBottom: 16 }}>
        <b>Status:</b> {status.running ? <span style={{ color: 'green' }}>Running</span> : <span style={{ color: 'red' }}>Stopped</span>}
        <br />
        <b>Interval:</b> {status.interval} seconds
        <br />
        <button onClick={startAutomation} disabled={loading || status.running} style={{ marginRight: 8 }}>Start</button>
        <button onClick={stopAutomation} disabled={loading || !status.running}>Stop</button>
        <input type="number" min={10} value={interval} onChange={e => setInterval(e.target.value)} style={{ marginLeft: 16, width: 100 }} /> seconds
      </div>
      <div style={{ marginBottom: 16 }}>
        <b>Add Job (JSON):</b>
        <input type="text" value={jobData} onChange={e => setJobData(e.target.value)} placeholder='{"query":"python developer"}' style={{ width: 400, marginLeft: 8 }} />
        <button onClick={addJob} disabled={loading || !jobData}>Add</button>
      </div>
      {error && <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>}
      <div style={{ marginBottom: 16 }}>
        <b>Job Queue:</b>
        <table style={{ width: '100%', marginTop: 8, borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f0f0f0' }}>
              <th>ID</th><th>Status</th><th>Data</th><th>Result</th><th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {queue.map(job => (
              <tr key={job.job_id} style={{ borderBottom: '1px solid #eee' }}>
                <td>{job.job_id}</td>
                <td>{job.status}</td>
                <td><pre style={{ margin: 0, fontSize: 12 }}>{JSON.stringify(job.job_data)}</pre></td>
                <td>{job.result || ''}</td>
                <td>{new Date(job.timestamp * 1000).toLocaleString()}</td>
              </tr>
            ))}
            {queue.length === 0 && <tr><td colSpan={5} style={{ textAlign: 'center', color: '#888' }}>No jobs in queue</td></tr>}
          </tbody>
        </table>
      </div>
      <div>
        <b>Automation Log:</b>
        <div style={{ background: '#f9f9f9', padding: 12, borderRadius: 6, minHeight: 60, fontFamily: 'monospace', fontSize: 13, maxHeight: 200, overflowY: 'auto' }}>
          {status.log && status.log.length > 0 ? status.log.map((line, i) => <div key={i}>{line}</div>) : <span style={{ color: '#888' }}>No log entries</span>}
        </div>
      </div>
    </div>
  );
} 