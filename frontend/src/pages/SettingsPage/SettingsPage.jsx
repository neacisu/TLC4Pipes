import { Settings } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export default function SettingsPage() {
    return (
        <div className="container mx-auto max-w-6xl space-y-6">
            <div className="flex items-center gap-4">
                <div className="p-3 bg-muted rounded-full">
                    <Settings className="h-6 w-6" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">System Settings</h1>
                    <p className="text-muted-foreground">Configure global parameters and user preferences.</p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Application Defaults</CardTitle>
                    <CardDescription>Global calculation parameters.</CardDescription>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground italic">Settings module coming soon...</p>
                </CardContent>
            </Card>
        </div>
    );
}
