import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiCall } from '../services/api';
import { TrendingUp, PieChart, Activity, Wallet, Calendar, Download, Loader } from 'lucide-react';

export default function Analytics() {
    const { token } = useAuth();
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [downloading, setDownloading] = useState(false);
    const [error, setError] = useState('');

    // Filtering State
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();
    const [selectedMonth, setSelectedMonth] = useState(currentMonth);
    const [selectedYear, setSelectedYear] = useState(currentYear);

    const fetchAnalytics = async (month, year) => {
        setLoading(true);
        setError('');
        try {
            // Updated Endpoint
            const endpoint = `/expenses/expenses/comparison-stats/?month=${month}&year=${year}`;
            const data = await apiCall(endpoint, 'GET', null, token);
            setSummary(data);
        } catch (err) {
            setError(err.message || 'Failed to load analytics data.');
        } finally {
            setLoading(false);
        }
    };

    const downloadPDF = async () => {
        setDownloading(true);
        try {
            const url = `http://127.0.0.1:8000/api/analytics/download-report/?month=${selectedMonth}&year=${selectedYear}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error("Failed to download PDF");

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `Analytics_Report_${selectedYear}_${selectedMonth}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (err) {
            console.error("Error downloading PDF:", err);
            alert("Could not generate the PDF report.");
        } finally {
            setDownloading(false);
        }
    };

    useEffect(() => {
        fetchAnalytics(selectedMonth, selectedYear);
    }, [token, selectedMonth, selectedYear]);

    const formatCurrency = (amount) => {
        return `₹${parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

    if (loading && !summary) {
        return (
            <div className="animate-fade-in" style={{ display: 'flex', gap: '2rem', flexDirection: 'column' }}>
                <div className="skeleton" style={{ height: '150px', width: '100%' }}></div>
                <div className="skeleton" style={{ height: '400px', width: '100%' }}></div>
            </div>
        );
    }

    if (error && !summary) {
        return (
            <div className="card text-center" style={{ color: 'var(--danger)', padding: '3rem' }}>
                <Activity size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
                <h3>Hmm...</h3>
                <p>{error}</p>
            </div>
        );
    }

    const comparisonData = summary?.comparison || [];
    const aiInsights = summary?.ai_insights || [];
    const stats = summary?.summary || {
        monthly_salary: 0,
        total_spent: 0,
        current_savings: 0,
        savings_target_amount: 0,
        savings_target_percentage: 20
    };

    const savingsPercentageAchieved = stats.monthly_salary > 0
        ? ((stats.current_savings / stats.savings_target_amount) * 100).toFixed(0)
        : 0;

    return (
        <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '900px', margin: '0 auto' }}>

            {/* Header & Filter Controls */}
            <div className="flex-between" style={{ alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1>Optimization Dashboard</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>AI Benchmark Breakdown for {summary?.month}</p>
                </div>

                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <button
                        className="btn btn-primary"
                        onClick={downloadPDF}
                        disabled={downloading || loading || !summary}
                        style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', height: '100%', whiteSpace: 'nowrap' }}
                    >
                        {downloading ? <Loader size={16} className="spinner" /> : <Download size={16} />}
                        Download Monthly Advice PDF
                    </button>
                    <div className="input-group" style={{ marginBottom: 0 }}>
                        <select
                            className="input-field"
                            style={{ padding: '0.5rem 1rem', width: '140px', cursor: 'pointer' }}
                            value={selectedMonth}
                            onChange={(e) => setSelectedMonth(Number(e.target.value))}
                        >
                            <option value={1}>January</option>
                            <option value={2}>February</option>
                            <option value={3}>March</option>
                            <option value={4}>April</option>
                            <option value={5}>May</option>
                            <option value={6}>June</option>
                            <option value={7}>July</option>
                            <option value={8}>August</option>
                            <option value={9}>September</option>
                            <option value={10}>October</option>
                            <option value={11}>November</option>
                            <option value={12}>December</option>
                        </select>
                    </div>

                    <div className="input-group" style={{ marginBottom: 0 }}>
                        <select
                            className="input-field"
                            style={{ padding: '0.5rem 1rem', width: '120px', cursor: 'pointer' }}
                            value={selectedYear}
                            onChange={(e) => setSelectedYear(Number(e.target.value))}
                        >
                            <option value={currentYear - 1}>{currentYear - 1}</option>
                            <option value={currentYear}>{currentYear}</option>
                            <option value={currentYear + 1}>{currentYear + 1}</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Loading Overlay State */}
            {loading && summary && (
                <div style={{ opacity: 0.5, pointerEvents: 'none', transition: 'opacity 0.2s' }}>
                </div>
            )}

            {/* Overview Cards & Savings Dial */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>

                {/* Savings Progress Dial Card */}
                <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.02) 100%)', gridColumn: '1 / -1' }}>

                    {/* Circle SVGs */}
                    <div style={{ position: 'relative', width: '100px', height: '100px' }}>
                        <svg width="100" height="100" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="45" fill="none" stroke="var(--glass-border)" strokeWidth="10" />
                            <circle
                                cx="50" cy="50" r="45" fill="none"
                                stroke={stats.current_savings >= stats.savings_target_amount ? "var(--success)" : "var(--accent-primary)"}
                                strokeWidth="10"
                                strokeDasharray="283"
                                strokeDashoffset={283 - (283 * Math.min(savingsPercentageAchieved, 100)) / 100}
                                strokeLinecap="round"
                                transform="rotate(-90 50 50)"
                                style={{ transition: 'stroke-dashoffset 1.5s ease-out' }}
                            />
                        </svg>
                        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                            <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{Math.min(savingsPercentageAchieved, 100)}%</span>
                        </div>
                    </div>

                    <div style={{ flex: 1 }}>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Monthly Savings Progress ({stats.savings_target_percentage}% Goal)</p>
                        <h2 style={{ color: 'var(--text-primary)', margin: 0, fontSize: '1.8rem', display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                            {formatCurrency(stats.current_savings)}
                            <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>/ {formatCurrency(stats.savings_target_amount)} Target</span>
                        </h2>
                        {stats.current_savings < 0 && (
                            <p style={{ color: 'var(--danger)', fontSize: '0.85rem', marginTop: '0.5rem', fontWeight: 600 }}>Emergency! You are deficit saving.</p>
                        )}
                    </div>
                </div>

                <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{ background: 'var(--accent-primary)', padding: '1rem', borderRadius: '12px', color: 'white', display: 'flex' }}>
                        <Wallet size={24} />
                    </div>
                    <div>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Total Monthly Spends</p>
                        <h2 style={{ color: 'var(--text-primary)', margin: 0, fontSize: '1.8rem' }}>{formatCurrency(stats.total_spent)}</h2>
                    </div>
                </div>

                <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{ background: 'var(--glass-border)', padding: '1rem', borderRadius: '12px', color: 'var(--text-primary)', display: 'flex' }}>
                        <TrendingUp size={24} />
                    </div>
                    <div>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Monthly Baseline Salary</p>
                        <h2 style={{ color: 'var(--accent-secondary)', margin: 0, fontSize: '1.8rem' }}>{formatCurrency(stats.monthly_salary)}</h2>
                    </div>
                </div>
            </div>

            {/* AI Advisor Context Card */}
            {stats.monthly_salary > 0 && (
                <div className="card" style={{ background: 'var(--card-bg)', border: '1px solid var(--accent-primary)', marginBottom: '1rem' }}>
                    <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', color: 'var(--accent-primary)' }}>
                        <Activity size={20} />
                        Strategic AI Coaching
                    </h3>

                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: '1.6' }}>
                        Based on your profile settings and <strong>{stats.savings_target_percentage}%</strong> savings goal, the Regressor has calculated your Optimized Targets and generated the following action plan:
                    </p>

                    {aiInsights.length > 0 && (
                        <div style={{ marginBottom: '2rem' }}>
                            <h4 style={{ color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1.1rem' }}>Key Insights</h4>
                            <ul style={{ listStyleType: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {aiInsights.map((insight, idx) => (
                                    <li key={idx} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', padding: '1rem', background: 'var(--glass-bg)', borderRadius: '8px', borderLeft: '4px solid var(--accent-primary)' }}>
                                        <span style={{ color: 'var(--accent-primary)', marginTop: '2px' }}>●</span>
                                        <span style={{ color: 'var(--text-primary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                                            {insight}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <h4 style={{ color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1.1rem' }}>Category Breaches</h4>

                    <ul style={{ listStyleType: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {comparisonData.filter(item => item.status === 'Danger').map((item, idx) => (
                            <li key={idx} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', padding: '1rem', background: 'rgba(251, 113, 133, 0.1)', borderRadius: '8px', borderLeft: '4px solid var(--danger)' }}>
                                <span style={{ color: 'var(--danger)', marginTop: '2px' }}>●</span>
                                <div>
                                    <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '0.25rem' }}>Reduce {item.category} Spending</strong>
                                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                        You are <strong>{formatCurrency(item.actual_spent - item.optimized_limit)}</strong> over the AI benchmark limit. Consider cutting back to hit savings targets.
                                    </span>
                                </div>
                            </li>
                        ))}

                        {comparisonData.filter(item => item.status === 'Danger').length === 0 && (
                            <li style={{ display: 'flex', gap: '1rem', alignItems: 'center', padding: '1rem', background: 'rgba(52, 211, 153, 0.1)', borderRadius: '8px', borderLeft: '4px solid var(--success)' }}>
                                <span style={{ color: 'var(--success)' }}>●</span>
                                <div>
                                    <strong style={{ color: 'var(--text-primary)' }}>Optimal Status!</strong>
                                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'block' }}>
                                        Excellent. You are safely within limits across all categories.
                                    </span>
                                </div>
                            </li>
                        )}
                    </ul>
                </div>
            )}

            {/* ML Optimization Breakdown (Actual Vs Target Bars) */}
            <div className="card">
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
                    <PieChart size={20} color="var(--accent-secondary)" />
                    Clarity Comparison Charts
                </h3>

                {comparisonData.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                        No limit mapping found for this month.
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                        {comparisonData.sort((a, b) => b.actual_spent - a.actual_spent).map((item, index) => {
                            // Calculate proper scaling for the Clarity Chart
                            const maxScale = Math.max(item.optimized_limit, item.actual_spent) * 1.1 || 1; // 10% overflow visual padding
                            const actualPercentage = (item.actual_spent / maxScale) * 100;
                            const targetPercentage = (item.optimized_limit / maxScale) * 100;
                            const isDanger = item.status === 'Danger';

                            // Visual percentage usage relative to ML limit
                            const usagePct = item.optimized_limit > 0 ? (item.actual_spent / item.optimized_limit) * 100 : 0;

                            return (
                                <div key={index} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                    <div className="flex-between" style={{ fontSize: '0.95rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                            <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '1.1rem' }}>{item.category}</span>
                                            <span className={`badge ${isDanger ? 'badge-danger' : 'badge-success'}`} style={{ fontSize: '0.7rem' }}>
                                                {isDanger ? 'Over Budget' : 'Safe Limits'}
                                            </span>
                                        </div>
                                        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>ML Target: {formatCurrency(item.optimized_limit)}</span>
                                            <span style={{ fontWeight: 700, width: '120px', textAlign: 'right', color: isDanger ? 'var(--danger)' : 'var(--text-primary)' }}>
                                                {formatCurrency(item.actual_spent)}
                                            </span>
                                        </div>
                                    </div>

                                    {/* The Comparison Bar Container (Clarity Chart) */}
                                    <div style={{ width: '100%', height: '16px', background: 'var(--glass-bg)', borderRadius: '8px', overflow: 'hidden', position: 'relative' }}>

                                        {/* The fill bar representing actual spend (Conditionally Red or Green) */}
                                        <div style={{
                                            width: `${actualPercentage}%`,
                                            height: '100%',
                                            background: isDanger ? 'var(--danger)' : 'var(--success)',
                                            borderRadius: '8px',
                                            transition: 'width 1s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
                                        }}></div>

                                        {/* The vertical marker showing the Regressor Limit Line */}
                                        <div style={{
                                            position: 'absolute',
                                            top: 0,
                                            bottom: 0,
                                            left: `${targetPercentage}%`,
                                            width: '2px',
                                            borderLeft: '2px dotted var(--text-primary)',
                                            zIndex: 10
                                        }}></div>
                                    </div>
                                    <div className="flex-between" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                        <span>Actual Spent</span>
                                        <span>{usagePct.toFixed(1)}% of ML limit</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
