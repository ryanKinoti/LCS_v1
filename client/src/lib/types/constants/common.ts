import {
    SelectOption,
    //devices
    DeviceType,
    RepairStatus,
    SaleStatus,
    //device parts
    PartStatus,
    MovementType,
    //bookings
    BookingStatusTypes,
    //users
    UserRoleTypes,
    ContactMethodTypes
} from "@/lib/types/constants/declarations.ts";

export class Devices {
    private static instance: Devices;

    private constructor() {
    }

    static getInstance(): Devices {
        if (!Devices.instance) {
            Devices.instance = new Devices();
        }
        return Devices.instance;
    }

    get TYPES(): SelectOption[] {
        return Object.entries(DeviceType).map(([key, value]) => ({
            value,
            label: this.formatLabel(key)
        }));
    }

    get REPAIR_STATUSES(): SelectOption[] {
        return Object.entries(RepairStatus).map(([key, value]) => ({
            value,
            label: this.formatLabel(key)
        }));
    }

    get SALE_STATUSES(): SelectOption[] {
        return Object.entries(SaleStatus).map(([key, value]) => ({
            value,
            label: this.formatLabel(key)
        }));
    }

    private formatLabel(key: string): string {
        return key.toLowerCase()
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    isValidDeviceType(type: string): type is DeviceType {
        return Object.values(DeviceType).includes(type as DeviceType);
    }

    isValidRepairStatus(status: string): status is RepairStatus {
        return Object.values(RepairStatus).includes(status as RepairStatus);
    }

    isValidSaleStatus(status: string): status is SaleStatus {
        return Object.values(SaleStatus).includes(status as SaleStatus);
    }
}

export class DeviceParts {
    private static instance: DeviceParts;

    private constructor() {
    }

    static getInstance(): DeviceParts {
        if (!DeviceParts.instance) {
            DeviceParts.instance = new DeviceParts();
        }
        return DeviceParts.instance;
    }

    get PART_STATUSES(): SelectOption[] {
        return Object.entries(PartStatus).map(([key, value]) => ({
            value,
            label: this.formatLabel(key)
        }));
    }

    get MOVEMENT_TYPES(): SelectOption[] {
        return Object.entries(MovementType).map(([key, value]) => ({
            value,
            label: this.formatLabel(key)
        }));
    }

    private formatLabel(key: string): string {
        return key.toLowerCase()
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    isValidPartStatus(status: string): status is PartStatus {
        return Object.values(PartStatus).includes(status as PartStatus);
    }

    isValidMovementType(type: string): type is MovementType {
        return Object.values(MovementType).includes(type as MovementType);
    }
}

export class BookingStatus {
    private static instance: BookingStatus;

    private constructor() {
    }

    static getInstance(): BookingStatus {
        if (!BookingStatus.instance) {
            BookingStatus.instance = new BookingStatus();
        }
        return BookingStatus.instance;
    }

    get STATUSES(): SelectOption[] {
        return Object.entries(BookingStatusTypes).map(([key, value]) => ({
            value,
            label: this.formatLabel(key)
        }));
    }

    private formatLabel(key: string): string {
        return key.toLowerCase()
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    isValidBookingStatus(status: string): status is BookingStatusTypes {
        return Object.values(BookingStatusTypes).includes(status as BookingStatusTypes);
    }
}

export class UserRoles {
    private static instance: UserRoles;

    private constructor() {
    }

    static getInstance(): UserRoles {
        if (!UserRoles.instance) {
            UserRoles.instance = new UserRoles();
        }
        return UserRoles.instance;
    }

    get ROLES(): SelectOption[] {
        return Object.entries(UserRoleTypes).map(([key, value]) => ({
            value,
            label: this.formatLabel(key)
        }));
    }

    private formatLabel(key: string): string {
        return key.toLowerCase()
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    isValidRole(role: string): role is UserRoleTypes {
        return Object.values(UserRoleTypes).includes(role as UserRoleTypes);
    }
}

export class ContactMethods {
    private static instance: ContactMethods;

    private constructor() {
    }

    static getInstance(): ContactMethods {
        if (!ContactMethods.instance) {
            ContactMethods.instance = new ContactMethods();
        }
        return ContactMethods.instance;
    }

    get METHODS(): SelectOption[] {
        return Object.entries(ContactMethodTypes).map(([key, value]) => ({
            value,
            label: this.formatLabel(key)
        }));
    }

    private formatLabel(key: string): string {
        return key.toLowerCase()
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    isValidContactMethod(method: string): method is ContactMethodTypes {
        return Object.values(ContactMethodTypes).includes(method as ContactMethodTypes);
    }
}


export const devices = Devices.getInstance();
export const deviceParts = DeviceParts.getInstance();
export const bookingStatus = BookingStatus.getInstance();
export const userRoles = UserRoles.getInstance();
export const contactMethods = ContactMethods.getInstance();