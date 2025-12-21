"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, AlertTriangle, Package } from "lucide-react";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { cn } from "@/lib/utils";

interface TrendData {
    date: string;
    total_wafers: number;
    defective_wafers: number;
    pass_wafers: number;
    yield_rate: number;
}

interface EquipmentData {
    tool_id: string;
    total_wafers: number;
    defective_wafers: number;
    defect_rate: number;
    defect_breakdown: Record<string, number>;
}

export default function AnalyticsPage() {
    const [trends, setTrends] = useState<TrendData[]>([]);
    const [equipmentData, setEquipmentData] = useState<EquipmentData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAnalyticsData();
    }, []);

    const fetchAnalyticsData = async () => {
        try {
            const trendsRes = await fetch("http://localhost:8000/api/trends");
            const trendsJson = await trendsRes.json();
            setTrends(trendsJson.trends || []);

            const equipRes = await fetch("http://localhost:8000/api/equipment-correlation");
            const equipJson = await equipRes.json();
            setEquipmentData(equipJson.equipment_data || []);
        } catch (error) {
            console.error("Failed to fetch analytics:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
            </div>
        );
    }

    return (
        <>
            <AppSidebar showBackButton={true} currentPage="analytics" />
            <div className={cn("transition-all duration-300", "ml-64")}>
                <div className="container mx-auto p-8">
                    <div className="mb-8">
                        <h1 className="text-4xl font-bold mb-2">Analytics Dashboard</h1>
                        <p className="text-muted-foreground">Histor ical trends and equipment performance insights</p>
                    </div>

                    {/* Summary Cards */}
                    <div className="grid md:grid-cols-3 gap-4 mb-8">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Analyzed</CardTitle>
                                <Package className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {trends.reduce((sum, t) => sum + t.total_wafers, 0)}
                                </div>
                                <p className="text-xs text-muted-foreground">Last 30 days</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Avg Yield Rate</CardTitle>
                                <TrendingUp className="h-4 w-4 text-green-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-green-500">
                                    {trends.length > 0
                                        ? (trends.reduce((sum, t) => sum + t.yield_rate, 0) / trends.length).toFixed(1)
                                        : 0}
                                    %
                                </div>
                                <p className="text-xs text-muted-foreground">Across all tools</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Worst Tool</CardTitle>
                                <AlertTriangle className="h-4 w-4 text-destructive" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-destructive">
                                    {equipmentData.length > 0 ? equipmentData[0].tool_id : "N/A"}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    {equipmentData.length > 0 ? `${equipmentData[0].defect_rate}% defect rate` : "No data"}
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Trend Chart */}
                    <Card className="mb-8">
                        <CardHeader>
                            <CardTitle>Historical Yield Trend</CardTitle>
                            <CardDescription>Daily yield rates over the last 30 days</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={350}>
                                <LineChart data={trends}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis yAxisId="left" />
                                    <YAxis yAxisId="right" orientation="right" />
                                    <Tooltip />
                                    <Legend />
                                    <Line yAxisId="left" type="monotone" dataKey="yield_rate" stroke="#00d4ff" strokeWidth={2} name="Yield Rate (%)" />
                                    <Line yAxisId="right" type="monotone" dataKey="total_wafers" stroke="#8884d8" strokeWidth={2} name="Total Wafers" />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Equipment Correlation */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Equipment Defect Correlation</CardTitle>
                            <CardDescription>Defect rates by tool (sorted by severity)</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={400}>
                                <BarChart data={equipmentData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="tool_id" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="defect_rate" fill="#ff0055" name="Defect Rate (%)" />
                                    <Bar dataKey="total_wafers" fill="#00d4ff" name="Total Wafers" />
                                </BarChart>
                            </ResponsiveContainer>

                            <div className="mt-6 space-y-3">
                                {equipmentData.slice(0, 5).map((tool) => (
                                    <div key={tool.tool_id} className="p-4 border rounded-lg">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="font-semibold">{tool.tool_id}</span>
                                            <span className="text-sm text-muted-foreground">
                                                {tool.defectivewafers}/{tool.total_wafers} defective
                                            </span>
                                        </div>
                                        <div className="text-sm text-muted-foreground">
                                            Top defects: {Object.entries(tool.defect_breakdown)
                                                .sort(([, a], [, b]) => b - a)
                                                .slice(0, 3)
                                                .map(([pattern, count]) => `${pattern} (${count})`)
                                                .join(", ")}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </>
    );
}
