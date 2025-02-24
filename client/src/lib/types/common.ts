import {ReactNode} from 'react';

export type WithChildren = {
    children: ReactNode;
};

export interface ApiResponse<T> {
    data: T;
    message: string;
    status: number;
}

export type DeviceType = 'laptop' | 'desktop' | 'printer';
export type DeviceRepairStatus = 'completed' | 'returned' | 'in_progress';
export type DeviceSaleStatus = 'new' | 'sold' | 'refurbished';
export type DevicePartStatus = | 'in_stock' | 'out_of_stock' | 'used' | 'defective' | 'disposed';
export type MovementType = 'repair' | 'sale';
export type BookingStatus = | 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'canceled';
export type PaymentStatus = | 'pending' | 'paid' | 'failed' | 'refunded' | 'partial';
export type PaymentMethod = | 'cash' | 'card' | 'mpesa' | 'bank_transfer';
export type TransactionType = | 'booking_payment' | 'parts_purchase' | 'service_payment' | 'staff_salary';

export interface BaseEntity {
    id: string;
    created_at: string;
    updated_at: string;
}

export interface BusinessHours {
    start_time: string;
    end_time: string;
}

export interface DailySchedule {
    start: string;
    end: string;
}

export interface WeeklyAvailability {
    monday?: DailySchedule;
    tuesday?: DailySchedule;
    wednesday?: DailySchedule;
    thursday?: DailySchedule;
    friday?: DailySchedule;
}