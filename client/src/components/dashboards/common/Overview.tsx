import React from 'react';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer} from 'recharts';
import {
    Laptop,
    Package,
    AlertCircle,
    Calendar,
    Loader2,
    Clock, AlertTriangle, DollarSign, ExternalLink
} from 'lucide-react';
import {useAuth} from '@/contexts/AuthContext';
import {isAdminDashboard} from '@/lib/types/interfaces/responses';
import {AdminDashboardData} from '@/lib/types/interfaces/dashboards';
import {QuickActionButtonProps, StatCardProps} from "@/lib/types/interfaces/overview.ts";

const StatCard: React.FC<StatCardProps> = ({title, value, icon, color, subtitle}) => (
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
                {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
            </div>
        </CardContent>
    </Card>
);

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

const prepareFinancialChartData = (financialData: AdminDashboardData['financial_snapshot']['data']) => {
    return financialData.map(item => ({
        date: item.date,
        revenue: parseFloat(item.total_revenue),
        expenses: parseFloat(item.total_expenses),
        netIncome: parseFloat(item.net_income)
    }));
};

const Overview = () => {
    const {dashboardData, status} = useAuth();

    if (status === 'authenticating' || !dashboardData) {
        return (
            <div className="flex items-center justify-center h-full">
                <Loader2 className="h-8 w-8 animate-spin"/>
            </div>
        );
    }

    if (!isAdminDashboard(dashboardData)) {
        return (
            <div className="p-4">
                <h1 className="text-2xl font-bold">Error</h1>
                <p>Invalid dashboard data type. Expected admin dashboard.</p>
            </div>
        );
    }

    const adminData = dashboardData;
    const financialChartData = prepareFinancialChartData(adminData.financial_snapshot.data);


    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-6">Dashboard Overview</h1>

            {/* Stats Grid - Booking Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <StatCard
                    title="Active Bookings"
                    value={adminData.booking_statistics.active_bookings}
                    icon={<Laptop className="h-6 w-6"/>}
                    color="#0066FF"
                />
                <StatCard
                    title="Pending Bookings"
                    value={adminData.booking_statistics.pending_bookings}
                    icon={<Clock className="h-6 w-6"/>}
                    color="#FFC107"
                />
                <StatCard
                    title="Completed Bookings"
                    value={adminData.booking_statistics.completed_bookings}
                    icon={<Calendar className="h-6 w-6"/>}
                    color="#28A745"
                />
                <StatCard
                    title="Inventory Alerts"
                    value={adminData.inventory_alerts.total_count}
                    icon={<AlertTriangle className="h-6 w-6"/>}
                    color="#DC3545"
                    subtitle="Items low in stock"
                />
            </div>

            {/* Charts and Additional Info */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                {/* Financial Chart - Spans 2 columns */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Financial Overview (Last 7 Days)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={financialChartData}>
                                    <CartesianGrid strokeDasharray="3 3"/>
                                    <XAxis dataKey="date"/>
                                    <YAxis/>
                                    <Tooltip formatter={(value) => [`$${value}`, '']}/>
                                    <Line
                                        type="monotone"
                                        dataKey="revenue"
                                        name="Revenue"
                                        stroke="#28A745"
                                        strokeWidth={2}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="expenses"
                                        name="Expenses"
                                        stroke="#DC3545"
                                        strokeWidth={2}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="netIncome"
                                        name="Net Income"
                                        stroke="#0066FF"
                                        strokeWidth={2}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="grid grid-cols-3 gap-4 mt-4">
                            <div>
                                <p className="text-gray-500 text-xs">Revenue</p>
                                <p className="text-lg font-semibold text-green-600">
                                    ${adminData.financial_snapshot.summary.total_revenue}
                                </p>
                            </div>
                            <div>
                                <p className="text-gray-500 text-xs">Expenses</p>
                                <p className="text-lg font-semibold text-red-600">
                                    ${adminData.financial_snapshot.summary.total_expenses}
                                </p>
                            </div>
                            <div>
                                <p className="text-gray-500 text-xs">Net Income</p>
                                <p className="text-lg font-semibold text-blue-600">
                                    ${adminData.financial_snapshot.summary.net_revenue}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Inventory Alerts */}
                <Card className="h-full">
                    <CardHeader>
                        <CardTitle>Inventory Alerts</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {adminData.inventory_alerts.total_count === 0 ? (
                            <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-md">
                                <Package className="h-12 w-12 text-gray-400 mb-2"/>
                                <p className="text-gray-500">No inventory alerts</p>
                            </div>
                        ) : (
                            <div className="space-y-4 max-h-64 overflow-auto">
                                {adminData.inventory_alerts.items.map((item) => (
                                    <div key={item.id}
                                         className="flex items-center justify-between p-3 bg-red-50 rounded-md">
                                        <div>
                                            <h3 className="font-medium">{item.name}</h3>
                                            <p className="text-sm text-gray-500">{item.model}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-red-600 font-bold">{item.quantity} left</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Bottom Grid: Recent Activities & Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Activities */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Recent Activities</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {adminData.recent_activities.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-32 bg-gray-50 rounded-md">
                                <AlertCircle className="h-12 w-12 text-gray-400 mb-2"/>
                                <p className="text-gray-500">No recent activities</p>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="min-w-full">
                                    <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job
                                            Card
                                        </th>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service</th>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                    </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                    {adminData.recent_activities.slice(0, 5).map((activity) => (
                                        <tr key={activity.id}>
                                            <td className="px-4 py-2 whitespace-nowrap">{activity.job_card_number}</td>
                                            <td className="px-4 py-2 whitespace-nowrap">{activity.detailed_service.service_name}</td>
                                            <td className="px-4 py-2 whitespace-nowrap">
                                                    <span
                                                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                            activity.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                                activity.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                                                    activity.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                                                        'bg-gray-100 text-gray-800'
                                                        }`}>
                                                        {activity.status}
                                                    </span>
                                            </td>
                                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                                {new Date(activity.created_at).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card>
                    <CardHeader>
                        <CardTitle>Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                            <QuickActionButton
                                icon={<Calendar/>}
                                label="New Booking"
                                onClick={() => window.location.href = '/admin/bookings/new'}/>
                            <QuickActionButton
                                icon={<Package/>}
                                label="Add Inventory"
                                onClick={() => window.location.href = '/admin/inventory/new'}/>
                            <QuickActionButton
                                icon={<DollarSign/>}
                                label="Finances"
                                onClick={() => window.location.href = '/admin/finances'}/>
                            <QuickActionButton
                                icon={<ExternalLink/>}
                                label="Reports"
                                onClick={() => window.location.href = '/admin/reports'}/>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Overview;