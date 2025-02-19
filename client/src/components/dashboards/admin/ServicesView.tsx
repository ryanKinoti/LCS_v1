import type React from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const ServicesView: React.FC = () => {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Shop Services</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="categories">
          <TabsList>
            <TabsTrigger value="categories">Service Categories</TabsTrigger>
            <TabsTrigger value="list">Service List</TabsTrigger>
            <TabsTrigger value="detailed">Detailed Services</TabsTrigger>
          </TabsList>
          <TabsContent value="categories">
            <ServiceCategories />
          </TabsContent>
          <TabsContent value="list">
            <ServiceList />
          </TabsContent>
          <TabsContent value="detailed">
            <DetailedServices />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

const ServiceCategories: React.FC = () => (
  <div>
    <h3 className="text-lg font-semibold mb-2">Service Categories</h3>
    <ul className="list-disc pl-5">
      <li>Hardware Repair</li>
      <li>Software Installation</li>
      <li>Data Recovery</li>
      <li>Upgrades</li>
    </ul>
  </div>
)

const ServiceList: React.FC = () => (
  <div>
    <h3 className="text-lg font-semibold mb-2">Service List</h3>
    <ul className="list-disc pl-5">
      <li>Screen Replacement</li>
      <li>Battery Replacement</li>
      <li>OS Installation</li>
      <li>Virus Removal</li>
      <li>Data Backup</li>
    </ul>
  </div>
)

const DetailedServices: React.FC = () => (
  <div>
    <h3 className="text-lg font-semibold mb-2">Detailed Services</h3>
    <table className="w-full">
      <thead>
        <tr>
          <th className="text-left">Service</th>
          <th className="text-left">Description</th>
          <th className="text-left">Price</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Screen Replacement</td>
          <td>Replace damaged or cracked laptop screens</td>
          <td>$150 - $300</td>
        </tr>
        <tr>
          <td>Battery Replacement</td>
          <td>Replace old or non-functioning laptop batteries</td>
          <td>$50 - $150</td>
        </tr>
        <tr>
          <td>OS Installation</td>
          <td>Install or reinstall operating systems</td>
          <td>$50 - $100</td>
        </tr>
      </tbody>
    </table>
  </div>
)

export default ServicesView

