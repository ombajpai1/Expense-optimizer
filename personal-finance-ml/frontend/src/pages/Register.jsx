import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiCall } from '../services/api';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    // Demographic Profile Fields
    const [monthlySalary, setMonthlySalary] = useState('');
    const [cityTier, setCityTier] = useState('2');
    const [savingsTarget, setSavingsTarget] = useState('20%-30%');

    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            // Create user with demographic payloads structure expected by Django
            await apiCall('/users/register/', 'POST', {
                username,
                email,
                password,
                monthly_salary: parseFloat(monthlySalary) || 0,
                city_tier: parseInt(cityTier),
                savings_target_percentage: parseInt(savingsTarget) || 20
            });

            // Auto login after reg
            const data = await apiCall('/users/token/', 'POST', { username, password });
            login(data.access);
            navigate('/');
        } catch (err) {
            setError(err.message || 'Failed to register');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex-center" style={{ minHeight: '100vh', padding: '2rem 1rem' }}>
            <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '450px' }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <h2>Get Started</h2>
                    <p style={{ color: 'var(--text-secondary)' }}>Create your ML tracking account</p>
                </div>

                {error && (
                    <div className="badge badge-danger" style={{ display: 'block', textAlign: 'center', marginBottom: '1rem', padding: '0.5rem' }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="input-group">
                        <label className="input-label">Username</label>
                        <input
                            className="input-field"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label className="input-label">Email</label>
                        <input
                            className="input-field"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label className="input-label">Password</label>
                        <input
                            className="input-field"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{ marginBottom: '2rem' }}
                        />
                    </div>

                    <div style={{ borderTop: '1px solid var(--glass-border)', margin: '1rem 0', paddingTop: '1rem' }}>
                        <p style={{ color: 'var(--accent-secondary)', fontSize: '0.9rem', marginBottom: '1rem', fontWeight: 600 }}>Financial Demographics (ML Profile)</p>

                        <div className="input-group" style={{ marginBottom: '1rem' }}>
                            <label className="input-label">Monthly Salary (₹)</label>
                            <input
                                className="input-field"
                                type="number"
                                step="1000"
                                value={monthlySalary}
                                onChange={(e) => setMonthlySalary(e.target.value)}
                                placeholder="e.g. 75000"
                                required
                            />
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <div className="input-group">
                                <label className="input-label">City Tier Mode</label>
                                <select
                                    className="input-field"
                                    value={cityTier}
                                    onChange={(e) => setCityTier(e.target.value)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    <option value="1">Tier 1 (Metro)</option>
                                    <option value="2">Tier 2</option>
                                    <option value="3">Tier 3</option>
                                </select>
                            </div>

                            <div className="input-group">
                                <label className="input-label">Savings Target</label>
                                <select
                                    className="input-field"
                                    value={savingsTarget}
                                    onChange={(e) => setSavingsTarget(e.target.value)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    <option value="10%-20%">10% - 20%</option>
                                    <option value="20%-30%">20% - 30%</option>
                                    <option value="30%+">30%+</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <button className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} type="submit" disabled={isLoading}>
                        {isLoading ? 'Creating Account...' : 'Sign Up'}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem' }}>
                    Already have an account? <Link to="/login">Log in</Link>
                </p>
            </div>
        </div>
    );
}
