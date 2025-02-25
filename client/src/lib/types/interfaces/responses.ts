import {User} from "@/lib/types/interfaces/common";
import {UserRoleTypes} from "@/lib/types/constants/declarations";
import {AdminDashboardData, CustomerDashboardData, StaffDashboardData} from "@/lib/types/interfaces/dashboards";

export interface UserResponse {
    user: User;
    profile?: {
        id?: number;
        role?: string;
        specializations?: string[];
    };
    role: Extract<UserRoleTypes, UserRoleTypes.ADMIN | UserRoleTypes.STAFF | UserRoleTypes.CUSTOMER>;
}

export interface RegisterResponse {
    message: string;
    data: {
        email: string;
        login_token: string;
    };
}

export interface DashboardResponse {
    user: User;
    role: Extract<UserRoleTypes, UserRoleTypes.ADMIN | UserRoleTypes.STAFF | UserRoleTypes.CUSTOMER>;
    dashboard: AdminDashboardData | StaffDashboardData | CustomerDashboardData;
}

export function isAdminDashboard(dashboard: any): dashboard is AdminDashboardData {
    return (
        dashboard &&
        'booking_statistics' in dashboard &&
        'inventory_alerts' in dashboard &&
        'financial_snapshot' in dashboard
    );
}

export function isStaffDashboard(dashboard: any): dashboard is StaffDashboardData {
    return (
        dashboard &&
        'assigned_repairs' in dashboard &&
        'pending_repairs' in dashboard &&
        'completed_repairs' in dashboard &&
        !('booking_statistics' in dashboard)
    );
}

export function isCustomerDashboard(dashboard: any): dashboard is CustomerDashboardData {
    return (
        dashboard &&
        'total_bookings' in dashboard &&
        'active_bookings' in dashboard &&
        'completed_bookings' in dashboard &&
        !('booking_statistics' in dashboard)
    );
}