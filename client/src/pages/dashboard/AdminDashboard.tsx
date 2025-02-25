import {useEffect, useState} from 'react';
import AdminLayout from '@/components/dashboards/layouts/AdminLayout';
import Overview from '@/components/dashboards/common/Overview.tsx';
import BookingsView from '@/components/dashboards/common/booking/BookingsView';
import { useAuth } from '@/contexts/AuthContext';

const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const {dashboardData, fetchDashboard, status} = useAuth();

    useEffect(() => {
        if (!dashboardData) {
            fetchDashboard();
        }
    }, [dashboardData, fetchDashboard]);

    const renderContent = () => {
        switch (activeTab) {
            case 'overview':
                return <Overview/>;
            case 'bookings':
                return <BookingsView/>;
            default:
                return <Overview/>;
        }
    };

    return (
        <AdminLayout activeTab={activeTab} onTabChange={setActiveTab} isLoading={status === 'authenticating'}>
            {renderContent()}
        </AdminLayout>
    );
};

export default AdminDashboard;