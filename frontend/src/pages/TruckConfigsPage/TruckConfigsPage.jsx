import { Truck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export default function TruckConfigsPage() {
    return (
        <div className="container mx-auto max-w-6xl space-y-6">
            <div className="flex items-center gap-4">
                <div className="p-3 bg-muted rounded-full">
                    <Truck className="h-6 w-6" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Truck Configurations</h1>
                    <p className="text-muted-foreground">Manage your fleet dimensions and weight limits.</p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Standard Fleet</CardTitle>
                    <CardDescription>Default trailers available for calculation.</CardDescription>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground italic">Configuration module coming soon...</p>
                </CardContent>
            </Card>
        </div>
    );
}
