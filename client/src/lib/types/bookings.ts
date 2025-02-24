import { BaseEntity, BookingStatus } from '@/lib/types/common';
import { User } from '@/lib/types/auth';

export interface Booking extends BaseEntity {
    customer: User;
    device_type: string;
    device_details: {
        brand: string;
        model: string;
        serial_number: string;
    };
    status: BookingStatus;
    scheduled_date: string;
    notes?: string;
}