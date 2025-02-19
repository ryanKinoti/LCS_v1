import {useEffect, useState} from "react"
import {Link, useNavigate} from "react-router-dom"
import {Button} from "@/components/ui/button"
import {Input} from "@/components/ui/input"
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card"
import {Label} from "@/components/ui/label"
import {Lock, Mail} from "lucide-react"
import logoMain from "@/assets/lcs_main_logo.png"
import {useAuth} from "@/contexts/AuthContext.tsx";
import {LoginCredentials} from "@/hooks/auth.ts";

function getDashboardPath(role: 'admin' | 'staff' | 'customer' | null): string {
    switch (role) {
        case 'admin':
            return '/admin/dashboard';
        case 'staff':
            return '/staff/dashboard';
        case 'customer':
            return '/customer/dashboard';
        default:
            return '/';
    }
}

const LoginPage = () => {
    const navigate = useNavigate();
    const {login, user, status} = useAuth();
    const [error, setError] = useState<string>('');

    const [formData, setFormData] = useState<LoginCredentials>({
        email: "",
        password: ""
    });

    const isLoading = status === 'authenticating';

    useEffect(() => {
        if (status === 'authenticated' && user) {
            const redirectPath = sessionStorage.getItem('redirectAfterLogin') || getDashboardPath(user.role);
            sessionStorage.removeItem('redirectAfterLogin');
            navigate(redirectPath, {replace: true});
        }
    }, [user, status, navigate]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
        setError('');
    };

    const validateForm = (): boolean => {
        if (!formData.email) {
            setError('Email is required');
            return false;
        }
        if (!formData.password) {
            setError('Password is required');
            return false;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            setError('Please enter a valid email address');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!validateForm()) return;
        setError("")

        try {
            await login(formData);
            // @ts-expect-error - We're not using the error variable here
        } catch (err: never) {

            let errorMessage = 'Failed to login';

            if (err.code) {
                switch (err.code) {
                    case 'auth/invalid-email':
                        errorMessage = 'Invalid email address';
                        break;
                    case 'auth/user-disabled':
                        errorMessage = 'This account has been disabled';
                        break;
                    case 'auth/user-not-found':
                    case 'auth/wrong-password':
                        errorMessage = 'Invalid email or password';
                        break;
                    default:
                        errorMessage = err.message || 'An error occurred during login';
                }

            } else if (err.response?.data?.detail) {
                errorMessage = err.response.data.detail;
            }

            setError(errorMessage);

        }
    };

    if (status === 'authenticating') {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"/>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#F4F6F8] flex flex-col justify-center items-center px-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <Link to="/">
                        <img src={logoMain || "/placeholder.svg"} alt="Laptop Care" className="h-16 mx-auto"/>
                    </Link>
                    <h1 className="text-3xl font-bold text-[#111517]">Welcome back</h1>
                    <p className="text-[#647987] mt-2">Log in to your account to continue</p>
                </div>
                <Card>
                    <CardHeader>
                        <CardTitle>Log In</CardTitle>
                        <CardDescription>Enter your email and password to access your account</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            {error && (
                                <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md">
                                    {error}
                                </div>
                            )}
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <div className="relative">
                                    <Mail
                                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#647987]"/>
                                    <Input
                                        id="email"
                                        name="email"
                                        type="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                        placeholder="Enter your email"
                                        className="pl-10"
                                        required
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="password">Password</Label>
                                <div className="relative">
                                    <Lock
                                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#647987]"/>
                                    <Input
                                        id="password"
                                        name="password"
                                        type="password"
                                        value={formData.password}
                                        onChange={handleChange}
                                        placeholder="Enter your password"
                                        className="pl-10"
                                        required
                                    />
                                </div>
                            </div>
                            <Button
                                type="submit"
                                className="w-full"
                                disabled={isLoading}
                            >
                                {isLoading ? "Logging in..." : "Log In"}
                            </Button>
                        </form>
                        <div className="mt-4 text-center">
                            <Link to="/forgot-password" className="text-sm text-[#0066FF] hover:underline">
                                Forgot your password?
                            </Link>
                        </div>
                    </CardContent>
                </Card>
                <div className="text-center mt-6">
                    <p className="text-[#647987]">
                        Don&#39;t have an account?{" "}
                        <Link to="/register" className="text-[#0066FF] hover:underline">
                            Sign up
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default LoginPage