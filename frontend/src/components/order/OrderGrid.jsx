import { useState, useEffect } from "react";
import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { pipeService } from "@/services/pipeService";

export default function OrderGrid({ items, onRemove, onAdd }) {
    const [availablePipes, setAvailablePipes] = useState([]);
    // Form state for new row
    const [selectedDn, setSelectedDn] = useState("");
    const [selectedPn, setSelectedPn] = useState("");
    const [quantity, setQuantity] = useState("1");
    const [loadingPipes, setLoadingPipes] = useState(false);

    // Load pipe catalog catalog
    useEffect(() => {
        const loadPipes = async () => {
            setLoadingPipes(true);
            try {
                const data = await pipeService.listPipes({ limit: 500 }); // Get all for now, optimize with search later
                setAvailablePipes(data);
            } catch (e) {
                console.error("Failed to load pipes", e);
            } finally {
                setLoadingPipes(false);
            }
        };
        loadPipes();
    }, []);

    // Filter logic
    const uniqueDns = [...new Set(availablePipes.map(p => p.dn_mm))].sort((a, b) => a - b);

    const availablePns = availablePipes
        .filter(p => !selectedDn || p.dn_mm === parseInt(selectedDn))
        .map(p => p.pn_class)
        .filter((v, i, a) => a.indexOf(v) === i); // unique

    const handleAddStart = () => {
        if (!selectedDn || !selectedPn || !quantity) return;

        // Find full pipe object
        const pipe = availablePipes.find(p => p.dn_mm === parseInt(selectedDn) && p.pn_class === selectedPn);
        if (!pipe) return;

        onAdd({
            pipeId: pipe.id,
            code: pipe.code,
            dn: pipe.dn_mm,
            pn: pipe.pn_class,
            quantity: parseInt(quantity)
        });

        // Reset simple fields
        setQuantity("1");
    };

    return (
        <div className="space-y-4">
            {/* Input Row */}
            <div className="grid grid-cols-4 gap-4 p-4 border rounded-lg bg-muted/30 items-end">
                <div className="space-y-2">
                    <span className="text-sm font-medium">Diameter (DN)</span>
                    <Select value={selectedDn} onValueChange={setSelectedDn}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select DN" />
                        </SelectTrigger>
                        <SelectContent>
                            {uniqueDns.map(dn => (
                                <SelectItem key={dn} value={dn.toString()}>{dn} mm</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2">
                    <span className="text-sm font-medium">Pressure Class</span>
                    <Select value={selectedPn} onValueChange={setSelectedPn} disabled={!selectedDn}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select PN" />
                        </SelectTrigger>
                        <SelectContent>
                            {availablePns.map(pn => (
                                <SelectItem key={pn} value={pn}>{pn}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2">
                    <span className="text-sm font-medium">Quantity</span>
                    <Input
                        type="number"
                        min="1"
                        value={quantity}
                        onChange={e => setQuantity(e.target.value)}
                    />
                </div>

                <Button onClick={handleAddStart} disabled={!selectedDn || !selectedPn}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Row
                </Button>
            </div>

            {/* Table */}
            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Pipe Code</TableHead>
                            <TableHead>Diameter (DN)</TableHead>
                            <TableHead>Class (PN)</TableHead>
                            <TableHead>Quantity</TableHead>
                            <TableHead className="w-[50px]"></TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {items.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                                    No items added. Add pipes manually or import CSV.
                                </TableCell>
                            </TableRow>
                        ) : (
                            items.map((item, idx) => (
                                <TableRow key={idx}>
                                    <TableCell className="font-medium">{item.code}</TableCell>
                                    <TableCell>{item.dn} mm</TableCell>
                                    <TableCell>{item.pn}</TableCell>
                                    <TableCell>{item.quantity}</TableCell>
                                    <TableCell>
                                        <Button variant="ghost" size="icon" onClick={() => onRemove(idx)}>
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
