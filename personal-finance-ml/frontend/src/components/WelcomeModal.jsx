import { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Target, MapPin, DollarSign, Sparkles } from 'lucide-react';

export default function WelcomeModal() {
    const { token } = useAuth();
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    // Form fields
    const [salary, setSalary] = useState('');
    const [cityTier, setCityTier] = useState(2);
    const [savingsGoal, setSavingsGoal] = useState(20);

    useEffect(() => {
        const checkProfile = async () => {
            try {
                const profile = await apiCall('/users/me/', 'GET', null, token);
                // The API returns monthly_salary either flat or nested depending on the serializer.
                // In UserDetailSerializer it is returned flat because of standard DRF serialization.
                const userSalary = profile.monthly_salary;
                if (!userSalary || parseFloat(userSalary) <= 0) {
                    setIsOpen(true);
                }
            } catch (err) {
                console.error("Could not fetch profile", err);
            } finally {
                setLoading(false);
            }
        };
        if (token) checkProfile();
    }, [token]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            await apiCall('/users/me/', 'PUT', {
                profile: {
                    monthly_salary: parseFloat(salary),
                    city_tier: parseInt(cityTier),
                    savings_target_percentage: parseInt(savingsGoal)
                }
            }, token);
            setIsOpen(false);
            window.location.reload();
        } catch (err) {
            console.error(err);
            alert('Failed to save profile setup.');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading || !isOpen) return null;

    return (
        <div style={{
            position: 'fixed', inset: 0,
            background: 'rgba(0,0,0,0.8)',
            backdropFilter: 'blur(10px)',
            zIndex: 9999,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
            <div className="card animate-fade-in" style={{ maxWidth: '500px', width: '100%', margin: '0 1.5rem', border: '1px solid var(--accent-primary)', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '4px', background: 'linear-gradient(90deg, var(--accent-primary), var(--success))' }}></div>

                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem', marginTop: '1rem' }}>
                    <Sparkles color="var(--accent-primary)" />
                    Welcome to FinanceML!
                </h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', lineHeight: '1.6' }}>
                    To unleash the full power of the Analytics Optimization Engine, we need to establish your baseline demographic profile.
                </p>

                <form onSubmit={handleSubmit}>
                    <div className="input-group">
                        <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <DollarSign size={16} /> Monthly Baseline Salary (₹)
                        </label>
                        <input type="number" className="input-field" placeholder="e.g. 50000" min="1000" required value={salary} onChange={e => setSalary(e.target.value)} />
                    </div>

                    <div className="input-group">
                        <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <MapPin size={16} /> Living Area (Cost of Living Index)
                        </label>
                        <select className="input-field" value={cityTier} onChange={e => setCityTier(e.target.value)} style={{ cursor: 'pointer' }}>
                            <option value={1}>Tier 1 (Metro / High Cost)</option>
                            <option value={2}>Tier 2 (Urban / Mid Cost)</option>
                            <option value={3}>Tier 3 (Semi-Urban / Low Cost)</option>
                        </select>
                    </div>

                    <div className="input-group">
                        <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Target size={16} /> Monthly Savings Goal (%)
                        </label>
                        <select className="input-field" value={savingsGoal} onChange={e => setSavingsGoal(e.target.value)} style={{ cursor: 'pointer' }}>
                            <option value={10}>10% - Wealth Preservation</option>
                            <option value={20}>20% - Standard Recommended</option>
                            <option value={30}>30% - Aggressive Scaling</option>
                            <option value={50}>50% - FIRE Movement</option>
                        </select>
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem', padding: '1rem' }} disabled={submitting}>
                        {submitting ? 'Initializing Engine...' : 'Initialize AI Engine'}
                    </button>
                </form>
            </div>
        </div>
    );
}
