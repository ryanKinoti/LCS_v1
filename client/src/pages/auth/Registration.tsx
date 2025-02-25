import React, {useState} from 'react'
import {Link, useNavigate} from "react-router-dom";
import {Button} from "@/components/ui/button"
import {Input} from "@/components/ui/input"
import {Card, CardContent} from "@/components/ui/card"
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select"
import {RadioGroup, RadioGroupItem} from "@/components/ui/radio-group"
import {Label} from "@/components/ui/label"
import {User, Mail, Phone, Lock} from 'lucide-react'
import logoMain from "@/assets/lcs_main_logo.png"
import {useAuth} from "@/contexts/AuthContext.tsx";
import {CustomerRegistrationFormData, customerRegistrationSchema} from "@/lib/validators/auth";
import {transformBackendErrors} from "@/lib/validators/root";
import {ContactMethodTypes, UserRoleTypes} from "@/lib/types/constants/declarations";

const RegistrationPage = () => {

    const navigate = useNavigate();
    const {register, status} = useAuth();
    const [error, setError] = useState<string | Record<string, string>>('');
    const isLoading = status === 'authenticating';

    const [formData, setFormData] = useState<CustomerRegistrationFormData>({
        email: '',
        password: '',
        confirm_password: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        profile_type: 'customer',
        role: UserRoleTypes.CLIENT,
        preferred_contact: ContactMethodTypes.EMAIL,
        company_name: '',
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleRoleChange = (value: string) => {
        // Only allow valid role values
        if (value === UserRoleTypes.CLIENT || value === UserRoleTypes.COMPANY) {
            setFormData(prev => ({
                ...prev,
                role: value as UserRoleTypes.CLIENT | UserRoleTypes.COMPANY,
                // Clear company name if switching from company to client
                company_name: value === UserRoleTypes.CLIENT ? '' : prev.company_name
            }));
        }
    };

    const validateForm = async () => {
        try {
            const result = await customerRegistrationSchema.safeParseAsync(formData);

            if (result.success) {
                setError('');
                return result.data;
            } else {
                // Extract and format errors from Zod
                const formattedErrors: Record<string, string> = {};
                result.error.errors.forEach(err => {
                    formattedErrors[err.path.join('.')] = err.message;
                });
                setError(formattedErrors);
                return null;
            }
        } catch (error) {
            console.error("Validation error:", error);
            setError({form: "An unexpected validation error occurred"});
            return null;
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        const validData = await validateForm();
        if (!validData) return;

        try {
            await register(formData);
            navigate('/login', {state: {registered: true}});
        } catch (error) {
            if (error instanceof Error) {
                setError(error.message);
            } else if (typeof error === 'object' && error !== null) {
                // Handle potential backend validation errors
                setError(transformBackendErrors(error as Record<string, string[] | string>));
            } else {
                setError('An unexpected error occurred during registration');
            }
        }
    };

    const showCompanyField = formData.role === UserRoleTypes.COMPANY;

    return (
        <div className="min-h-screen bg-[#F4F6F8] flex flex-col items-center justify-center px-4">
            <div className="w-full max-w-lg space-y-6">
                <div className="text-center">
                    <Link to="/">
                        <img src={logoMain || "/placeholder.svg"} alt="Laptop Care" className="h-16 mx-auto"/>
                    </Link>
                </div>

                <Card className="border-0 shadow-lg bg-white rounded-xl">
                    <CardContent className="p-8">
                        <div className="text-center mb-6">
                            <h1 className="text-2xl font-bold text-[#111517]">Create an account</h1>
                            <p className="text-[#647987] mt-2">Sign up to get started with Laptop Care</p>
                        </div>

                        <div className="space-y-6">
                            <h2 className="text-xl font-semibold">Sign Up</h2>
                            <p className="text-[#647987]">Enter your details to create your account</p>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                {/* Full Name Fields */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="relative">
                                        <User className="absolute left-3 top-3 h-5 w-5 text-gray-400"/>
                                        <Input
                                            type="text"
                                            placeholder="First Name"
                                            className="pl-10 py-2 w-full bg-white"
                                            name="first_name"
                                            value={formData.first_name}
                                            onChange={handleChange}
                                            disabled={isLoading}/>
                                    </div>
                                    <div className="relative">
                                        <User className="absolute left-3 top-3 h-5 w-5 text-gray-400"/>
                                        <Input
                                            type="text"
                                            placeholder="Last Name"
                                            className="pl-10 py-2 w-full bg-white"
                                            name="last_name"
                                            value={formData.last_name}
                                            onChange={handleChange}
                                            disabled={isLoading}/>
                                    </div>
                                </div>

                                {/* Email & Phone Number Fields */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400"/>
                                        <Input
                                            type="email"
                                            placeholder="Email Address"
                                            className="pl-10 py-2 w-full bg-white"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleChange}
                                            disabled={isLoading}/>
                                    </div>
                                    <div className="relative">
                                        <Phone className="absolute left-3 top-3 h-5 w-5 text-gray-400"/>
                                        <Input
                                            type="tel"
                                            placeholder="Phone Number"
                                            className="pl-10 py-2 w-full bg-white"
                                            name="phone_number"
                                            value={formData.phone_number}
                                            onChange={handleChange}
                                            disabled={isLoading}/>
                                    </div>
                                </div>

                                {/* Preferred Contact (Standalone Field with Label) */}
                                <div>
                                    <label
                                        className="block text-sm font-medium text-gray-700 mb-1"
                                        htmlFor="preferredContact">
                                        Preferred Contact
                                    </label>
                                    <Select
                                        value={formData.preferred_contact}
                                        onValueChange={(value) => {
                                            if (Object.values(ContactMethodTypes).includes(value as ContactMethodTypes)) {
                                                setFormData({
                                                    ...formData,
                                                    preferred_contact: value as ContactMethodTypes
                                                });
                                            }
                                        }}>
                                        <SelectTrigger className="w-full">
                                            <SelectValue placeholder="Select preferred contact method"/>
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="email">Email</SelectItem>
                                            <SelectItem value="phone_call">Phone</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                {/* Account Type */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="relative">
                                        <Label className="text-base">Account Type</Label>
                                        <RadioGroup
                                            defaultValue="client"
                                            value={formData.role}
                                            onValueChange={handleRoleChange}
                                            className="grid grid-cols-2 gap-4"
                                            disabled={isLoading}>
                                            <div className="flex items-center space-x-2">
                                                <RadioGroupItem
                                                    value="client"
                                                    id="client"
                                                    className="border-2 border-gray-200"/>
                                                <Label
                                                    htmlFor="client"
                                                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                                    Individual Client
                                                </Label>
                                            </div>

                                            <div className="flex items-center space-x-2">
                                                <RadioGroupItem
                                                    value="company"
                                                    id="company"
                                                    className="border-2 border-gray-200"/>
                                                <Label
                                                    htmlFor="company"
                                                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                                    Company
                                                </Label>
                                            </div>
                                        </RadioGroup>
                                    </div>
                                </div>

                                {/* Password Fields */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400"/>
                                        <Input
                                            type="password"
                                            placeholder="Password"
                                            className="pl-10 py-2 w-full bg-white"
                                            name="password"
                                            value={formData.password}
                                            onChange={handleChange}
                                            disabled={isLoading}/>
                                    </div>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400"/>
                                        <Input
                                            type="password"
                                            placeholder="Confirm Password"
                                            className="pl-10 py-2 w-full bg-white"
                                            name="confirm_password"
                                            value={formData.confirm_password}
                                            onChange={handleChange}
                                            disabled={isLoading}/>
                                    </div>
                                </div>

                                {showCompanyField && (
                                    <div className="relative">
                                        <Input
                                            type="text"
                                            placeholder="Company Name"
                                            name="company_name"
                                            value={formData.company_name}
                                            onChange={handleChange}
                                            className="pl-10 py-2 w-full bg-white"
                                            disabled={isLoading}
                                        />
                                    </div>
                                )}

                                {/* Sign-Up Button */}
                                <Button
                                    type="submit"
                                    className="w-full bg-[#0066FF] text-white py-6 rounded-lg hover:bg-blue-700"
                                    disabled={isLoading}>
                                    {isLoading ? 'Signing up...' : 'Sign Up'}
                                </Button>
                                {typeof error === 'object' && error !== null && 'form' in error && (
                                    <p className="text-red-500 text-center mt-2">{error.form}</p>
                                )}
                            </form>
                        </div>
                    </CardContent>
                </Card>

                <div className="text-center">
                    <p className="text-[#647987]">
                        Already have an account?{" "}
                        <a href="/login" className="text-[#0066FF] hover:underline">
                            Log in
                        </a>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default RegistrationPage