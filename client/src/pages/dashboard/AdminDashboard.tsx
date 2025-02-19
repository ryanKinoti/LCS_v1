import {useState} from 'react';
import AdminLayout from '@/components/dashboards/layouts/AdminLayout';
import Overview from '@/components/dashboards/common/Overview.tsx';
import BookingsView from '@/components/dashboards/common/booking/BookingsView';

const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState('overview');

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
        <AdminLayout activeTab={activeTab} onTabChange={setActiveTab}>
            {renderContent()}
        </AdminLayout>
    );
};

export default AdminDashboard;