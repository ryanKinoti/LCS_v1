import type React from "react"
import {useState} from "react"
import {Tabs, TabsContent, TabsList, TabsTrigger} from "@/components/ui/tabs"
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"

const UsersView: React.FC = () => {
    const [users] = useState([
        {id: 1, name: "John Doe", email: "john@example.com", role: "Customer"},
        {id: 2, name: "Jane Smith", email: "jane@example.com", role: "Staff"},
    ])

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Laptop-Care Users</CardTitle>
            </CardHeader>
            <CardContent>
                <Tabs defaultValue="all">
                    <TabsList>
                        <TabsTrigger value="all">All Users</TabsTrigger>
                        <TabsTrigger value="customers">Customers</TabsTrigger>
                        <TabsTrigger value="staff">Staff</TabsTrigger>
                    </TabsList>
                    <TabsContent value="all">
                        <UserTable users={users}/>
                    </TabsContent>
                    <TabsContent value="customers">
                        <UserTable users={users.filter((user) => user.role === "Customer")}/>
                    </TabsContent>
                    <TabsContent value="staff">
                        <UserTable users={users.filter((user) => user.role === "Staff")}/>
                    </TabsContent>
                </Tabs>
            </CardContent>
        </Card>
    )
}

const UserTable: React.FC<{ users: any[] }> = ({users}) => (
    <table className="w-full">
        <thead>
        <tr>
            <th className="text-left">Name</th>
            <th className="text-left">Email</th>
            <th className="text-left">Role</th>
        </tr>
        </thead>
        <tbody>
        {users.map((user) => (
            <tr key={user.id}>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
            </tr>
        ))}
        </tbody>
    </table>
)

export default UsersView

