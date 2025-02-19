import type React from "react"
import {Tabs, TabsContent, TabsList, TabsTrigger} from "@/components/ui/tabs"
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"

const InventoryView: React.FC = () => {
    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Inventory Information</CardTitle>
            </CardHeader>
            <CardContent>
                <Tabs defaultValue="devices">
                    <TabsList>
                        <TabsTrigger value="devices">Devices in Store</TabsTrigger>
                        <TabsTrigger value="parts">Device Parts Inventory</TabsTrigger>
                    </TabsList>
                    <TabsContent value="devices">
                        <DevicesInStore/>
                    </TabsContent>
                    <TabsContent value="parts">
                        <DeviceParts/>
                    </TabsContent>
                </Tabs>
            </CardContent>
        </Card>
    )
}

const DevicesInStore: React.FC = () => (
    <div>
        <h3 className="text-lg font-semibold mb-2">Devices in Store</h3>
        <table className="w-full">
            <thead>
            <tr>
                <th className="text-left">Device</th>
                <th className="text-left">Owner</th>
                <th className="text-left">Status</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Dell XPS 15</td>
                <td>Customer Owned</td>
                <td>In Repair</td>
            </tr>
            <tr>
                <td>HP Spectre x360</td>
                <td>Shop Owned</td>
                <td>Available</td>
            </tr>
            <tr>
                <td>MacBook Pro 13&#34;</td>
                <td>Customer Owned</td>
                <td>Ready for Pickup</td>
            </tr>
            </tbody>
        </table>
    </div>
)

const DeviceParts: React.FC = () => (
    <div>
        <h3 className="text-lg font-semibold mb-2">Device Parts Inventory</h3>
        <table className="w-full">
            <thead>
            <tr>
                <th className="text-left">Part</th>
                <th className="text-left">Compatibility</th>
                <th className="text-left">Quantity</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>15.6&#34; LCD Screen</td>
                <td>Dell, HP</td>
                <td>10</td>
            </tr>
            <tr>
                <td>512GB SSD</td>
                <td>Universal</td>
                <td>25</td>
            </tr>
            <tr>
                <td>8GB RAM DDR4</td>
                <td>Universal</td>
                <td>50</td>
            </tr>
            </tbody>
        </table>
    </div>
)

export default InventoryView