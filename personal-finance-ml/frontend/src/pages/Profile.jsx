import React, { useState, useEffect } from 'react';
import { User, DollarSign, Target, MapPin, Loader, Save, CheckCircle } from 'lucide-react';
import { apiCall } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
    const { token } = useAuth();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');
    const [errorMsg, setErrorMsg] = useState('');

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        monthly_salary: '',
        city_tier: 2,
        savings_target_percentage: 20
    });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await apiCall('/users/me/', 'GET', null, token);
                setFormData({
                    username: data.username,
                    email: data.email || '',
                    monthly_salary: data.monthly_salary || '',
                    city_tier: data.city_tier || 2,
                    savings_target_percentage: data.savings_target_percentage || 20
                });
            } catch (err) {
                console.error("Failed to load profile", err);
                setErrorMsg("Failed to load profile. Please try again.");
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setSuccessMsg('');
        setErrorMsg('');

        try {
            await apiCall('/users/me/', 'PUT', {
                email: formData.email,
                monthly_salary: parseFloat(formData.monthly_salary) || 0,
                city_tier: parseInt(formData.city_tier),
                savings_target_percentage: parseInt(formData.savings_target_percentage) || 20
            }, token);
            setSuccessMsg("Profile successfully updated and optimization limits recalculated!");
        } catch (err) {
            console.error("Failed to update profile", err);
            setErrorMsg("Failed to update profile. Ensure all inputs are valid.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex-center" style={{ height: '80vh' }}>
                <Loader className="spinner" size={48} color="var(--primary-color)" />
            </div>
        );
    }

    return (
        <div className="dashboard-container profile-container animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto', paddingTop: '2rem' }}>
            <div className="dashboard-header" style={{ marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <User size={32} color="var(--primary-color)" /> Profile & ML Demographics
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Set your financial baseline to fuel the AI Budget Regressor.</p>
                </div>
            </div>

            {successMsg && (
                <div className="alert alert-success animate-slide-up" style={{ backgroundColor: '#064e3b', color: '#34d399', padding: '1rem', borderRadius: '12px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <CheckCircle size={20} /> {successMsg}
                </div>
            )}

            {errorMsg && (
                <div className="alert alert-danger animate-slide-up" style={{ padding: '1rem', borderRadius: '12px', marginBottom: '2rem' }}>
                    {errorMsg}
                </div>
            )}

            <div className="glass-panel" style={{ padding: '2.5rem' }}>
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                    <div className="form-group">
                        <label>Username (Read Only)</label>
                        <div className="input-with-icon">
                            <User size={18} />
                            <input type="text" value={formData.username} readOnly disabled style={{ opacity: 0.7 }} />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Email Address</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="your.email@example.com"
                        />
                    </div>

                    <div className="form-divider" style={{ borderTop: '1px solid rgba(255,255,255,0.1)', margin: '1rem 0' }}></div>
                    <h3 style={{ fontSize: '1.25rem', color: 'var(--primary-light)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        Optimization Parameters
                    </h3>

                    <div className="form-row" style={{ display: 'flex', gap: '1.5rem' }}>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Monthly Salary (INR)</label>
                            <div className="input-with-icon">
                                <DollarSign size={18} />
                                <input
                                    type="number"
                                    name="monthly_salary"
                                    value={formData.monthly_salary}
                                    onChange={handleChange}
                                    placeholder="e.g. 150000"
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group" style={{ flex: 1 }}>
                            <label>City Tier</label>
                            <div className="input-with-icon">
                                <MapPin size={18} />
                                <select name="city_tier" value={formData.city_tier} onChange={handleChange} required>
                                    <option value={1}>Tier 1 (Metro / High Cost)</option>
                                    <option value={2}>Tier 2 (Urban / Mid Cost)</option>
                                    <option value={3}>Tier 3 (Semi-Urban / Low Cost)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Target Savings Percentage</label>
                        <div className="input-with-icon">
                            <Target size={18} />
                            <input
                                type="number"
                                name="savings_target_percentage"
                                value={formData.savings_target_percentage}
                                onChange={handleChange}
                                placeholder="e.g. 25"
                                min="0" max="100"
                                required
                            />
                        </div>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                            The AI will aggressively trim your "Recreation" and scalable limits to ensure you hit this goal.
                        </p>
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start', padding: '0.75rem 2rem', marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }} disabled={saving}>
                        {saving ? <Loader className="spinner" size={18} /> : <Save size={18} />}
                        Save Settings
                    </button>
                </form>
            </div>
        </div>
    );
}
