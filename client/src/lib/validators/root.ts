import {z} from "zod";
import {useState} from "react";

export interface ValidationResult<T> {
    success: boolean;
    data?: T;
    errors?: Record<string, string>;
    touched?: Set<string>;
}

export type ValidationErrors = Record<string, string>;

export function useValidation<T extends z.ZodObject<any>>(schema: T) {
    const [errors, setErrors] = useState<ValidationErrors>({});
    const [touched, setTouched] = useState<Set<string>>(new Set());

    const validate = async (data: unknown): Promise<ValidationResult<z.infer<T>>> => {
        try {
            const validData = await schema.parseAsync(data);
            setErrors({});
            return {
                success: true,
                data: validData,
                touched: touched
            };
        } catch (error) {
            if (error instanceof z.ZodError) {
                const newErrors = error.errors.reduce((acc, curr) => ({
                    ...acc,
                    [curr.path.join('.')]: curr.message
                }), {});
                setErrors(newErrors);
                return {
                    success: true,
                    data: newErrors,
                    touched: touched
                };
            }
            console.error('Validation error:', error);
            throw new Error('Validation failed due to an unexpected error');
        }
    };

    const validateField = async (field: string, value: unknown): Promise<boolean> => {
        try {
            const fieldSchema = schema.shape?.[field];
            if (fieldSchema) {
                await fieldSchema.parseAsync(value);
                clearFieldError(field);
                return true;
            }
            return false;
        } catch (error) {
            if (error instanceof z.ZodError) {
                const [firstError] = error.errors;
                setFieldError(field, firstError.message);
            }
            return false;
        }
    };

    const setFieldTouched = (field: string, isTouched: boolean = true) => {
        const newTouched = new Set(touched);
        if (isTouched) {
            newTouched.add(field);
        } else {
            newTouched.delete(field);
        }
        setTouched(newTouched);
    };

    const setFieldError = (field: string, message: string) => {
        setErrors(prev => ({...prev, [field]: message}));
    };

    const clearErrors = () => {
        setErrors({});
        setTouched(new Set());
    };

    const clearFieldError = (field: string) => {
        setErrors(prev => {
            const {[field]: _, ...rest} = prev;
            return rest;
        });
    };

    const shouldShowError = (field: string): boolean => {
        return touched.has(field) && field in errors;
    };

    return {
        errors,
        touched,
        validate,
        validateField,
        setFieldError,
        setFieldTouched,
        clearErrors,
        clearFieldError,
        shouldShowError,
        hasErrors: Object.keys(errors).length > 0
    };
}

export const transformBackendErrors = (backendErrors: Record<string, string[] | string>): ValidationErrors => {
    return Object.entries(backendErrors).reduce((acc, [key, messages]) => ({
        ...acc,
        [key]: Array.isArray(messages) ? messages[0] : messages
    }), {});
};