import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const RouterContext = createContext({
  currentPath: '/',
  navigate: () => {},
  goBack: () => {}
});

export function RouterProvider({ children }) {
  // Normalize current path from window.location
  const getPath = () => {
    if (typeof window === 'undefined') return '/';
    const path = window.location.pathname || '/';
    return path.endsWith('/') && path.length > 1 ? path.slice(0, -1) : path;
  };

  const [currentPath, setCurrentPath] = useState(getPath);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(getPath());
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = useCallback((toPath) => {
    if (toPath !== window.location.pathname) {
      window.history.pushState(null, '', toPath);
      setCurrentPath(toPath);
      window.scrollTo(0, 0);
    }
  }, []);

  const goBack = useCallback(() => {
    window.history.back();
  }, []);

  return (
    <RouterContext.Provider value={{ currentPath, navigate, goBack }}>
      {children}
    </RouterContext.Provider>
  );
}

export function useRouter() {
  const context = useContext(RouterContext);
  if (!context) {
    throw new Error('useRouter must be used within a RouterProvider');
  }
  return context;
}

export function Link({ to, children, className, style, onClick, ...rest }) {
  const { navigate } = useRouter();

  const handleClick = (e) => {
    if (e) e.preventDefault();
    if (onClick) onClick(e);
    navigate(to);
  };

  return (
    <a href={to} onClick={handleClick} className={className} style={style} {...rest}>
      {children}
    </a>
  );
}

export function Route({ path, currentPath, element }) {
  if (path !== currentPath) return null;
  return element;
}

