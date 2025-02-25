export interface RevenueData {
    total_revenue: number;
    bookings_count: number;
    average_booking_value: number;
}

export interface Activity {
    type: string;
    action: string;
    timestamp: string;
    id: number;
}

export interface AdminDashboard {
    total_repairs: number;
    pending_repairs: number;
    completed_repairs: number;
    low_stock_items: number;
    total_inventory_value: number;
    active_staff: number;
    revenue_data: RevenueData;
    recent_activity: Activity[];
}

export interface StaffDashboard {
    assigned_repairs: number;
    pending_repairs: number;
    completed_repairs: number;
    recent_activity: Activity[];
}

export interface CustomerDashboard {
    total_bookings: number;
    active_bookings: number;
    registered_devices: number;
    recent_activity: Activity[];
}

export type Dashboard = AdminDashboard | StaffDashboard | CustomerDashboard;