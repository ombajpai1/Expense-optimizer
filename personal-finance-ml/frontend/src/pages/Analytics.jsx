import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiCall } from '../services/api';
import { TrendingUp, PieChart, Activity, Wallet } from 'lucide-react';

export default function Analytics() {
    const { token } = useAuth();
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                // Request current month summary
                const data = await apiCall('/analytics/monthly_summary/', 'GET', null, token);
                setSummary(data);
            } catch (err) {
                setError('Failed to load analytics data.');
            } finally {
                setLoading(false);
            }
        };

        fetchAnalytics();
    }, [token]);

    const formatCurrency = (amount) => {
        return `₹${parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

    if (loading) {
        return (
            <div className="animate-fade-in" style={{ display: 'flex', gap: '2rem', flexDirection: 'column' }}>
                <div className="skeleton" style={{ height: '150px', width: '100%' }}></div>
                <div className="skeleton" style={{ height: '400px', width: '100%' }}></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card text-center" style={{ color: 'var(--danger)', padding: '3rem' }}>
                <Activity size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
                <h3>Hmm...</h3>
                <p>{error}</p>
            </div>
        );
    }

    const categories = summary?.aggregated_data || {};
    const totalAmount = summary?.total_amount || 0;

    // Convert object to array and calculate percentages for CSS bars
    const chartData = Object.keys(categories)
        .map(key => ({
            name: key,
            amount: categories[key],
            percentage: totalAmount > 0 ? (categories[key] / totalAmount) * 100 : 0
        }))
        .sort((a, b) => b.amount - a.amount); // Sort descending

    return (
        <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '900px', margin: '0 auto' }}>
            <div className="flex-between">
                <div>
                    <h1>Analytics Dashboard</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>Breakdown for {summary?.month}</p>
                </div>
            </div>

            {/* Overview Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
                <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', background: 'linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(99,102,241,0.02) 100%)' }}>
                    <div style={{ background: 'var(--accent-primary)', padding: '1rem', borderRadius: '12px', color: 'white', display: 'flex' }}>
                        <Wallet size={24} />
                    </div>
                    <div>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Total Monthly Spends</p>
                        <h2 style={{ color: 'var(--text-primary)', margin: 0, fontSize: '1.8rem' }}>{formatCurrency(totalAmount)}</h2>
                    </div>
                </div>

                <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{ background: 'var(--glass-border)', padding: '1rem', borderRadius: '12px', color: 'var(--text-primary)', display: 'flex' }}>
                        <TrendingUp size={24} />
                    </div>
                    <div>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Active Categories</p>
                        <h2 style={{ color: 'var(--text-primary)', margin: 0, fontSize: '1.8rem' }}>{chartData.length}</h2>
                    </div>
                </div>
            </div>

            {/* Category Breakdown (CSS Bars) */}
            <div className="card">
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
                    <PieChart size={20} color="var(--accent-secondary)" />
                    Expense Distribution by Category
                </h3>

                {chartData.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                        No expenses found for this month.
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        {chartData.map((item, index) => (
                            <div key={index} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                <div className="flex-between" style={{ fontSize: '0.95rem' }}>
                                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{item.name}</span>
                                    <div style={{ display: 'flex', gap: '1rem' }}>
                                        <span style={{ color: 'var(--text-secondary)' }}>{item.percentage.toFixed(1)}%</span>
                                        <span style={{ fontWeight: 600, width: '100px', textAlign: 'right' }}>{formatCurrency(item.amount)}</span>
                                    </div>
                                </div>
                                <div style={{ width: '100%', height: '8px', background: 'var(--glass-bg)', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{
                                        width: `${item.percentage}%`,
                                        height: '100%',
                                        background: `linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))`,
                                        borderRadius: '4px',
                                        transition: 'width 1s ease-in-out'
                                    }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
