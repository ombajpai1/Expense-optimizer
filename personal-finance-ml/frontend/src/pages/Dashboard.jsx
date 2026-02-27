import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiCall } from '../services/api';
import { Activity, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

export default function Dashboard() {
    const { token } = useAuth();
    const [expenses, setExpenses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Form State
    const [amount, setAmount] = useState('');
    const [description, setDescription] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const fetchExpenses = async () => {
        try {
            const data = await apiCall('/expenses/expenses/', 'GET', null, token);
            setExpenses(data);
        } catch (err) {
            setError('Failed to load expenses');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchExpenses();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError('');

        try {
            await apiCall('/expenses/expenses/', 'POST', {
                amount: parseFloat(amount),
                description
            }, token);

            // Reset form & reload data
            setAmount('');
            setDescription('');
            fetchExpenses();
        } catch (err) {
            setError(err.message || 'Failed to add expense');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="animate-fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>

            {/* LEFT COLUMN: Input Form */}
            <div>
                <div className="card" style={{ position: 'sticky', top: '100px' }}>
                    <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Activity size={20} color="var(--accent-primary)" />
                        Add Transaction
                    </h3>

                    {error && <div className="badge badge-danger" style={{ marginBottom: '1rem', width: '100%', padding: '0.5rem' }}>{error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="input-group">
                            <label className="input-label">Description (for ML Engine)</label>
                            <input
                                className="input-field"
                                type="text"
                                placeholder="e.g. Uber ride to airport"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                required
                            />
                        </div>

                        <div className="input-group">
                            <label className="input-label">Amount (₹)</label>
                            <input
                                className="input-field"
                                type="number"
                                step="0.01"
                                placeholder="0.00"
                                value={amount}
                                onChange={(e) => setAmount(e.target.value)}
                                required
                            />
                        </div>

                        <button className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} type="submit" disabled={isSubmitting}>
                            {isSubmitting ? 'Analyzing via ML...' : 'Save & Analyze'}
                        </button>
                    </form>
                </div>
            </div>

            {/* RIGHT COLUMN: Expense List (ML Visualizer) */}
            <div>
                <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
                    <h2>Recent Activity</h2>
                    <span className="badge badge-info">{expenses.length} Total</span>
                </div>

                {loading ? (
                    <div className="skeleton" style={{ height: '200px', width: '100%' }}></div>
                ) : expenses.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                        No expenses found. Add some to see the ML categorization in action!
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {expenses.map((expense) => (
                            <div key={expense.id} className="card" style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                borderLeft: expense.is_anomaly ? '4px solid var(--danger)' : '4px solid var(--success)',
                                padding: '1.25rem 1.5rem'
                            }}>
                                <div>
                                    <h4 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>{expense.description}</h4>
                                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                            <Clock size={14} />
                                            {new Date(expense.timestamp).toLocaleDateString()}
                                        </span>

                                        {expense.is_ml_predicted && (
                                            <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                                                AI Auto-Categorized
                                            </span>
                                        )}

                                        {expense.category && (
                                            <span>• Category: <strong>{expense.category.name}</strong></span>
                                        )}
                                    </div>
                                </div>

                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                                        ₹{parseFloat(expense.amount).toFixed(2)}
                                    </div>

                                    {expense.is_anomaly ? (
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--danger)', fontSize: '0.8rem', fontWeight: 600 }}>
                                            <AlertTriangle size={14} /> High Risk ({(expense.risk_score * 100).toFixed(0)}%)
                                        </div>
                                    ) : (
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--success)', fontSize: '0.8rem', fontWeight: 600, justifyContent: 'flex-end' }}>
                                            <CheckCircle size={14} /> Normal
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

        </div>
    );
}
