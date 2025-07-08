import axios from 'axios';

// Set up axios instance with dynamic baseURL detection
const api = axios.create();

export const detectApiPort = async () => {
  const ports = [8002, ...Array.from({length: 10}, (_, i) => 8001 + i).filter(p => p !== 8002)];
  for (let port of ports) {
    try {
      const response = await axios.get(`http://localhost:${port}/api/health`, { timeout: 1000 });
      if (response.status === 200) {
        api.defaults.baseURL = `http://localhost:${port}`;
        return port;
      }
    } catch (error) {
      continue;
    }
  }
  throw new Error('No API Bridge found on ports 8001-8010.');
};

export const healthCheck = () => api.get('/api/health');
export const getCredentials = () => api.get('/api/get_credentials');
export const loginLinkedInSecure = () => api.post('/api/login_linkedin_secure');
export const startSession = (session_id, mode='manual') => api.post('/api/session/start', { session_id, automation_mode: mode });
export const updateSession = (session_id, stats) => api.post('/api/session/update', { ...stats }, { params: { session_id } });
export const endSession = (session_id) => api.post('/api/session/end', null, { params: { session_id } });
// Add more API calls as needed

export default api; 