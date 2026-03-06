import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { LogOut, Activity, PlusCircle, PieChart, User, Sun, Moon } from 'lucide-react';

export default function Navbar() {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav style={{
            background: 'var(--glass-bg)',
            backdropFilter: 'var(--glass-blur)',
            borderBottom: '1px solid var(--glass-border)',
            padding: '1rem 0',
            position: 'sticky',
            top: 0,
            zIndex: 50
        }}>
            <div className="container flex-between">
                <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-primary)' }}>
                    <Activity color="var(--accent-primary)" size={28} />
                    <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.25rem' }}>
                        Finance<span style={{ color: 'var(--accent-primary)' }}>ML</span>
                    </span>
                </Link>

                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <Link to="/profile" className="btn btn-secondary" style={{ border: 'none', padding: '0.5rem 1rem' }}>
                        <User size={18} /> Profile
                    </Link>
                    <Link to="/analytics" className="btn btn-secondary" style={{ border: 'none', padding: '0.5rem 1rem' }}>
                        <PieChart size={18} /> Dashboard
                    </Link>
                    <Link to="/" className="btn btn-secondary" style={{ border: 'none', padding: '0.5rem 1rem' }}>
                        <Activity size={18} /> Expenses
                    </Link>
                    <button className="btn btn-primary" style={{ padding: '0.5rem 1rem' }} onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                        <PlusCircle size={18} /> New Expense
                    </button>
                    <div style={{ width: '1px', height: '24px', background: 'var(--border-light)', margin: '0 0.5rem' }}></div>
                    <button onClick={toggleTheme} className="btn btn-secondary" style={{ border: 'none', padding: '0.5rem', color: 'var(--text-secondary)' }} title="Toggle Theme">
                        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                    </button>
                    <button onClick={handleLogout} className="btn btn-secondary" style={{ border: 'none', padding: '0.5rem', color: 'var(--text-secondary)' }} title="Logout">
                        <LogOut size={20} />
                    </button>
                </div>
            </div>
        </nav>
    );
}
