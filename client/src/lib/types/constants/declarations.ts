export interface SelectOption {
    value: string;
    label: string;
}

export enum DeviceType {
    LAPTOP = 'laptop',
    DESKTOP = 'desktop',
    PRINTER = 'printer'
}

export enum RepairStatus {
    COMPLETED = 'completed',
    RETURNED = 'returned',
    IN_PROGRESS = 'in_progress'
}

export enum SaleStatus {
    NEW = 'new',
    SOLD = 'sold',
    REFURBISHED = 'refurbished'
}

export enum PartStatus {
    IN_STOCK = 'in_stock',
    OUT_OF_STOCK = 'out_of_stock',
    USED = 'used',
    DEFECTIVE = 'defective',
    DISPOSED = 'disposed'
}

export enum MovementType {
    REPAIR = 'repair',
    SALE = 'sale'
}

export enum BookingStatusTypes {
    PENDING = 'pending',
    CONFIRMED = 'confirmed',
    IN_PROGRESS = 'in_progress',
    COMPLETED = 'completed',
    CANCELLED = 'canceled'
}

export enum UserRoleTypes {
    CLIENT = 'client',
    COMPANY = 'company',

    ADMIN = 'admin',
    TECHNICIAN = 'technician',
    RECEPTIONIST = 'receptionist',

    STAFF = 'staff',
    CUSTOMER = 'customer'
}

export enum ContactMethodTypes {
    EMAIL = 'email',
    PHONE_CALL = 'phone_call',
    SMS = 'sms'
}

export enum ToastType {
    SUCCESS = 'success',
    ERROR = 'error',
    WARNING = 'warning',
    INFO = 'info',
    DEFAULT = 'default'
}

export enum ModalType {
    CONFIRMATION = 'confirmation',
    FORM = 'form',
    ALERT = 'alert',
    CUSTOM = 'custom'
}