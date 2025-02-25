// Definition of interfaces for the dashboard data
import React from "react";

export interface FinancialData {
    date: string;
    total_revenue: string;
    total_expenses: string;
    net_income: string;
}

export interface FinancialSummary {
    total_revenue: number;
    total_expenses: number;
    service_revenue: number;
    parts_revenue: number;
    outstanding_payments: number;
    net_revenue: number;
    profit_margin: number;
}

export interface BookingStatistics {
    active_bookings: number;
    pending_bookings: number;
    completed_bookings: number;
    canceled_bookings: number;
    total_bookings: number;
}

export interface InventoryPart {
    id: number;
    name: string;
    model: string;
    serial_number: string;
    status: string;
    quantity: number;
}

export interface InventoryAlerts {
    total_count: number;
    items: InventoryPart[];
}

export interface BookingDetail {
    id: number;
    job_card_number: string;
    customer: {
        id: number;
        role: string;
        company_name: string | null;
    };
    technician: {
        id: number;
        role: string;
        specializations: string[];
    } | null;
    detailed_service: {
        id: number;
        service_name: string;
        device: string;
        price: string;
    };
    status: string;
    scheduled_time: string;
    device: {
        id: number;
        device_type: string;
        brand: string;
        model: string;
        serial_number: string;
        repair_status: string;
    } | null;
    parts_used: Array<{
        id: number;
        part_details: {
            id: number;
            name: string;
            model: string;
            serial_number: string;
            status: string;
            quantity: number;
        };
        quantity: number;
    }>;
    total_parts_cost: number;
    payment_status: string;
    notes: string;
    diagnosis: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface AdminDashboardData {
    booking_statistics: BookingStatistics;
    inventory_alerts: InventoryAlerts;
    financial_snapshot: {
        data: FinancialData[];
        summary: FinancialSummary;
    };
    recent_activities: BookingDetail[];
}

export interface StaffDashboardData {
    assigned_repairs: number;
    pending_repairs: number;
    completed_repairs: number;
    // Add more staff-specific fields as needed
}

export interface CustomerDashboardData {
    total_bookings: number;
    active_bookings: number;
    completed_bookings: number;
}

export type DashboardData = AdminDashboardData | StaffDashboardData | CustomerDashboardData;

// setup of necessary properties for the dashboard data
export interface AdminLayoutProps {
    children: React.ReactNode;
    activeTab: string;
    onTabChange: (tab: string) => void;
    isLoading?: boolean;
}