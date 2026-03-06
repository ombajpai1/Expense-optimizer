import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiCall } from '../services/api';
import { Activity, AlertTriangle, CheckCircle, Clock, Trash2, Sparkles, Check, Edit2 } from 'lucide-react';

export default function Dashboard() {
    const { token } = useAuth();
    const [expenses, setExpenses] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Form State
    const [amount, setAmount] = useState('');
    const [description, setDescription] = useState('');
    const [categoryId, setCategoryId] = useState('Auto');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Inline Editing State
    const [editingExpenseId, setEditingExpenseId] = useState(null);
    const [editingCategoryId, setEditingCategoryId] = useState('');

    const fetchExpensesAndCategories = async () => {
        try {
            const [expData, catData] = await Promise.all([
                apiCall('/expenses/expenses/', 'GET', null, token),
                apiCall('/expenses/categories/', 'GET', null, token)
            ]);
            setExpenses(expData);
            setCategories(catData);
        } catch (err) {
            setError('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchExpensesAndCategories();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError('');

        try {
            await apiCall('/expenses/expenses/', 'POST', {
                amount: parseFloat(amount),
                description,
                category_id: categoryId
            }, token);

            // Reset form & reload data
            setAmount('');
            setDescription('');
            setCategoryId('Auto');
            fetchExpensesAndCategories();
        } catch (err) {
            setError(err.message || 'Failed to add expense');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDelete = async (expenseId) => {
        if (!window.confirm("Are you sure you want to delete this expense? This action cannot be undone.")) {
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/expenses/expenses/${expenseId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 204) {
                // Re-fetch data to update UI and trigger fresh ML aggregations
                fetchExpensesAndCategories();
            } else {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to delete');
            }
        } catch (err) {
            setError(err.message || 'Failed to delete expense');
        }
    };

    const handleVerify = async (expenseId) => {
        try {
            await apiCall(`/expenses/expenses/${expenseId}/`, 'PATCH', { needs_review: false }, token);
            setExpenses(prevExpenses => prevExpenses.map(exp =>
                exp.id === expenseId ? { ...exp, needs_review: false } : exp
            ));
        } catch (err) {
            setError(err.message || 'Failed to verify expense');
        }
    };

    const handleEditStart = (expense) => {
        setEditingExpenseId(expense.id);
        setEditingCategoryId(expense.category ? expense.category.id : (categories[0]?.id || ''));
    };

    const handleEditSave = async (expenseId) => {
        try {
            const updatedExpenseData = await apiCall(`/expenses/expenses/${expenseId}/`, 'PATCH', {
                category: editingCategoryId,
                needs_review: false,
                is_ml_predicted: false
            }, token);
            setEditingExpenseId(null);

            // Only update local array to prevent full re-render stutter
            setExpenses(prevExpenses => prevExpenses.map(exp =>
                exp.id === expenseId ? updatedExpenseData : exp
            ));
        } catch (err) {
            setError(err.message || 'Failed to update category');
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

                        <div className="input-group">
                            <label className="input-label">Category Assignment</label>
                            <select
                                className="input-field"
                                value={categoryId}
                                onChange={(e) => setCategoryId(e.target.value)}
                                style={{ cursor: 'pointer' }}
                            >
                                <option value="Auto">Auto-Detect (AI ✨)</option>
                                {categories.map(cat => (
                                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                                ))}
                            </select>
                        </div>

                        <button className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} type="submit" disabled={isSubmitting}>
                            {isSubmitting ? 'Processing...' : (categoryId === 'Auto' ? 'Save & Analyze' : 'Save Expense')}
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

                                    {editingExpenseId === expense.id ? (
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
                                            <select
                                                className="input-field"
                                                style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem', height: 'auto' }}
                                                value={editingCategoryId}
                                                onChange={(e) => setEditingCategoryId(e.target.value)}
                                            >
                                                {categories.map(cat => (
                                                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                                                ))}
                                            </select>
                                            <button onClick={() => handleEditSave(expense.id)} className="btn btn-primary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }}>Save</button>
                                            <button onClick={() => setEditingExpenseId(null)} className="btn" style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem', background: 'transparent', color: 'var(--text-muted)' }}>Cancel</button>
                                        </div>
                                    ) : (
                                        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                                <Clock size={14} />
                                                {new Date(expense.timestamp).toLocaleDateString()}
                                            </span>

                                            {expense.is_ml_predicted ? (
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <span
                                                        className="badge"
                                                        title={expense.needs_review ? `AI suggested '${expense.category_detail?.name || 'Unknown'}' with low confidence. Is this correct?` : "High Confidence AI Match"}
                                                        style={{
                                                            fontSize: '0.7rem',
                                                            background: expense.needs_review ? 'linear-gradient(135deg, #ea580c, #f97316)' : 'linear-gradient(135deg, #8b5cf6, #d946ef)',
                                                            color: 'white',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            gap: '4px',
                                                            padding: '4px 8px',
                                                            borderRadius: '12px',
                                                            cursor: 'help'
                                                        }}>
                                                        <Sparkles size={12} />
                                                        {expense.needs_review ? 'AI Suggests: ' : 'AI Mapped: '} {expense.category_detail ? expense.category_detail.name : 'Unknown'}
                                                    </span>

                                                    {/* Feedback Icons */}
                                                    <button
                                                        onClick={() => handleVerify(expense.id)}
                                                        title="Verify AI Prediction"
                                                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--success)', display: 'flex', alignItems: 'center' }}
                                                    >
                                                        <Check size={16} />
                                                    </button>
                                                    <button
                                                        onClick={() => handleEditStart(expense)}
                                                        title="Correct Category Manually"
                                                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}
                                                    >
                                                        <Edit2 size={16} />
                                                    </button>
                                                </div>
                                            ) : expense.category && (
                                                <span>• Category: <strong>{expense.category_detail ? expense.category_detail.name : 'Unknown'}</strong></span>
                                            )}
                                        </div>
                                    )}
                                </div>

                                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', textAlign: 'right' }}>
                                    <div>
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
                                    <button
                                        onClick={() => handleDelete(expense.id)}
                                        style={{
                                            background: 'transparent',
                                            border: 'none',
                                            color: 'var(--text-muted)',
                                            cursor: 'pointer',
                                            padding: '0.5rem',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            transition: 'color 0.2s ease',
                                        }}
                                        onMouseOver={(e) => e.currentTarget.style.color = 'var(--danger)'}
                                        onMouseOut={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
                                        title="Delete Expense"
                                    >
                                        <Trash2 size={20} />
                                    </button>
                                </div>

                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
