import React, {ReactElement} from 'react';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer} from 'recharts';
import {
    Users,
    Laptop,
    Package,
    AlertCircle,
    Calendar,
    Bell,
    Settings,
    Loader2,
} from 'lucide-react';
import {useAuth} from '@/contexts/AuthContext';
import {formatDistance} from 'date-fns';

const Overview = () => {
    const {user} = useAuth();

    if (!user) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin"/>
            </div>
        );
    }

    // Extract the necessary data
    const dashboardData = user.dashboard;
    const userRole = user.role;
    // const userInfo = user.user;

    return (
        <div className="min-h-screen bg-[#F8F9FA]">
            <main className="container mx-auto p-4">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    {userRole === 'admin' && (
                        <>
                            <StatCard
                                title="Total Repairs"
                                value={dashboardData.total_repairs}
                                icon={<Laptop className="h-6 w-6"/>}
                                color="#0066FF"/>
                            <StatCard
                                title="Pending Repairs"
                                value={dashboardData.pending_repairs}
                                icon={<AlertCircle className="h-6 w-6"/>}
                                color="#DC3545"/>
                            <StatCard
                                title="Low Stock Items"
                                value={dashboardData.low_stock_items}
                                icon={<Package className="h-6 w-6"/>}
                                color="#28A745"/>
                            <StatCard
                                title="Active Staff"
                                value={dashboardData.active_staff}
                                icon={<Users className="h-6 w-6"/>}
                                color="#FFC107"/>
                        </>
                    )}

                    {userRole === 'staff' && (
                        <>
                            <StatCard
                                title="Assigned Repairs"
                                value={dashboardData.assigned_repairs || 0}
                                icon={<Laptop/>}
                                color="#0066FF"
                            />
                            <StatCard
                                title="Pending Repairs"
                                value={dashboardData.pending_repairs || 0}
                                icon={<AlertCircle/>}
                                color="#DC3545"
                            />
                            <StatCard
                                title="Completed Repairs"
                                value={dashboardData.completed_repairs || 0}
                                icon={<Package/>}
                                color="#28A745"
                            />
                        </>
                    )}

                    {userRole === 'customer' && (
                        <>
                            <StatCard
                                title="Total Bookings"
                                value={dashboardData.total_bookings || 0}
                                icon={<Calendar/>}
                                color="#0066FF"
                            />
                            <StatCard
                                title="Active Bookings"
                                value={dashboardData.active_bookings || 0}
                                icon={<AlertCircle/>}
                                color="#DC3545"
                            />
                            <StatCard
                                title="Registered Devices"
                                value={dashboardData.registered_devices || 0}
                                icon={<Laptop/>}
                                color="#28A745"
                            />
                        </>
                    )}
                </div>

                {/* Charts and Additional Info */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Revenue Chart (Admin Only) */}
                    {userRole === 'admin' && dashboardData.revenue_data && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Revenue Overview</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="h-72">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={dashboardData.revenue_data}>
                                            <CartesianGrid strokeDasharray="3 3"/>
                                            <XAxis dataKey="month"/>
                                            <YAxis/>
                                            <Tooltip/>
                                            <Line
                                                type="monotone"
                                                dataKey="amount"
                                                stroke="#0066FF"
                                                strokeWidth={2}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Recent Activity */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Recent Activity</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {dashboardData.recent_activity.map((activity, index) => (
                                    <div key={`${activity.type}-${activity.id}-${index}`}
                                         className="flex items-start space-x-4">
                                        <div className="rounded-full p-2 bg-blue-100">
                                            {activity.type === 'booking' ? (
                                                <Calendar className="h-4 w-4 text-blue-600"/>
                                            ) : (
                                                <Package className="h-4 w-4 text-blue-600"/>
                                            )}
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm text-gray-800">{activity.description}</p>
                                            <p className="text-xs text-gray-500">
                                                {formatDistance(new Date(activity.date), new Date(), {addSuffix: true})}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Quick Actions */}
                    {userRole === 'admin' && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Quick Actions</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-wrap gap-4">
                                    <QuickActionButton
                                        icon={<Calendar/>}
                                        label="New Booking"
                                        onClick={() => window.location.href = '/admin/bookings/new'}/>
                                    <QuickActionButton
                                        icon={<Package/>}
                                        label="Add Inventory"
                                        onClick={() => window.location.href = '/admin/inventory/new'}/>
                                    <QuickActionButton
                                        icon={<Bell/>}
                                        label="Notifications"
                                        onClick={() => window.location.href = '/admin/notifications'}/>
                                    <QuickActionButton
                                        icon={<Settings/>}
                                        label="Settings"
                                        onClick={() => window.location.href = '/admin/settings'}/>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </main>
        </div>
    );
};

// Stat Card Component
interface StatCardProps {
    title: string;
    value: number;
    icon: ReactElement;
    color: string;
}

const StatCard: React.FC<StatCardProps> = ({title, value, icon, color}) => (
    <Card>
        <CardContent className="flex items-center p-4">
            <div
                className="rounded-full p-3 mr-4"
                style={{backgroundColor: `${color}20`}}>
                {React.cloneElement(icon, {color} as React.SVGProps<SVGSVGElement>)}
            </div>
            <div>
                <p className="text-sm text-gray-600">{title}</p>
                <p className="text-2xl font-bold text-[#343A40]">{value}</p>
            </div>
        </CardContent>
    </Card>
);

// Quick Action Button Component
interface QuickActionButtonProps {
    icon: ReactElement;
    label: string;
    onClick: () => void;
}

const QuickActionButton: React.FC<QuickActionButtonProps> = ({icon, label, onClick}) => (
    <button
        onClick={onClick}
        className="flex items-center justify-center p-4 bg-[#F4F6F8] hover:bg-[#E2E6EA] rounded-lg transition-colors duration-200">
        <div className="flex flex-col items-center">
            {React.cloneElement(icon, {
                className: "h-6 w-6 mb-2 text-[#004085]",
            } as React.SVGProps<SVGSVGElement>)}
            <span className="text-sm text-[#343A40]">{label}</span>
        </div>
    </button>
);

export default Overview;