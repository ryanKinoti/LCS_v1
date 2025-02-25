import {z} from "zod"
import {ContactMethodTypes, UserRoleTypes} from "@/lib/types/constants/declarations"

const phoneRegex = /^\+?1?\d{9,15}$/;

const baseRegistrationSchema = z.object({
    email: z.string()
        .email("Please enter a valid email address")
        .transform(val => val.toLowerCase()),
    password: z.string()
        .min(8, "Password must be at least 8 characters long")
        .regex(/[0-9]/, "Password must contain at least one number")
        .regex(/[a-zA-Z]/, "Password must contain at least one letter")
        .refine(val => !(/^\d+$/).test(val), "Password cannot be entirely numeric"),
    confirm_password: z.string(),
    first_name: z.string().min(1, "First name is required"),
    last_name: z.string().min(1, "Last name is required"),
    phone_number: z.string()
        .optional()
        .refine(val => !val || phoneRegex.test(val),
            "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."),
    profile_type: z.literal('customer').or(z.literal('staff'))
})

export const customerRegistrationSchema = baseRegistrationSchema.extend({
    profile_type: z.literal('customer'),
    role: z.enum([UserRoleTypes.CLIENT, UserRoleTypes.COMPANY] as const),
    company_name: z.string()
        .optional(),
    preferred_contact: z.enum([
        ContactMethodTypes.EMAIL,
        ContactMethodTypes.PHONE_CALL,
        ContactMethodTypes.SMS
    ] as const)
        .default(ContactMethodTypes.EMAIL)
}).refine(
    (data: z.infer<typeof baseRegistrationSchema> & {
        role: UserRoleTypes.CLIENT | UserRoleTypes.COMPANY,
        company_name?: string
    }) => {
        if (data.password !== data.confirm_password) {
            return {
                message: "Passwords do not match",
                path: ["confirm_password"]
            };
        }

        if (data.role === UserRoleTypes.COMPANY) {
            return !!data.company_name && data.company_name.trim() !== '';
        }
        return true;
    },
    {
        message: "Validation failed",
        path: ["confirm_password"]
    }
);

const isValidTimeFormat = (time: string) => {
    return /^([01]\d|2[0-3]):([0-5]\d)$/.test(time); // HH:MM 24-hour format
};

const isValidTimeRange = (start: string, end: string) => {
    if (!start || !end || !isValidTimeFormat(start) || !isValidTimeFormat(end)) {
        return false;
    }
    const [startHour, startMin] = start.split(':').map(Number);
    const [endHour, endMin] = end.split(':').map(Number);

    // Convert to minutes for easier comparison
    const startTime = startHour * 60 + startMin;
    const endTime = endHour * 60 + endMin;

    return endTime > startTime;
};

const isWithinBusinessHours = (time: string): boolean => {
    if (!time || !isValidTimeFormat(time)) return false;

    // Business hours from constants.py: 08:00 AM to 06:00 PM
    const businessStart = 8 * 60; // 8:00 AM in minutes
    const businessEnd = 18 * 60;  // 6:00 PM in minutes

    const [hour, min] = time.split(':').map(Number);
    const timeInMinutes = hour * 60 + min;

    return timeInMinutes >= businessStart && timeInMinutes <= businessEnd;
};

const dailyScheduleSchema = z.object({
    start: z.string()
        .refine(isValidTimeFormat, "Time must be in HH:MM format")
        .refine(time => isWithinBusinessHours(time), "Time must be within business hours (08:00 AM - 06:00 PM)"),
    end: z.string()
        .refine(isValidTimeFormat, "Time must be in HH:MM format")
        .refine(time => isWithinBusinessHours(time), "Time must be within business hours (08:00 AM - 06:00 PM)")
}).refine(data => isValidTimeRange(data.start, data.end), {
    message: "End time must be after start time",
    path: ["end"]
});

const availabilitySchema = z.object({
    monday: dailyScheduleSchema.optional(),
    tuesday: dailyScheduleSchema.optional(),
    wednesday: dailyScheduleSchema.optional(),
    thursday: dailyScheduleSchema.optional(),
    friday: dailyScheduleSchema.optional()
}).refine(data => {
    // At least one day must have a schedule (similar to Django validation)
    return Object.values(data).some(day => day !== undefined);
}, {
    message: "At least one day must have a schedule",
    path: ["availability"]
});

export const staffRegistrationSchema = baseRegistrationSchema.extend({
    profile_type: z.literal('staff'),
    role: z.enum([
        UserRoleTypes.ADMIN,
        UserRoleTypes.TECHNICIAN,
        UserRoleTypes.RECEPTIONIST
    ] as const),
    specializations: z.array(z.string())
        .min(1, "At least one specialization is required")
        .refine(arr => Array.isArray(arr), "Specializations must be a list"),
    availability: availabilitySchema
        .optional()
        .default({})
}).refine(
    (data: z.infer<typeof baseRegistrationSchema> & {
        specializations: string[],
        availability?: Record<string, { start: string, end: string }>
    }) => data.password === data.confirm_password,
    {
        message: "Passwords do not match",
        path: ["confirm_password"]
    }
);

// Type inference helpers
export type CustomerRegistrationFormData = z.infer<typeof customerRegistrationSchema>
export type StaffRegistrationFormData = z.infer<typeof staffRegistrationSchema>