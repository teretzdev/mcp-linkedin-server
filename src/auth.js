import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCredentials, loginLinkedInSecure } from './api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [autoLoginInProgress, setAutoLoginInProgress] = useState(false);
  const [autoLoginError, setAutoLoginError] = useState(null);

  useEffect(() => {
    // On mount, check credentials and auto-login if possible
    (async () => {
      try {
        const credentialsResponse = await getCredentials();
        if (credentialsResponse.data.configured) {
          setAutoLoginInProgress(true);
          setAutoLoginError(null);
          try {
            const loginResp = await loginLinkedInSecure();
            if (loginResp.data && loginResp.data.success) {
              setIsLoggedIn(true);
              setCurrentUser({
                name: credentialsResponse.data.name || credentialsResponse.data.username || 'User',
                email: credentialsResponse.data.username || 'user@example.com',
                avatar: 'https://via.placeholder.com/40'
              });
            } else {
              setAutoLoginError(loginResp.data?.message || 'Auto-login failed');
            }
          } catch (err) {
            setAutoLoginError(err.response?.data?.message || 'Auto-login failed');
          } finally {
            setAutoLoginInProgress(false);
          }
        }
      } catch (error) {
        setAutoLoginError(error.message);
      }
    })();
  }, []);

  const login = async () => {
    setAutoLoginInProgress(true);
    setAutoLoginError(null);
    try {
      const loginResp = await loginLinkedInSecure();
      if (loginResp.data && loginResp.data.success) {
        setIsLoggedIn(true);
        setCurrentUser({
          name: loginResp.data.name || loginResp.data.username || 'User',
          email: loginResp.data.username || 'user@example.com',
          avatar: 'https://via.placeholder.com/40'
        });
      } else {
        setAutoLoginError(loginResp.data?.message || 'Login failed');
      }
    } catch (err) {
      setAutoLoginError(err.response?.data?.message || 'Login failed');
    } finally {
      setAutoLoginInProgress(false);
    }
  };

  const logout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, currentUser, autoLoginInProgress, autoLoginError, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
} 