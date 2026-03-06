import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import WelcomeModal from '../components/WelcomeModal';

export default function ProtectedLayout() {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex-center" style={{ minHeight: '100vh' }}>
                <div className="skeleton" style={{ width: '100px', height: '100px', borderRadius: '50%' }}></div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="app-layout">
            <Navbar />
            <WelcomeModal />
            <main className="container" style={{ padding: '2rem 1.5rem', marginTop: '1rem' }}>
                <Outlet />
            </main>
        </div>
    );
}
