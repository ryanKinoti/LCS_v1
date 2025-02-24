import api from '@/hooks/api.ts';
import axios from "axios";

// BookingList Interfaces
export interface User {
    id: number;
    email: string;
    first_name: string | null;
    last_name: string | null;
    phone_number: string | null;
    email_verified: boolean;
    phone_verified: boolean;
}

export interface CustomerProfile {
    id: number;
    user: User;
    customer_role: 'client' | 'company';
    preferred_contact: 'email' | 'phone';
    company_name?: string;
    address?: string;
    notes?: string;
    created_at: string;
    updated_at: string;
}

export interface StaffProfile {
    id: number;
    user: User;
    role: 'technician' | 'admin' | 'receptionist';
    specializations: string[];
    availability: Record<string, { start: string; end: string }>;
    created_at: string;
    updated_at: string;
}

export interface Device {
    id: number;
    customer?: User;
    device_type: 'laptop' | 'desktop' | 'printer';
    brand: string;
    model: string;
    serial_number: string;
    created_at: string;
}

export interface DevicePart {
    id: number;
    customer_laptop?: Device;
    name: string;
    model: string;
    serial_number: string;
    price: number | null;
    quantity: number | null;
    category: string;
    status: 'in_stock' | 'out_of_stock' | 'used' | 'defective' | 'disposed';
    warranty_months: number;
    minimum_stock: number;
    created_at: string;
}

export interface Service {
    id: number;
    name: string;
    category: {
        id: number;
        name: string;
        description?: string;
    };
    description?: string;
    estimated_time: string;
    active: boolean;
}

export interface DetailedService {
    id: number;
    service: Service;
    device: string;
    changes_to_make: string;
    price: number;
    notes?: string;
}

export interface BookingPart {
    id: number;
    part: DevicePart;
    quantity: number;
    total_cost: number;
}

export interface BookingListItem {
    id: number;
    job_card_number: string;
    customer_name: string;
    customer_contact: string;
    preferred_contact: string;
    service_name: string;
    device_info: string;
    scheduled_time: string;
    status: BookingStatus;
    payment_status: PaymentStatus;
}

export interface BookingDetail {
    id: number;
    job_card_number: string;
    customer: CustomerProfile;
    technician: StaffProfile | null;
    detailed_service: DetailedService;
    device: Device;
    status: BookingStatus;
    scheduled_time: string;
    parts_used: BookingPart[];
    is_active: boolean;

    total_parts_cost: number;
    payment_status: PaymentStatus;
    total_cost: number;

    notes: string;
    diagnosis: string;
    created_at: string;
    updated_at: string;
}

export interface BookingStats {
    active_repairs: number;
    pending_repairs: number;
    completed_today: number;
    recent_bookings: BookingListItem[];
}

// NewBooking Interfaces
export interface CustomerFormData {
    type: 'existing' | 'new';
    email: string;
    firstName?: string;
    lastName?: string;
    phoneNumber?: string;
    preferredContact?: 'email' | 'phone';
}

export interface DeviceFormData {
    deviceType: string;
    brand: string;
    model: string;
    serialNumber: string;
}

export interface DevicePartFormData {
    name: string;
    model: string;
    serial_number: string;
    category: string;
    warranty_months: number;
    status: 'in_stock' | 'used';
    quantity?: number;
}

export interface BookingFormData {
    serviceId: string;
    scheduledTime: string;
    notes?: string;
}

export interface CustomerResponse {
    id: number;
    customer_profile: CustomerProfile;
    message?: string;
}

export interface DeviceResponse {
    id: number;
    device: Device;
    message?: string;
}

export type BookingStatus = 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded';

export interface ApiResponse<T> {
    data: T;
    message?: string;
}

export interface ErrorResponse {
    detail: string;
    errors?: Record<string, string[]>;
}

export const getAllBookings = async (): Promise<ApiResponse<BookingListItem[]>> => {
    try {
        const response = await api.get('/api/bookings/all/');
        return {
            data: response.data,
            message: response.statusText
        };
    } catch (error: unknown) {
        console.error('Failed to fetch bookings:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to fetch bookings');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to fetch bookings');
    }
};

export const getBookingStats = async (): Promise<ApiResponse<BookingStats>> => {
    try {
        const response = await api.get('/api/bookings/all/dashboard_stats/');
        return response.data;
    } catch (error: unknown) {
        console.error('Failed to fetch booking stats:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to fetch booking stats');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to fetch booking stats');
    }
};

export const getBookingDetailById = async (id: number): Promise<ApiResponse<BookingDetail>> => {
    try {
        const response = await api.get(`/api/bookings/single/${id}/`);
        return {
            data: response.data,
            message: response.statusText
        };
    } catch (error: unknown) {
        console.error('Failed to fetch booking details:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to fetch booking details');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to fetch booking details');
    }
};

export const updateBooking = async (id: number, data: Partial<BookingDetail>): Promise<BookingDetail> => {
    try {
        const response = await api.patch(`/api/bookings/all/${id}/`, data);
        return response.data;
    } catch (error: unknown) {
        console.error('Failed to update booking:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to update booking');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to update booking');
    }
};

export const deleteBooking = async (id: number): Promise<void> => {
    try {
        await api.post(`/api/bookings/all/${id}/`);
    } catch (error: unknown) {
        console.error('Failed to delete booking:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to delete booking');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to delete booking');
    }
};

export const findCustomerByEmail = async (email: string): Promise<ApiResponse<CustomerProfile>> => {
    try {
        const response = await api.get(`/api/user/customer-profiles/?email=${email}`);
        console.log(response.data);
        return {
            data: response.data,
            message: response.statusText
        };
    } catch (error: unknown) {
        console.error('Failed to find customer:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to find customer');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to find customer');
    }
};
export const createCustomer = async (data: CustomerFormData): Promise<ApiResponse<CustomerProfile>> => {
    try {
        const tempPassword = Math.random().toString(36).slice(-8);

        const response = await api.post("/api/user/register/", {
            email: data.email,
            password: tempPassword,
            confirm_password: tempPassword,
            first_name: data.firstName,
            last_name: data.lastName,
            phone_number: data.phoneNumber,
            preferred_contact: data.preferredContact,
            profile_type: "customer",
        });

        return {
            data: response.data,
            message: tempPassword // Return temporary password in message
        };
    } catch (error: unknown) {
        console.error('Failed to create customer:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to create customer');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to create customer');
    }
};

export const createDevice = async (data: DeviceFormData, customerId: number): Promise<ApiResponse<Device>> => {
    try {
        const response = await api.post("/api/inventory/devices/", {
            ...data,
            customer: customerId,
        });
        return {
            data: response.data,
            message: response.statusText
        };
    } catch (error: unknown) {
        console.error('Failed to create device:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to create device');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to create device');
    }
};

export const addDeviceParts = async (
    deviceId: number,
    parts: DevicePartFormData[]
): Promise<ApiResponse<DevicePart[]>> => {
    try {
        const promises = parts.map(part =>
            api.post("/api/inventory/parts/", {
                ...part,
                customer_laptop: deviceId,
                status: 'used', // Since these are parts attached to a customer's device
                minimum_stock: 1
            })
        );
        const responses = await Promise.all(promises);
        return {
            data: responses.map(response => response.data),
            message: "Device parts added successfully"
        };
    } catch (error: unknown) {
        console.error('Failed to add device parts:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to add device parts');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to add device parts');
    }
};

export const getDetailedServices = async (): Promise<ApiResponse<DetailedService[]>> => {
    try {
        const response = await api.get('/api/services/detailed/');
        return {
            data: response.data,
            message: response.statusText
        };
    } catch (error: unknown) {
        console.error('Failed to fetch services:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to fetch services');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to fetch services');
    }
};

export const initiateBooking = async (
    data: BookingFormData,
    customerId: number,
    deviceId: number
): Promise<ApiResponse<BookingDetail>> => {
    try {
        const response = await api.post("/api/bookings/all/", {
            customer_id: customerId,
            device_id: deviceId,
            detailed_service_id: data.serviceId,
            scheduled_time: data.scheduledTime,
            notes: data.notes,
            status: "pending",
        });

        return {
            data: response.data,
            message: response.statusText
        };
    } catch (error: unknown) {
        console.error('Failed to create booking:', error);
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.detail || 'Failed to create booking');
        }
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Failed to create booking');
    }
};