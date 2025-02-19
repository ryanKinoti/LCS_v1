import api from '@/hooks/api';

export interface DashboardStats {
    // Admin stats
    total_repairs?: number;
    pending_repairs?: number;
    low_stock_items?: number;
    total_inventory_value?: number;
    active_staff?: number;
    revenue_data?: Array<{
        month: string;
        amount: number;
    }>;

    // Staff stats
    assigned_repairs?: number;
    completed_repairs?: number;
    avg_repair_time?: number;

    // Customer stats
    total_bookings?: number;
    active_bookings?: number;
    registered_devices?: number;

    // Common
    recent_activity: Array<{
        type: string;
        id: number;
        description: string;
        date: string;
    }>;
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
    try {
        const response = await api.get('/api/accounts/overview/');
        return response.data;
    } catch (error: any) {
        console.error('Failed to fetch dashboard stats:', error);
        throw new Error(error.response?.data?.detail || 'Failed to fetch dashboard statistics');
    }
};