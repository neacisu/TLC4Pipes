import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, MoreHorizontal, FileText, Trash2, Truck } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

import { orderService } from "@/services/orderService";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";

export default function DashboardPage() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            const { orders: fetched = [] } = await orderService.listOrders({
                status: "draft,processing,calculated,cancelled",
            });
            // Sort by creation date desc (fallback to id desc)
            const sorted = [...fetched].sort((a, b) => {
                const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
                const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
                if (aTime === bTime) {
                    return (b.id || 0) - (a.id || 0);
                }
                return bTime - aTime;
            });
            setOrders(sorted);
        } catch (error) {
            console.error("Failed to fetch orders:", error);
            toast.error("Failed to load orders history");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Are you sure you want to delete this order?")) return;

        try {
            await orderService.deleteOrder(id);
            toast.success("Order deleted");
            fetchOrders(); // Refresh list
        } catch (error) {
            console.error("Delete failed:", error);
            toast.error("Failed to delete order");
        }
    };

    const getStatusBadge = (status) => {
        const variants = {
            draft: "secondary",
            processing: "default",
            calculated: "default", // or a specific color if available
            completed: "default", // we can customize colors later
            cancelled: "destructive"
        };
        const labels = {
            draft: "Draft",
            processing: "Procesare",
            calculated: "Procesat",
            completed: "Finalizat",
            cancelled: "Anulat",
        };
        return <Badge variant={variants[status] || "outline"}>{labels[status] || status}</Badge>;
    };

    return (
        <div className="space-y-6 container mx-auto max-w-7xl px-4 py-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                    <p className="text-muted-foreground">Manage your loading orders and history.</p>
                </div>
                <Link to="/orders/new">
                    <Button>
                        <Plus className="mr-2 h-4 w-4" /> New Order
                    </Button>
                </Link>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Orders History</CardTitle>
                    <CardDescription>
                        A list of all your created orders ({orders.length}).
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="text-center py-8 text-muted-foreground">Loading orders...</div>
                    ) : orders.length === 0 ? (
                        <div className="text-center py-12 border rounded-lg border-dashed bg-muted/20">
                            <h3 className="text-lg font-medium">No orders found</h3>
                            <p className="text-muted-foreground mb-4">Get started by creating your first loading plan.</p>
                            <Link to="/orders/new">
                                <Button variant="outline">Create Order</Button>
                            </Link>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-[100px]">Order #</TableHead>
                                    <TableHead>Created</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead className="text-right">Items</TableHead>
                                    <TableHead className="text-right">Total Weight</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {orders.map((order) => (
                                    <TableRow key={order.id}>
                                        <TableCell className="font-medium">{order.order_number}</TableCell>
                                        <TableCell>
                                            {order.created_at ? format(new Date(order.created_at), "PPP") : "N/A"}
                                        </TableCell>
                                        <TableCell>{getStatusBadge(order.status)}</TableCell>
                                        <TableCell className="text-right">{order.total_pipes || order.total_items || 0}</TableCell>
                                        <TableCell className="text-right">
                                            {order.total_weight_kg ? (order.total_weight_kg / 1000).toFixed(2) + " t" : "-"}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <DropdownMenu>
                                                <DropdownMenuTrigger asChild>
                                                    <Button variant="ghost" className="h-8 w-8 p-0">
                                                        <span className="sr-only">Open menu</span>
                                                        <MoreHorizontal className="h-4 w-4" />
                                                    </Button>
                                                </DropdownMenuTrigger>
                                                <DropdownMenuContent align="end">
                                                    <DropdownMenuItem onClick={() => navigate(`/orders/${order.id}/edit`)}>
                                                        <FileText className="mr-2 h-4 w-4" /> View / Edit
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem onClick={() => navigate(`/results?orderId=${order.id}`)} disabled={order.status === 'draft'}>
                                                        <Truck className="mr-2 h-4 w-4" /> View Loading Plan
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem className="text-red-600" onClick={() => handleDelete(order.id)}>
                                                        <Trash2 className="mr-2 h-4 w-4" /> Delete
                                                    </DropdownMenuItem>
                                                </DropdownMenuContent>
                                            </DropdownMenu>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
